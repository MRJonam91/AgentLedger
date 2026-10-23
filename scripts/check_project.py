# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproducible project checks, including a narrow publication-content scan."""

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md", "LICENSING.md", "ASSETS.md",
            "README.md", "README.it.md", "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md",
            "CODE_OF_CONDUCT.md", "CHANGELOG.md", "AGENTS.md", ".github/FUNDING.yml",
            "docs/ARCHITECTURE.md", "docs/THREAT_MODEL.md", "docs/EVENTS.md", "docs/ROADMAP.md",
            "docs/VERIFICATION.md", "docs/LAUNCH.md", ".github/workflows/ci.yml"]
PATTERNS = {
    "credential_pattern": re.compile(r"(?:sk-(?:proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{24,})"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    "personal_windows_path": re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+"),
    "personal_email": re.compile(r"[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")}


def scan_text(content):
    findings = set()
    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(content):
            value = match.group(0)
            if label == "personal_email":
                domain = value.rsplit("@", 1)[1].lower()
                if domain in {"users.noreply.github.com", "example.org", "example.com", "example.net"}:
                    continue
            findings.add(label)
    return sorted(findings)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def public_files():
    try:
        if Path(git("rev-parse", "--show-toplevel").decode().strip()).resolve() != ROOT:
            raise FileNotFoundError("source_archive_has_no_own_git_root")
        names = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")
        return sorted({ROOT / name for name in names if name and (ROOT / name).is_file()})
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Source archives have no Git metadata. Inspect only the distributed source tree.
        skip = {".git", ".venv", ".test-output", ".agentledger", "build", "dist", "__pycache__"}
        return sorted(p for p in ROOT.rglob("*") if p.is_file()
                      and not (set(p.relative_to(ROOT).parts) & skip)
                      and not any(part.endswith(".egg-info") for part in p.parts))


def check(history=False):
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append(name + ": missing")
    source = sorted((ROOT / "agentledger").glob("*.py"))
    core_lines = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in source)
    if core_lines >= 1500:
        errors.append("runtime_core: 1500 line limit exceeded")
    files = public_files()
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() not in {".py", ".md", ".toml", ".json", ".yml", ".svg", ".in", ".cfg"} and path.name not in {"LICENSE", "NOTICE", ".gitignore", ".gitattributes", "PKG-INFO"}:
            errors.append(name + ": unexpected public file type")
            continue
        content = path.read_text(encoding="utf-8")
        errors.extend(name + ": " + kind for kind in scan_text(content))
        if path.suffix == ".py":
            if not content.startswith("# SPDX-License-Identifier: GPL-3.0-or-later"):
                errors.append(name + ": missing SPDX")
            try:
                ast.parse(content, filename=name, feature_version=(3, 11))
            except SyntaxError:
                errors.append(name + ": incompatible Python syntax")
        if path.suffix == ".md":
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
                if re.match(r"https?://|#|mailto:", link):
                    continue
                target = link.split("#", 1)[0]
                if target and not (path.parent / target).exists():
                    errors.append(name + ": broken local link")
    funding = (ROOT / ".github/FUNDING.yml").read_text(encoding="utf-8")
    if not all(s in funding for s in ("MRJonam91", "ko_fi: mrjonam", "buy_me_a_coffee: mrjonam", "https://paypal.me/manorollo")):
        errors.append("funding: incomplete")
    commit_count = 0
    if history:
        commits = git("rev-list", "--all").decode().splitlines()
        commit_count = len(commits)
        for commit in commits:
            metadata = git("show", "-s", "--format=%an <%ae>%n%cn <%ce>%n%B", commit).decode("utf-8")
            errors.extend(commit + ": " + kind for kind in scan_text(metadata))
            names = git("ls-tree", "-r", "--name-only", "-z", commit).decode().split("\0")
            for name in filter(None, names):
                raw = git("show", commit + ":" + name)
                try:
                    content = raw.decode("utf-8")
                except UnicodeError:
                    errors.append(commit + ": nontext historical content")
                    continue
                errors.extend(commit + ":" + name + ": " + kind for kind in scan_text(content))
    return {"core_physical_lines": core_lines, "public_files": len(files),
            "reachable_commits_checked": commit_count, "errors": errors,
            "scan_scope": "Known credential, email and local-path patterns; not a security certification"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true")
    result = check(parser.parse_args().history)
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))
