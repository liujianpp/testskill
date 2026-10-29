# 10 · 技能详解：test-automation（测试资产库 + 每日回归 CI）

> **一句话**：所有测试资产的**长期存放与执行仓库**——用例库（25 列 Excel）+ 自动化脚本（接口 pytest / 界面 Playwright / 小程序 Jest）+ 每晚自动回归。**它不是技能，是仓库**；技能负责「生成」，它负责「沉淀与执行」。

[← 返回总导读](README.md) | 套件自带文档：[test-automation/README.md](../../test-automation/README.md)、[使用说明.md](../../test-automation/使用说明.md)

---

## 1. 目录结构

```
test-automation/
├── cases/                            # 用例库（25 列 Excel）
│   ├── main/{api,web}/               #   主干回归用例集（<模块>.xlsx 合表）
│   └── iterations/<版本号>/          #   迭代用例（上线后晋级 → main/）
├── api/                              # 接口自动化（pytest + requests）
│   ├── main/ + iterations/<版本号>/
│   └── conftest.py + pytest.ini + requirements.txt + config/.env.example
├── web/                              # 界面自动化（Playwright）
│   ├── main/{tests,pages,fixtures}/ + iterations/<版本号>/
│   └── playwright.config.ts + package.json
├── miniprogram/                      # 小程序层（清单制：suite-main.json + iterations suite.json）
├── scripts/                          # promote_cases.py（分拣）+ promote_iteration.py（晋级）
└── reports/                          # 运行报告（不入库；含 promote-log.md）
```

CI 配置在**仓库根** `.github/workflows/regression.yml`。

## 2. 核心概念：目录即身份

| 目录 | 含义 | 何时跑 |
|------|------|--------|
| `main/` | 主干回归集：核心链路 + 已上线稳定资产 | **每日定时 + 发版前** |
| `iterations/<版本号>/` | 本迭代新增 | 迭代期间日常 + 迭代回归 |

- 一个测试资产只属于一处；
- **版本号命名**：`YYYYQn-<特性>`（如 `2026Q4-tenant-login`）或 `YYYYMM-<特性>`。

## 3. 分拣：把 spectest 产物入库（promote_cases.py）

spectest 生成的 25 列 Excel，按「**是否回归用例**」列自动分拣：

- 回归用例行 → 追加进 `cases/main/api|web/` 对应模块合表（按「模块+用例标题」去重）；
- 非回归行 → `cases/iterations/<版本号>/`（整表副本）；
- 「API URL」列非空归 `api/`，其余归 `web/`。

```bash
# 在 test-automation/ 下执行；先 --dry-run 预演看效果
uv run --with openpyxl python scripts/promote_cases.py \
  --input <spectest 的 25列.xlsx> --version 2026Q4-xxx [--dry-run]
```

## 4. 晋级：迭代 → 主干（promote_iteration.py）

- **晋级条件**：迭代功能已上线 + 回归 **2 轮全绿**（人工确认）；
- 默认 dry-run 预览，`--confirm` 才真执行：

```bash
uv run --with openpyxl python scripts/promote_iteration.py --version 2026Q4-xxx [--confirm]
```

- 它会做：用例并入 `cases/main/`（去重）；`api/iterations/` 脚本移入 `api/main/`；`web/iterations/` spec 移入 `web/main/tests/`（自动把 `'../../main/'` 引用改写为 `'../'`）；完成后迭代目录归档到 `cases/iterations/_promoted/<ver>-<日期>/`，并追加 `reports/promote-log.md`。

## 5. 手动跑一遍（验证资产是否健康）

**接口（pytest）**：

```bash
cd api && cp config/.env.example config/.env   # 填 API_BASE_URL
uv venv .venv && uv pip install -r requirements.txt --python .venv/Scripts/python.exe
.venv/Scripts/python.exe -m pytest        # 全部（main + iterations）
.venv/Scripts/python.exe -m pytest main   # 仅主干
```

**界面（Playwright）**：

```bash
cd web && npm install && npx playwright install chromium
npx playwright test              # 全部
npx playwright test main         # 仅主干（CI 即此命令）
```

> 未设 `BASE_URL` 时，真实环境用例自动跳过、本地自检用例始终执行——所以没配环境也不会满屏报错。

## 6. 每日回归 CI

- 位置：仓库根 `.github/workflows/regression.yml`；
- **每日 02:17 定时**跑 `test-automation/` 下主干回归：接口（pytest main）+ 界面（Playwright chromium）；
- 支持手动触发与 `scope=main|all`；
- 结果报告落 `reports/`（不入库）。

## 7. 与技能链的关系（一张图看懂资产从哪来到哪去）

```
spectest（25列用例设计）
   │ promote_cases.py 按「是否回归用例」分拣 ↓
cases/main | cases/iterations
   │ web-script-author（界面用例→Playwright spec）/ ApiAutoTest2.0（接口脚本）
api/web/miniprogram 脚本库
   │ CI（regression.yml）每晚跑 main
reports/（aggregate_reports.py 五源统一报告，playwright-results.json 为第五源）
```

## 8. 使用话术

**场景 1：本次迭代做完，入库**
> 「把 spectest/changes/jifen-v2/artifacts/jifen-v2_testcases.xlsx 分拣入库，版本号 2026Q4-jifen，先 dry-run 给我看」

**场景 2：迭代上线，晋级主干**
> 「把 2026Q4-jifen 晋级进主干，先预览」

**场景 3：手动跑主干回归**
> 「在 test-automation/web 下跑 npx playwright test main」

## 9. 环境与密钥

- 各层 `.env` 不入库（已 gitignore），模板见各层 `.env.example`；
- 账号密码一律环境变量，禁止写进用例/脚本/仓库。

## 10. 常见问题

**Q：迭代脚本 import 主干的公共模块怎么写？**
迭代 spec 引用主干公共层用 `'../../main/pages/...'`；晋级脚本会自动改写路径。

**Q：晋级前为什么必须 2 轮全绿？**
防止把不稳定用例塞进主干，害得每日 CI 天天红。

**Q：reports/ 为什么不入库？**
报告是运行产物，量大且每次不同；只保留 `promote-log.md`（晋级台账）入库。

---

*本册基于 test-automation 2026-10-29 现状整理。*
