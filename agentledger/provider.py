# SPDX-License-Identifier: GPL-3.0-or-later
"""Single bounded HTTPS request, no content persistence and no retries."""

import json
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_response(api_key, model, prompt, max_output_tokens):
    body = json.dumps({"model": model, "input": prompt,
                       "max_output_tokens": max_output_tokens, "store": False,
                       "tools": []}).encode("utf-8")
    request = Request("https://api.openai.com/v1/responses", data=body,
                      headers={"Authorization": "Bearer " + api_key,
                               "Content-Type": "application/json"}, method="POST")
    with build_opener(NoRedirect()).open(request, timeout=60) as reply:
        content = reply.read(MAX_RESPONSE_BYTES + 1)
    if len(content) > MAX_RESPONSE_BYTES:
        raise ValueError("response_too_large")
    return json.loads(content)
