# test-automation：测试资产库（主干 × 迭代 × 接口/界面）

本目录是**测试资产的沉淀与执行库**：用例库（25 列 Excel）+ 自动化脚本（接口 pytest / 界面 Playwright / 小程序 Jest）+ 统一报告。位于技能仓库内（`test-automation/`）——技能负责**生成**，本目录负责**沉淀与执行**。

## 目录结构

```
test-automation/
├── cases/                            # 用例库（25 列 Excel，spectest 产物沉淀）
│   ├── main/                         # 主干回归用例集（回归基准）
│   │   ├── api/                      #   接口用例 xlsx
│   │   └── web/                      #   界面用例 xlsx
│   └── iterations/<版本号>/          # 迭代用例（上线后晋级 → main/）
├── api/                              # 接口自动化（pytest + requests）
│   ├── main/                         #   主干脚本（核心链路回归）
│   ├── iterations/<版本号>/          #   迭代新增脚本
│   ├── conftest.py + pytest.ini + requirements.txt
│   └── config/.env.example           #   环境配置模板（.env 不入库）
├── web/                              # 界面自动化（Playwright）
│   ├── main/                         #   主干脚本（tests/pages/fixtures）
│   ├── iterations/<版本号>/
│   └── playwright.config.ts + package.json
├── miniprogram/                      # 小程序自动化（Jest，见 miniprogram/README.md）
├── reports/                          # 运行报告（playwright/allure/统一报告，不入库）
（CI workflow 位于仓库根 .github/workflows/regression.yml，working-directory 指向本目录）
```

## 核心约定：主干（main）与迭代（iterations）

**目录即身份**——一个测试资产只属于一处：

| 目录 | 含义 | 何时跑 |
|------|------|--------|
| `main/` | 主干回归集：核心链路 + 已上线稳定用例/脚本 | 每日定时 + 发版前 |
| `iterations/<版本号>/` | 本迭代新增用例/脚本 | 迭代期间日常 + 迭代回归 |

**版本号命名**：`YYYYQn-<特性>`（如 `2026Q4-tenant-login`）或 `YYYYMM-<特性>`。

### 分拣规则（用例从哪来）

spectest 生成的 25 列 Excel（`spectest/changes/<name>/artifacts/<name>_testcases.xlsx`），按**「是否回归用例」列**分拣：

- 回归用例行 → 追加进 `cases/main/api|web/` 对应模块合表（`<模块>.xlsx`，按「模块+用例标题」去重）
- 非回归行 → 落 `cases/iterations/<版本号>/`（整表副本供迭代评审）
- API URL 列非空的用例归属 `api/`，其余归属 `web/`

```bash
# 分拣（P1-3，已实现并验证）
uv run --with openpyxl python scripts/promote_cases.py \
  --input <spectest产出的25列.xlsx> --version 2026Q4-xxx [--dry-run]
```

### 晋级规则（迭代 → 主干）

1. 新增用例/脚本一律先进 `iterations/<版本号>/`
2. **晋级条件**：迭代功能已上线，且回归 **2 轮全绿**（人工确认）
3. **晋级动作**（P1-4 脚本化，默认 dry-run，`--confirm` 才执行）：

```bash
uv run --with openpyxl python scripts/promote_iteration.py --version 2026Q4-xxx [--confirm]
```

   - 用例：迭代 xlsx 按 API URL 归属 api/web、按「模块」并入 `cases/main/` 合表（含去重）
   - 脚本：`api/iterations/<ver>/*.py` → `api/main/`；`web/iterations/<ver>/*.spec.ts` → `web/main/tests/`，并自动把 `'../../main/'` 引用改写为 `'../'`
   - 小程序清单合并为人工步骤（见 miniprogram/README.md）
   - 完成后迭代目录归档到 `cases/iterations/_promoted/<ver>-<日期>/`，并追加 `reports/promote-log.md`

## 快速开始

### 接口（pytest）

```bash
cd api
cp config/.env.example config/.env    # 填 API_BASE_URL
uv venv .venv && uv pip install -r requirements.txt --python .venv/Scripts/python.exe
.venv/Scripts/python.exe -m pytest                      # 全部（main + iterations）
.venv/Scripts/python.exe -m pytest main                 # 仅主干
```

### 界面（Playwright）

```bash
cd web
npm install
npx playwright install chromium
npx playwright test                    # 全部
npx playwright test main               # 仅主干（CI 即此命令）
```

真实环境冒烟需设置 `BASE_URL`（复制 `web/.env.example` → `.env`）；未设置时真实环境用例自动跳过，本地自检用例始终执行（验证安装）。

**界面迭代的 import 约定**：迭代 spec 放 `web/iterations/<ver>/`（扁平），引用主干公共层用 `'../../main/pages/...'` / `'../../main/fixtures/...'`；晋级脚本会自动改写为 `'../...'`。

## 环境与密钥

- 各层 `.env` **不入库**（.gitignore 已排除），模板见各层 `.env.example`
- 账号密码一律环境变量注入，禁止写进用例/脚本/仓库

## 与技能链的关系

```
spectest（用例设计，25列 Excel）
   │  按「是否回归用例」列分拣 ↓
cases/main | cases/iterations
   │  web-script-author（P2-5，待建）对界面用例生成 Playwright 脚本
   │  api 用例 → ApiAutoTest2.0 流水线生成/执行 pytest 脚本
api/web/miniprogram 脚本库
   │  CI（regression.yml）定时跑 main
reports/ 统一报告（aggregate_reports.py 四源汇总）
```

## 当前状态

- [x] P0-1 仓库骨架（本仓库）
- [x] P0-2 Playwright 界面脚本层（install-check 开箱绿 + 真实环境模板）
- [x] P1-3 用例沉淀脚本 `scripts/promote_cases.py`（已验证：分拣/去重/幂等）
- [x] P1-4 迭代→主干晋级脚本 `scripts/promote_iteration.py`（已验证：模块合表/脚本搬移/import 改写/归档）
- [x] P2-5 web-script-author 技能（位于技能仓库 `E:\AI\skills\web-script-author\`，25 列用例 → Playwright spec）
- [x] P3-6 CI 定时回归（workflow 位于仓库根 .github/workflows/regression.yml，配 secrets 后生效；汇总器已支持 Playwright JSON 源）
