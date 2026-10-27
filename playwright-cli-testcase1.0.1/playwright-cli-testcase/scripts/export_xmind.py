#!/usr/bin/env python3
"""Export web test cases JSON to XMind (.xmind), Zen / 2020+ compatible."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
import zipfile
from collections import OrderedDict
from pathlib import Path
from xml.sax.saxutils import escape


def load_data(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "cases" not in data:
        raise ValueError("JSON 需包含 title（可选）与 cases 数组")
    if not isinstance(data["cases"], list):
        raise ValueError("cases 必须为数组")
    return data


def _clip(text: str, limit: int = 200) -> str:
    text = (text or "").strip().replace("\r\n", "\n")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _new_id() -> str:
    return uuid.uuid4().hex[:26]


def _topic(title: str, children: list[dict] | None = None, notes: str | None = None) -> dict:
    node: dict = {
        "id": _new_id(),
        "class": "topic",
        "title": title,
    }
    if notes:
        node["notes"] = {"plain": {"content": notes}}
    if children:
        node["children"] = {"attached": children}
    return node


def _build_sheet(data: dict) -> dict:
    title = (data.get("title") or "Web 测试用例").strip() or "Web 测试用例"
    cases = data["cases"]

    modules: "OrderedDict[str, list]" = OrderedDict()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("cases 中每一项必须为对象")
        module = (case.get("module") or "未分类").strip() or "未分类"
        modules.setdefault(module, []).append(case)

    root_children: list[dict] = []

    assumptions = (data.get("assumptions") or "").strip()
    if assumptions:
        root_children.append(_topic("假设说明", notes=assumptions))

    for module, module_cases in modules.items():
        case_topics: list[dict] = []
        for case in module_cases:
            priority = (case.get("priority") or "").strip()
            case_title = (case.get("title") or case.get("case_id") or "未命名用例").strip()
            case_id = (case.get("case_id") or "").strip()
            label = f"[{priority}] {case_title}" if priority else case_title
            if case_id:
                label = f"{case_id} {label}"

            pre = _clip(str(case.get("precondition") or ""))
            steps = _clip(str(case.get("steps") or ""), 400)
            expected = _clip(str(case.get("expected") or ""), 400)

            # 标题 → 前置 → 步骤 → 预期（逐级嵌套，缺层则挂到最近祖先）
            layers: list[dict] = []
            if pre:
                layers.append(_topic(f"前置: {pre}"))
            if steps:
                layers.append(_topic(f"步骤: {steps}"))
            if expected:
                layers.append(_topic(f"预期: {expected}"))

            nested: dict | None = None
            for node in reversed(layers):
                if nested is not None:
                    node["children"] = {"attached": [nested]}
                nested = node

            case_topics.append(_topic(label, [nested] if nested else None))

        root_children.append(_topic(module, case_topics))

    return {
        "id": _new_id(),
        "class": "sheet",
        "title": "测试用例",
        "rootTopic": _topic(title, root_children),
    }


def _content_xml(sheet: dict) -> str:
    """Legacy content.xml for broader compatibility alongside content.json."""

    def topics_xml(topics: list[dict]) -> str:
        if not topics:
            return ""
        parts = ['<children><topics type="attached">']
        for topic in topics:
            tid = escape(str(topic.get("id") or _new_id()))
            title = escape(str(topic.get("title") or ""))
            kids = topic.get("children", {}).get("attached", [])
            parts.append(f'<topic id="{tid}"><title>{title}</title>')
            parts.append(topics_xml(kids))
            parts.append("</topic>")
        parts.append("</topics></children>")
        return "".join(parts)

    root = sheet.get("rootTopic") or {}
    sheet_id = escape(str(sheet.get("id") or _new_id()))
    sheet_title = escape(str(sheet.get("title") or "测试用例"))
    root_id = escape(str(root.get("id") or _new_id()))
    root_title = escape(str(root.get("title") or ""))
    attached = root.get("children", {}).get("attached", [])

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        '<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" version="2.0">'
        f'<sheet id="{sheet_id}">'
        f'<topic id="{root_id}"><title>{root_title}</title>'
        f"{topics_xml(attached)}"
        "</topic>"
        f"<title>{sheet_title}</title>"
        "</sheet>"
        "</xmap-content>"
    )


_MIN_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd4c\x00\x00\x00\x00IEND\xaeB`\x82"
)


def export_xmind(data: dict, output: Path) -> None:
    sheet = _build_sheet(data)
    metadata = {
        "creator": {"name": "playwright-cli-testcase", "version": "1.0"},
    }
    manifest = {
        "file-entries": {
            "content.json": {},
            "content.xml": {},
            "metadata.json": {},
            "Thumbnails/thumbnail.png": {},
        }
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "content.json",
            json.dumps([sheet], ensure_ascii=False, indent=2),
        )
        zf.writestr("content.xml", _content_xml(sheet))
        zf.writestr(
            "metadata.json",
            json.dumps(metadata, ensure_ascii=False, indent=2),
        )
        zf.writestr(
            "manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2),
        )
        zf.writestr("Thumbnails/thumbnail.png", _MIN_PNG)


def main() -> int:
    parser = argparse.ArgumentParser(description="将 Web 测试用例 JSON 导出为 XMind")
    parser.add_argument("input_json", type=Path, help="输入 JSON 路径")
    parser.add_argument("output_xmind", type=Path, help="输出 .xmind 路径")
    args = parser.parse_args()

    try:
        data = load_data(args.input_json)
        export_xmind(data, args.output_xmind)
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"导出失败: {exc}", file=sys.stderr)
        return 1

    print(f"已导出 XMind: {args.output_xmind.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
