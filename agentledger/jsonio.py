# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded strict JSON inputs and create-only local output files."""

import json
import math
import os
from pathlib import Path

from .domain import canonical

MAX_OBJECT = 2 * 1024 * 1024
MAX_BATCH = 16 * 1024 * 1024
MAX_RECORDS = 1000


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("invalid_json")
        value[key] = item
    return value


def reject_constant(value):
    raise ValueError("invalid_json")


def decode_object(raw):
    if not isinstance(raw, bytes):
        raise ValueError("invalid_json")
    if len(raw) > MAX_OBJECT:
        raise ValueError("input_too_large")
    try:
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object,
                           parse_constant=reject_constant)
        if not isinstance(value, dict):
            raise ValueError()
        stack = [(value, 0)]
        while stack:
            item, depth = stack.pop()
            if depth > 64 or (isinstance(item, float) and not math.isfinite(item)):
                raise ValueError()
            if isinstance(item, str):
                item.encode("utf-8")
            if isinstance(item, dict):
                for key in item:
                    key.encode("utf-8")
            if isinstance(item, (dict, list)):
                children = item.values() if isinstance(item, dict) else item
                stack.extend((child, depth + 1) for child in children)
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise ValueError("invalid_json") from None


def read_object(path):
    with Path(path).open("rb") as stream:
        return decode_object(stream.read(MAX_OBJECT + 1))


def read_jsonl(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BATCH + 1)
    if len(raw) > MAX_BATCH:
        raise ValueError("input_too_large")
    try:
        lines = raw.decode("utf-8-sig").split("\n")
    except UnicodeError:
        raise ValueError("invalid_json") from None
    records: list[dict] = []
    for line in lines:
        if line.strip():
            if len(records) == MAX_RECORDS:
                raise ValueError("invalid_batch")
            records.append(decode_object(line.encode("utf-8")))
    if not records:
        raise ValueError("invalid_batch")
    return records


def create_output(path):
    try:
        return os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("output_exists") from None


def write_new_object(path, value):
    content = (canonical(value) + "\n").encode("utf-8")
    write_new_bytes(path, content)


def write_new_bytes(path, content):
    if not isinstance(content, bytes):
        raise ValueError("invalid_input")
    fd = create_output(path)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        Path(path).unlink(missing_ok=True)
        raise
