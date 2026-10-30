# Python 可执行造数脚本（仅 HTTP）

Agent **直接写出完整可运行 `.py`**，不经中间 JSON。用户本地执行才真正造数/回滚；Skill 本身不连库、不调接口。

**禁止**生成 `*-db-seed.py` / pymysql 连库脚本。表结构造数只用 SQL 文件，由用户手工执行。

## 文件命名

统一写到输出目录下的 `script/` 子目录（不要写到输出根目录，也不要写到 Skill 自带的 `scripts/`）：

| 输入 | 文件 | 依赖 |
|---|---|---|
| 接口文档 | `script/{场景}-api-seed.py` | `pip install requests` |
| 仅表结构（无接口） | 不出 Python | — |

脚本顶部用注释写明依赖安装命令。

## CLI

```bash
python3 script/{场景}-api-seed.py seed       # 默认；省略子命令时等同 seed
python3 script/{场景}-api-seed.py rollback
```

- 成功 exit `0`
- 缺环境变量、请求失败、回滚不可用 → exit 非 `0`，并向 stderr 打印原因

## 环境变量（禁止写死密码）

优先已有环境变量；否则读输出根目录 `.env`（脚本内嵌加载，无需 `python-dotenv`）。出 Python 时同时写 `.env.example` + `.env`（占位），`.env` 勿提交。

| 变量 | 说明 |
|---|---|
| `SEED_BASE_URL` | 必填，如 `https://api.example.test` |
| `SEED_TOKEN` | 可选；需要鉴权时必填，放入 `Authorization: Bearer ...`（文档若规定其他 header 则跟文档） |

启动时检查必填变量；缺失则打印用法并 exit `1`。

脚本开头加载 `.env` 示例：

```python
from pathlib import Path

def load_dotenv() -> None:
    for path in (Path(__file__).resolve().parent.parent / ".env", Path.cwd() / ".env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = value
        break

load_dotenv()
```

`.env.example` 示例：

```bash
SEED_BASE_URL=http://localhost:8080
SEED_TOKEN=
```

## 公共约定

- 前缀常量：`PREFIX = "QA_YYYYMMDD_"`（与当天造数一致）
- `do_seed()` / `do_rollback()` + `main()` 解析 argv
- 依赖顺序：先主后从（seed）；回滚相反
- **串联链路**：`do_seed()` 按链路顺序调接口，把返回 id 传给下一步；同一画像用下标对齐（第 n 条公寓对应第 n 条房间 / 租客 / 入住）
- **唯一字段运行时随机**：手机、身份证、邮箱、唯一单号等在每次 `seed` 用 `secrets` 生成，并打印到结果清单；禁止写死固定号段
- seed 结束后打印结果清单（用途、关键业务键 / id），便于人工核对
- 回滚只删本次前缀数据；禁止 `TRUNCATE`、禁止无 WHERE 的 `DELETE`、禁止 `DROP`

## HTTP 脚本结构

```python
#!/usr/bin/env python3
"""场景造数（HTTP）。依赖: pip install requests"""
from __future__ import annotations

import os
import sys
import requests

PREFIX = "QA_YYYYMMDD_"

def env(name: str, default: str | None = None) -> str:
    ...

def do_seed() -> int:
    # 按依赖 / 串联链路顺序 POST；保存返回 id 并传给下一步；打印清单
    ...

def do_rollback() -> int:
    # 有 DELETE/取消接口：按反序调用
    # 无删除接口：print 明确提示，return 1
    ...

def main() -> int:
    action = (sys.argv[1] if len(sys.argv) > 1 else "seed").lower()
    if action == "seed":
        return do_seed()
    if action == "rollback":
        return do_rollback()
    print(f"usage: {sys.argv[0]} [seed|rollback]", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
```

要求：

- 请求 URL = `SEED_BASE_URL` + path
- body 为可提交 JSON，带前缀的可识别字段
- 正常画像期望 2xx；异常画像若文档约定 4xx，按约定断言，失败则非 0
- 无删除/取消类接口时，`do_rollback` 必须说明无法接口回滚并返回非 0（不要假装成功）

## 交付时给用户的示例命令

```bash
# 编辑项目根目录 .env 填入 SEED_TOKEN 后：
python3 script/{场景}-api-seed.py seed
python3 script/{场景}-api-seed.py rollback
```
