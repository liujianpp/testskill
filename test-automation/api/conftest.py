"""api 层共享夹具与 .env 加载。

config/.env 存在时自动加载（KEY=VALUE，# 注释），已有环境变量不覆盖。
"""
import os
from pathlib import Path

API_DIR = Path(__file__).resolve().parent


def _load_env() -> None:
    env_file = API_DIR / "config" / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


_load_env()
