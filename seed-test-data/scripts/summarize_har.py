#!/usr/bin/env python3
"""Summarize a HAR file into deduplicated API candidates for seed-test-data.

Read-only: does not call APIs or write to databases.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

STATIC_EXT = (
    ".js",
    ".css",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".map",
    ".ico",
    ".webp",
)
STATIC_MIME_HINTS = (
    "javascript",
    "text/css",
    "image/",
    "font/",
    "octet-stream",
)
HEALTH_RE = re.compile(r"/(health|ping|ready|live|actuator)(/|$)", re.I)
LOGIN_RE = re.compile(r"/(login|auth|oauth|token|signin)(/|$)", re.I)
CANCEL_RE = re.compile(r"(cancel|void|checkout|check-?out|退|作废)", re.I)


def fail(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def header_map(headers: list[dict[str, Any]] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for h in headers or []:
        name = (h.get("name") or "").strip()
        if not name:
            continue
        out[name.lower()] = str(h.get("value") or "")
    return out


def content_type(headers: dict[str, str], post_mime: str | None = None) -> str:
    return headers.get("content-type") or post_mime or ""


def auth_header_names(headers: dict[str, str]) -> list[str]:
    names: list[str] = []
    for key in headers:
        lk = key.lower()
        if lk in ("authorization", "token", "x-token", "x-auth-token", "x-access-token"):
            names.append(key)
        elif "token" in lk or lk.endswith("authorization"):
            names.append(key)
    return sorted(set(names))


def is_static(url: str, mime: str) -> bool:
    path = urlparse(url).path.lower()
    if any(path.endswith(ext) for ext in STATIC_EXT):
        return True
    ml = (mime or "").lower()
    return any(h in ml for h in STATIC_MIME_HINTS if h != "octet-stream")


def json_field_count(text: str | None) -> int:
    if not text:
        return 0
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return 0
    if isinstance(data, dict):
        return len(data)
    if isinstance(data, list):
        return len(data)
    return 1


def guess_purpose(method: str, path: str, has_body: bool) -> str:
    m = method.upper()
    if LOGIN_RE.search(path):
        return "login"
    if m == "DELETE" or CANCEL_RE.search(path):
        return "delete"
    if m in ("POST", "PUT", "PATCH") and has_body:
        return "create"
    if m == "GET":
        return "get"
    if m in ("POST", "PUT", "PATCH"):
        return "create"
    return "other"


def response_id_hints(text: str | None) -> list[str]:
    if not text:
        return []
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return []
    hints: list[str] = []

    def walk(obj: Any, prefix: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                path = f"{prefix}.{k}" if prefix else k
                if re.search(r"(^id$|Id$|_id$)", k) and not isinstance(v, (dict, list)):
                    hints.append(path)
                if isinstance(v, (dict, list)) and path.count(".") < 3:
                    walk(v, path)
        elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
            walk(obj[0], f"{prefix}[]" if prefix else "[]")

    walk(data, "")
    # prefer short common paths
    uniq = []
    for h in hints:
        if h not in uniq:
            uniq.append(h)
    return uniq[:8]


def load_har(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"not found: {path}")
    except json.JSONDecodeError as e:
        fail(f"invalid HAR JSON: {e}")
    return {}


def pick_default_host(entries: list[dict[str, Any]]) -> str | None:
    hosts: list[str] = []
    for e in entries:
        req = e.get("request") or {}
        url = req.get("url") or ""
        if not url:
            continue
        method = (req.get("method") or "").upper()
        if method == "OPTIONS":
            continue
        parsed = urlparse(url)
        mime = content_type(header_map(req.get("headers")), (req.get("postData") or {}).get("mimeType"))
        if is_static(url, mime):
            continue
        if parsed.netloc:
            hosts.append(parsed.netloc)
    if not hosts:
        return None
    return Counter(hosts).most_common(1)[0][0]


def summarize(path: Path, host: str | None) -> dict[str, Any]:
    har = load_har(path)
    entries = (har.get("log") or {}).get("entries") or []
    if not isinstance(entries, list):
        fail("HAR missing log.entries[]")

    default_host = pick_default_host(entries)
    filter_host = host or default_host

    # key -> candidate with score
    best: dict[str, dict[str, Any]] = {}

    for e in entries:
        req = e.get("request") or {}
        resp = e.get("response") or {}
        url = req.get("url") or ""
        method = (req.get("method") or "").upper()
        if not url or not method:
            continue
        if method == "OPTIONS":
            continue

        parsed = urlparse(url)
        path_only = parsed.path or "/"
        req_headers = header_map(req.get("headers"))
        post = req.get("postData") or {}
        mime = content_type(req_headers, post.get("mimeType"))
        if is_static(url, mime):
            continue
        if HEALTH_RE.search(path_only) and method == "GET":
            continue
        if filter_host and parsed.netloc and parsed.netloc != filter_host:
            continue

        body_text = post.get("text")
        body_fields = json_field_count(body_text)
        has_body = bool(body_text)
        resp_text = ((resp.get("content") or {}).get("text")) if isinstance(resp.get("content"), dict) else None
        purpose = guess_purpose(method, path_only, has_body)

        # keep write / get / delete / login; drop bare GET list noise later by purpose
        if purpose == "other" and method == "GET" and not re.search(r"/\d+(/|$)|\{", path_only):
            # keep GET only if looks like resource-by-id; lists still useful for validate — keep if path has api-ish segment
            if not re.search(r"/api/|/v\d+/", path_only):
                continue

        key = f"{method} {path_only}"
        score = body_fields * 10 + (2 if has_body else 0) + (1 if resp_text else 0)
        started = e.get("startedDateTime") or ""
        cand = {
            "method": method,
            "path": path_only,
            "host": parsed.netloc,
            "purpose": purpose,
            "contentType": mime.split(";")[0].strip() if mime else "",
            "authHeaders": auth_header_names(req_headers),
            "bodyFieldCount": body_fields,
            "hasBody": has_body,
            "responseIdHints": response_id_hints(resp_text),
            "status": resp.get("status"),
            "startedDateTime": started,
            "_score": score,
        }
        prev = best.get(key)
        if prev is None or score > prev["_score"] or (
            score == prev["_score"] and started > (prev.get("startedDateTime") or "")
        ):
            best[key] = cand

    candidates = []
    for c in best.values():
        c.pop("_score", None)
        candidates.append(c)

    order = {"login": 0, "create": 1, "get": 2, "delete": 3, "other": 4}
    candidates.sort(key=lambda x: (order.get(x["purpose"], 9), x["path"], x["method"]))

    return {
        "file": str(path),
        "entryCount": len(entries),
        "host": filter_host,
        "candidateCount": len(candidates),
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize HAR into seed API candidates")
    parser.add_argument("har", type=Path, help="Path to .har file")
    parser.add_argument("--host", default=None, help="Only keep this request host")
    parser.add_argument("--text", action="store_true", help="Print short text list instead of JSON")
    args = parser.parse_args()

    if not args.har.is_file():
        fail(f"not found: {args.har}")

    summary = summarize(args.har, args.host)
    if args.text:
        print(f"host={summary['host']} entries={summary['entryCount']} candidates={summary['candidateCount']}")
        for i, c in enumerate(summary["candidates"], 1):
            auth = ",".join(c["authHeaders"]) or "-"
            print(
                f"{i}. [{c['purpose']}] {c['method']} {c['path']} "
                f"bodyFields={c['bodyFieldCount']} auth={auth} status={c.get('status')}"
            )
    else:
        json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
