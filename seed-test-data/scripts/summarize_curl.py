#!/usr/bin/env python3
"""Summarize curl command(s) into deduplicated API candidates for seed-test-data.

Read-only: does not call APIs or write to databases.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

LOGIN_RE = re.compile(r"/(login|auth|oauth|token|signin)(/|$)", re.I)
CANCEL_RE = re.compile(r"(cancel|void|checkout|check-?out|退|作废)", re.I)
URL_RE = re.compile(r"https?://[^\s'\"\\]+", re.I)


def fail(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


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


def auth_header_names(headers: dict[str, str]) -> list[str]:
    names: list[str] = []
    for key in headers:
        lk = key.lower()
        if lk in ("authorization", "token", "x-token", "x-auth-token", "x-access-token"):
            names.append(key)
        elif "token" in lk or lk.endswith("authorization"):
            names.append(key)
    return sorted(set(names))


def join_continuations(text: str) -> str:
    """Join lines ending with backslash; keep newlines otherwise for splitting commands."""
    lines = text.splitlines()
    out: list[str] = []
    buf = ""
    for line in lines:
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            buf += stripped[:-1] + " "
        else:
            buf += stripped
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return "\n".join(out)


def split_curl_commands(text: str) -> list[str]:
    joined = join_continuations(text)
    commands: list[str] = []
    current: list[str] = []
    for raw in joined.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # drop leading shell prompt
        if line.startswith("$ "):
            line = line[2:].strip()
        if line.startswith("curl ") or line == "curl" or line.startswith("curl\t"):
            if current:
                commands.append(" ".join(current))
            current = [line]
        elif current:
            # continuation without backslash already joined; treat as same cmd only if previous incomplete
            current.append(line)
        # else ignore non-curl lines
    if current:
        commands.append(" ".join(current))
    return commands


def _take_value(argv: list[str], i: int) -> tuple[str, int]:
    if i + 1 >= len(argv):
        fail(f"missing value after {argv[i]}")
    return argv[i + 1], i + 1


def parse_curl_command(cmd: str) -> dict[str, Any] | None:
    try:
        argv = shlex.split(cmd, posix=True)
    except ValueError as e:
        fail(f"cannot parse curl: {e}")

    if not argv or argv[0] != "curl":
        return None

    method: str | None = None
    url: str | None = None
    headers: dict[str, str] = {}
    body_parts: list[str] = []
    used_json_flag = False

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in ("-X", "--request"):
            val, i = _take_value(argv, i)
            method = val.upper()
        elif arg in ("-H", "--header"):
            val, i = _take_value(argv, i)
            if ":" in val:
                name, value = val.split(":", 1)
                headers[name.strip()] = value.strip()
        elif arg in ("-d", "--data", "--data-raw", "--data-binary", "--data-ascii"):
            val, i = _take_value(argv, i)
            body_parts.append(val)
        elif arg == "--json":
            val, i = _take_value(argv, i)
            body_parts.append(val)
            used_json_flag = True
            if "content-type" not in {k.lower() for k in headers}:
                headers["Content-Type"] = "application/json"
        elif arg in ("-u", "--user", "-A", "--user-agent", "-b", "--cookie", "-e", "--referer",
                     "--connect-timeout", "--max-time", "-o", "--output", "-w", "--write-out",
                     "--cert", "--key", "--cacert", "--proxy"):
            _, i = _take_value(argv, i)
        elif arg.startswith("-") and "=" in arg and not arg.startswith("--data"):
            # e.g. --request=POST
            key, _, val = arg.partition("=")
            if key in ("-X", "--request"):
                method = val.upper()
        elif arg.startswith("-"):
            # boolean flags: -s -k -L -v -g etc.
            pass
        else:
            if arg.startswith("http://") or arg.startswith("https://"):
                url = arg
            elif url is None and URL_RE.match(arg):
                url = arg
        i += 1

    if url is None:
        m = URL_RE.search(cmd)
        if m:
            url = m.group(0)

    if not url:
        return None

    body = body_parts[-1] if body_parts else None
    has_body = bool(body)
    if method is None:
        method = "POST" if has_body else "GET"

    parsed = urlparse(url)
    path_only = parsed.path or "/"
    ctype = ""
    for k, v in headers.items():
        if k.lower() == "content-type":
            ctype = v.split(";")[0].strip()
            break
    if not ctype and used_json_flag:
        ctype = "application/json"

    return {
        "method": method.upper(),
        "path": path_only,
        "host": parsed.netloc,
        "purpose": guess_purpose(method, path_only, has_body),
        "contentType": ctype,
        "authHeaders": auth_header_names(headers),
        "bodyFieldCount": json_field_count(body),
        "hasBody": has_body,
        "responseIdHints": [],
        "status": None,
        "order": 0,
    }


def summarize(text: str, source: str) -> dict[str, Any]:
    commands = split_curl_commands(text)
    if not commands:
        fail("no curl commands found")

    best: dict[str, dict[str, Any]] = {}
    order = 0
    for cmd in commands:
        cand = parse_curl_command(cmd)
        if cand is None:
            continue
        order += 1
        cand["order"] = order
        key = f"{cand['method']} {cand['path']}"
        score = cand["bodyFieldCount"] * 10 + (2 if cand["hasBody"] else 0)
        prev = best.get(key)
        if prev is None or score > prev.get("_score", 0) or (
            score == prev.get("_score", 0) and order > prev.get("order", 0)
        ):
            cand["_score"] = score
            best[key] = cand

    if not best:
        fail("no parseable curl URLs found")

    purpose_rank = {"login": 0, "create": 1, "get": 2, "delete": 3, "other": 4}
    candidates = []
    for c in best.values():
        c.pop("_score", None)
        candidates.append(c)
    candidates.sort(key=lambda x: (purpose_rank.get(x["purpose"], 9), x["order"], x["path"]))

    return {
        "file": source,
        "commandCount": len(commands),
        "candidateCount": len(candidates),
        "candidates": candidates,
    }


def read_input(path: str) -> tuple[str, str]:
    if path == "-":
        return sys.stdin.read(), "<stdin>"
    p = Path(path)
    if not p.is_file():
        fail(f"not found: {path}")
    return p.read_text(encoding="utf-8"), str(p)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize curl commands into seed API candidates")
    parser.add_argument("source", help="Path to .sh/.curl/.txt, or - for stdin")
    parser.add_argument("--text", action="store_true", help="Print short text list instead of JSON")
    args = parser.parse_args()

    text, label = read_input(args.source)
    summary = summarize(text, label)

    if args.text:
        print(f"source={summary['file']} commands={summary['commandCount']} candidates={summary['candidateCount']}")
        for i, c in enumerate(summary["candidates"], 1):
            auth = ",".join(c["authHeaders"]) or "-"
            print(
                f"{i}. [{c['purpose']}] {c['method']} {c['path']} "
                f"bodyFields={c['bodyFieldCount']} auth={auth}"
            )
    else:
        json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
