"""主干冒烟样例（api/main）。

- test_repo_contract: 仓库结构自检（始终应通过，CI 布线验证用）
- test_api_reachable: API_BASE_URL 可达性冒烟（未配置环境时自动跳过）
"""
import os
from pathlib import Path

import pytest
import requests

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_repo_contract():
    """骨架自检：主干/迭代目录齐备。"""
    expected_dirs = [
        REPO_ROOT / "cases" / "main" / "api",
        REPO_ROOT / "cases" / "main" / "web",
        REPO_ROOT / "cases" / "iterations",
        REPO_ROOT / "api" / "main",
        REPO_ROOT / "api" / "iterations",
        REPO_ROOT / "web" / "main",
        REPO_ROOT / "web" / "iterations",
        REPO_ROOT / "reports",
    ]
    for d in expected_dirs:
        assert d.is_dir(), f"缺少目录：{d}"


@pytest.mark.skipif(
    not os.getenv("API_BASE_URL"),
    reason="未设置 API_BASE_URL（见 api/config/.env.example）",
)
def test_api_reachable():
    """被测服务可达性冒烟：任何 HTTP 响应即说明域名与网络通，不假设首页语义。"""
    base = os.environ["API_BASE_URL"].rstrip("/")
    resp = requests.get(base, timeout=10)
    assert resp.status_code < 600
