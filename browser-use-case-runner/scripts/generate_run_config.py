#!/usr/bin/env python3
"""Generate a per-run JSON config under reports/ from exported cases JSONL + optional source path."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def _load_cases(jsonl_path: Path) -> list[dict]:
    cases: list[dict] = []
    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
    return cases


def _infer_login_suite(cases: list[dict], source_hint: str) -> bool:
    hint = source_hint.lower()
    if "登录" in source_hint or "login" in hint:
        return True
    if not cases:
        return False

    def is_login_row(c: dict) -> bool:
        cid = str(c.get("id", "")).upper()
        mod = str(c.get("module", ""))
        name = str(c.get("name", ""))
        pre = str(c.get("preconditions", ""))
        steps = str(c.get("steps", ""))
        if cid.startswith("TC-LOGIN") or "LOGIN" in cid:
            return True
        blob = mod + name + pre + steps
        return "登录" in blob or "login" in blob.lower()

    hits = sum(1 for c in cases if is_login_row(c))
    return hits >= max(1, len(cases) // 2) or (hits > 0 and len(cases) <= 3)


def main() -> None:
    p = argparse.ArgumentParser(description="Generate reports/run-config-<UTC>.json from cases JSONL.")
    p.add_argument("--jsonl", required=True, help="Path to cases JSONL (e.g. reports/cases-room.jsonl)")
    p.add_argument(
        "--source",
        default="",
        help="Original case source label for traceability (e.g. xlsx:test-data/房间管理-测试用例.xlsx)",
    )
    p.add_argument(
        "--defaults",
        default="",
        help="Optional path to default runner JSON (video outputDir/notes) to merge for outputDir",
    )
    p.add_argument("-o", "--output", default="", help="Write config to this path; default reports/run-config-<UTC>.json")
    args = p.parse_args()

    jsonl_path = Path(args.jsonl)
    if not jsonl_path.is_file():
        raise SystemExit(f"JSONL not found: {jsonl_path}")

    cases = _load_cases(jsonl_path)
    source_hint = args.source or str(jsonl_path)
    is_login = _infer_login_suite(cases, source_hint)
    session = "fresh-per-case" if is_login else "single-session"

    defaults: dict = {}
    if args.defaults:
        dp = Path(args.defaults)
        if dp.is_file():
            defaults = json.loads(dp.read_text(encoding="utf-8"))

    vr = defaults.get("videoRecording") if isinstance(defaults.get("videoRecording"), dict) else {}
    video_block = {
        "enabled": False,
        "outputDir": str(vr.get("outputDir") or "reports/recordings"),
        "notes": str(
            vr.get("notes")
            or "Default: enabled=false (方式1); use browser-use screenshot + report paths. When true: user asked for full-screen external capture (ffmpeg/OBS); not viewport-native; browser-use CLI has no built-in record command."
        ),
    }

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = Path(args.output) if args.output else Path("reports") / f"run-config-{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = {
        "schema": "browser-use-case-runner/run-config/1",
        "generatedAtUtc": ts,
        "casesJsonl": str(jsonl_path.as_posix()),
        "casesSource": args.source or str(jsonl_path),
        "caseCount": len(cases),
        "inferredSuiteKind": "login" if is_login else "other",
        "sessionStrategy": session,
        "sessionStrategyRationale": (
            "推断为登录类用例集：默认每条用例前 close --all 再起 headed open，避免表单/会话串扰。"
            if is_login
            else "推断为非登录主流程：默认单会话连续执行直至遇阻，减少重复登录与验证码。"
        ),
        "videoRecording": video_block,
        "userOverrides": {
            "videoRecordingConfirmed": False,
            "sessionStrategyConfirmed": False,
            "notes": "由 Agent 询问用户后可将 videoRecording.enabled / sessionStrategy 更新为本文件，并把 *_Confirmed 置为 true。",
        },
    }

    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path.resolve())


if __name__ == "__main__":
    main()
