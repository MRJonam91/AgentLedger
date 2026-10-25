# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline process and HTTP integration checks; no paid provider traffic."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from agentledger.provider import MAX_RESPONSE_BYTES, request_response
from test_domain import response

ROOT = Path(__file__).resolve().parents[1]


class LocalTransportTests(unittest.TestCase):
    def exercise(self, payload, status=200):
        calls = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                calls.append({"body": json.loads(body), "path": self.path})
                self.send_response(status)
                if status == 307:
                    self.send_header("Location", "/redirected")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        url = f"http://127.0.0.1:{server.server_port}/v1/responses"
        def local_request(original, **kwargs):
            self.assertEqual(original, "https://api.openai.com/v1/responses")
            return Request(url, **kwargs)
        try:
            with patch("agentledger.provider.Request", side_effect=local_request), \
                 patch("agentledger.provider.build_opener",
                       side_effect=lambda *handlers: build_opener(ProxyHandler({}), *handlers)):
                result = request_response("synthetic-local-key", "demo-model", "synthetic prompt", 512)
            return result, calls
        finally:
            self.calls = calls
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)

    def test_actual_http_request_and_usage_decode(self):
        result, calls = self.exercise(json.dumps(response()).encode("utf-8"))
        self.assertEqual(result["usage"]["input_tokens"], 1000)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["body"], {"model": "demo-model", "input": "synthetic prompt",
                                         "max_output_tokens": 512, "store": False, "tools": []})

    def test_redirect_is_not_followed(self):
        with self.assertRaises(HTTPError) as error:
            self.exercise(b"", status=307)
        self.assertEqual(error.exception.code, 307)
        self.assertEqual(len(self.calls), 1)

    def test_invalid_provider_json_fails_without_retry(self):
        with self.assertRaisesRegex(ValueError, "invalid_json"):
            self.exercise(b'{"usage":{},"usage":{}}')
        self.assertEqual(len(self.calls), 1)

    def test_oversized_provider_response_fails_without_retry(self):
        with self.assertRaisesRegex(ValueError, "response_too_large"):
            self.exercise(b" " * (MAX_RESPONSE_BYTES + 1))
        self.assertEqual(len(self.calls), 1)


class ConcurrentProcessTests(unittest.TestCase):
    def test_new_database_and_batch_dedupe_across_processes(self):
        with tempfile.TemporaryDirectory() as temporary:
            db = Path(temporary) / "ledger.sqlite3"
            command = [sys.executable, "-m", "agentledger", "--db", str(db),
                       "import-jsonl", str(ROOT / "examples/responses.jsonl")]
            processes = [subprocess.Popen(command, cwd=ROOT, env=dict(os.environ, OPENAI_API_KEY=""),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
                         for _ in range(3)]
            results = []
            try:
                for process in processes:
                    out, err = process.communicate(timeout=30)
                    results.append((process.returncode, out, err))
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.kill()
                        process.communicate()
            self.assertEqual(sorted(r[0] for r in results), [0, 2, 2], results)
            for code, out, err in results:
                if code == 2:
                    self.assertEqual(json.loads(err)["error"], "duplicate_response")
            report = subprocess.run([sys.executable, "-m", "agentledger", "--db", str(db),
                                     "report", "--summary"], cwd=ROOT, capture_output=True,
                                    text=True, encoding="utf-8", check=True, timeout=15)
            self.assertEqual(json.loads(report.stdout)["event_count"], 2)


if __name__ == "__main__":
    unittest.main()
