"""
CSV-driven API tests. Parametrized via conftest pytest_generate_tests.
Run with: run_tests.py --csv=test_cases.csv (or pytest this file --csv=... from project root).
"""

import json
import logging
import os

import allure
import pytest
import requests

logger = logging.getLogger(__name__)


def _extract_json_path(obj, path: str):
    if not path or not path.startswith("$."):
        return None
    keys = path[2:].split(".")
    cur = obj
    for k in keys:
        cur = cur.get(k) if isinstance(cur, dict) else None
        if cur is None:
            break
    return cur


def _apply_inject(headers: dict, extracted: dict | None, inject_spec: str):
    """根据注入方式将前置依赖产出注入请求头。extracted 为依赖的 extract 键值，支持任意占位符 {key}。"""
    if not extracted or not inject_spec or not isinstance(extracted, dict):
        return
    if inject_spec.strip().lower() == "cookie":
        return
    parts = inject_spec.split(":", 2)
    if len(parts) >= 3 and parts[0].strip().lower() == "header":
        name = parts[1].strip()
        template = parts[2].strip()
        for key, val in extracted.items():
            if val is not None and "{" + key + "}" in template:
                template = template.replace("{" + key + "}", str(val))
        if template:
            headers[name] = template


def _apply_path_params(path: str, path_params_str: str) -> str:
    """用 CSV 的「路径参数」列替换 path 中的 {key}，值为用户填写的字面量，不做占位符替换。"""
    if not path_params_str or not path_params_str.strip():
        return path
    try:
        params = json.loads(path_params_str)
    except json.JSONDecodeError:
        logger.warning("路径参数 JSON 解析失败，跳过替换: %s", path_params_str[:100])
        return path
    if not isinstance(params, dict):
        return path
    for key, val in params.items():
        if val is None:
            continue
        path = path.replace("{" + key + "}", str(val))
    return path


def _to_number(val):
    """尽量将值转换为数字，无法转换则返回原值。"""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        v = val.strip()
        try:
            if "." in v:
                return float(v)
            return int(v)
        except ValueError:
            return val
    return val


def _parse_expected_value(raw: str):
    """解析右侧期望值字符串，支持数字与字符串两类。"""
    s = raw.strip()
    # 带双引号的，去掉最外层引号，按字符串处理
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    # 纯数字或小数，按数字处理
    num = _to_number(s)
    return num


def _evaluate_condition(data: dict, expr_str: str):
    """
    解析并断言单个条件表达式。
    支持：
    - $.code==200
    - $.data.id!=1
    - $.data.total>=0
    - $.data.username==user001
    - 仅 JSONPath：$.data.token  → 断言该值为真
    """
    expr = expr_str.strip()
    if not expr:
        return

    # 运算符按长度优先匹配，避免 >= 被拆成 >
    operators = [">=", "<=", ">", "<", "!=", "=="]
    op = None
    left = right = None
    for candidate in operators:
        if candidate in expr:
            parts = expr.split(candidate, 1)
            if len(parts) == 2:
                left, right = parts[0].strip(), parts[1].strip()
                op = candidate
                break

    # 无运算符：仅做 JSONPath 存在性/真值校验
    if op is None:
        actual = _extract_json_path(data, expr)
        assert actual, f"Check failed: {expr} is falsy or missing"
        return

    actual = _extract_json_path(data, left)
    assert actual is not None, f"Check failed: {left} is missing"
    expected = _parse_expected_value(right)

    # 数值比较运算
    if op in {">", ">=", "<", "<="}:
        actual_num = _to_number(actual)
        expected_num = _to_number(expected)
        if not isinstance(actual_num, (int, float)) or not isinstance(expected_num, (int, float)):
            raise AssertionError(
                f"Numeric comparison requires number types: {left}={actual!r}, expected={expected!r}"
            )
        if op == ">":
            assert actual_num > expected_num, f"Check failed: {left} = {actual_num} !> {expected_num}"
        elif op == ">=":
            assert actual_num >= expected_num, f"Check failed: {left} = {actual_num} !>= {expected_num}"
        elif op == "<":
            assert actual_num < expected_num, f"Check failed: {left} = {actual_num} !< {expected_num}"
        else:  # <=
            assert actual_num <= expected_num, f"Check failed: {left} = {actual_num} !<= {expected_num}"
        return

    # 等值／不等值比较
    actual_num = _to_number(actual)
    expected_num = _to_number(expected)
    # 若两边都可转为数字，则按数字比较；否则按字符串比较
    if isinstance(actual_num, (int, float)) and isinstance(expected_num, (int, float)):
        a_val, e_val = actual_num, expected_num
    else:
        a_val, e_val = str(actual), str(expected)

    if op == "==":
        assert a_val == e_val, f"Check failed: {left} = {a_val!r} != {e_val!r}"
    elif op == "!=":
        assert a_val != e_val, f"Check failed: {left} = {a_val!r} == {e_val!r}"
    else:
        raise AssertionError(f"Unsupported operator in expression: {expr_str}")


def test_api_row(row, auth_cookie):
    """Execute one API test per CSV row."""
    if not row or not row.get("接口路径"):
        pytest.skip("No CSV data or --csv not specified")

    base_url = os.environ.get("BASE_URL", "http://localhost:8080")
    path = row.get("接口路径", "").strip()
    path_params_str = row.get("路径参数") or ""
    path = _apply_path_params(path, path_params_str)
    method = (row.get("请求方法") or "GET").strip().upper()
    req_body_str = (row.get("请求体/参数") or "")
    expected_status = int(row.get("预期状态码") or 200)
    expected_check = (row.get("预期响应校验") or "").strip()
    dep = (row.get("前置依赖") or "无").strip()
    inject = row.get("注入方式") or ""
    case_id = row.get("用例ID", "")
    case_name = row.get("用例名称", "")

    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json"}

    if dep != "无" and auth_cookie:
        extracted = auth_cookie.get(dep) if isinstance(auth_cookie, dict) else auth_cookie
        _apply_inject(headers, extracted, inject)

    with allure.step(f"{case_id} {case_name}"):
        body = json.loads(req_body_str) if req_body_str.strip() and method != "GET" else None
        logger.info(
            "请求: %s %s | headers=%s | body=%s",
            method, url, headers, body if body is not None else "(无)",
        )
        if method == "GET":
            resp = requests.request(method, url, headers=headers, timeout=30)
        else:
            resp = requests.request(method, url, json=body, headers=headers, timeout=30)

        try:
            body_log = resp.json()
            body_str = json.dumps(body_log, ensure_ascii=False)
        except Exception:
            body_str = resp.text
        if len(body_str) > 500:
            body_str = body_str[:500] + "..."
        logger.info("响应: status=%s | body=%s", resp.status_code, body_str)
        try:
            err_body = json.dumps(resp.json(), ensure_ascii=False)[:200]
        except Exception:
            err_body = resp.text[:200]
        assert resp.status_code == expected_status, (
            f"Expected {expected_status}, got {resp.status_code}: {err_body}"
        )

        if expected_check and "application/json" in resp.headers.get("content-type", ""):
            data = resp.json()
            # 支持多条件：按 && 或 ; 拆开逐个断言，如 $.code==200 && $.data.token
            for part in expected_check.replace(";", "&&").split("&&"):
                part = part.strip()
                if not part:
                    continue
                _evaluate_condition(data, part)
