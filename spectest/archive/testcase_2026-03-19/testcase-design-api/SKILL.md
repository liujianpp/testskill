---
name: testcase-design-api
description: 从 OpenAPI/Swagger 规范自动生成高覆盖率 API 测试用例，并输出标准格式 Excel 文档。当用户说"生成API测试用例"、"设计接口测试用例"、"帮我写API用例"、"根据接口文档生成测试用例"、"design api test cases"、"对 XXX 接口设计测试用例"、"结合数据库设计测试用例"时触发此技能。支持 OpenAPI JSON 格式输入，自动对比已有测试用例找出缺口，并行调度3个子Agent进行测试用例设计，最终输出带验证SQL的标准测试用例Excel文档。
---

# API 测试用例设计技能

你是一名资深QA工程师，擅长基于API文档、业务逻辑、数据库结构进行高质量测试用例设计。本技能帮助用户从 OpenAPI 规范自动生成覆盖率最大化的测试用例，输出可直接使用的标准测试用例文档。

## 技能工作目录

```
~/.claude/skills/testcase-design-api/
├── workspaces/                    # 每次执行自动创建工作区（按时间戳命名）
│   └── YYYYMMDD_HHMMSS/
│       ├── project_info/          # 项目资料（用户手册、需求文档、业务逻辑文档）
│       ├── api_docs/              # API 接口文档（OpenAPI JSON）
│       ├── testcase/              # 已有测试用例文档（Excel）
│       ├── db_info/               # 数据库连接信息
│       ├── testcase_template/     # 测试用例表头参考文件
│       └── output/                # 最终输出目录
├── scripts/                       # 可复用执行脚本
│   ├── setup_workspace.py         # 创建工作区、复制用户文件
│   ├── find_uncovered_apis.py     # 对比 API 文档与已有用例，找出缺口
│   ├── query_db_schema.py         # 查询 MySQL 表结构
│   └── export_excel.py            # 将设计结果导出为标准 Excel
├── references/
│   ├── design-methods.md          # 测试设计方法（结对思维、等价类等）
│   └── testcase-headers.md        # 标准测试用例表头定义
└── assets/
    └── testcase_header_template.md # 标准表头参考
```

---

## 用户输入

向用户确认以下信息后启动流程：

| 参数 | 必填 | 说明 |
|------|------|------|
| API 文档路径 | ✅ 必填 | OpenAPI/Swagger JSON 文件路径 |
| 目标 API | 可选 | 指定哪些 API 要设计用例（不填则自动找缺口） |
| 已有测试用例 | 可选 | Excel 格式的已有测试用例，用于对比覆盖缺口 |
| 项目资料路径 | 可选 | 需求文档、业务逻辑文档等目录 |
| 业务逻辑文档 | 可选 | 补充 API 文档中未描述的业务规则 |
| 数据库连接信息 | 可选 | 数据库连接配置，默认使用 `测试mysql` 配置 |

**默认数据库配置文件（若用户未提供，自动使用）：**

`~/.claude/skills/testcase-design-api/db_config.json`（可直接编辑修改连接信息）

```json
{
  "测试mysql": {
    "host": "192.168.1.31",
    "port": 13306,
    "user": "ethan",
    "password": "ethan263*2",
    "database": null,
    "charset": "utf8mb4"
  }
}
```

> `setup_workspace.py` 执行时会自动读取此文件并复制到工作区 `db_info/db_config.json`。

---

## 执行步骤

### 环境准备：检查并初始化 uv Python 环境

> **每次启动技能前自动执行。首次运行约需 30 秒安装依赖；后续直接复用已有环境，几乎无等待。**
> **所有脚本必须用 `uv run` 执行，禁止直接使用 `python` 命令。**

#### 1. 确认 uv 已安装

**Linux / macOS / WSL：**

```bash
if ! command -v uv &> /dev/null; then
    echo "uv 未安装，正在自动安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
uv --version
```

**Windows（PowerShell）：**

```powershell
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv 未安装，正在自动安装..."
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
}
uv --version
```

#### 2. 同步技能 Python 环境（首次自动创建 .venv，后续瞬间复用）

**Linux / macOS / WSL：**

```bash
SKILL_DIR="$HOME/.claude/skills/testcase-design-api"
uv sync --project "$SKILL_DIR"
# 首次：自动创建 .venv 并安装 openpyxl、pymysql 等依赖（约 10-30 秒）
# 后续：检测到环境已存在且依赖未变更，瞬间完成
```

**Windows（PowerShell）：**

```powershell
$SkillDir = "$env:USERPROFILE\.claude\skills\testcase-design-api"
uv sync --project $SkillDir
```

环境就绪位置：
- Linux / WSL：`~/.claude/skills/testcase-design-api/.venv/`
- Windows：`%USERPROFILE%\.claude\skills\testcase-design-api\.venv\`

#### 3. 后续所有脚本的执行方式

> ⚠️ **重要：`SKILL_DIR=` 变量赋值行与 `uv run` 命令行必须在同一个 Bash 工具调用中执行，不可拆分为两次调用，否则变量会丢失，导致脚本路径错误（如 `/scripts/xxx.py`）。**

**Linux / macOS / WSL：**

```bash
SKILL_DIR="$HOME/.claude/skills/testcase-design-api"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/<脚本名>.py" [参数]
```

**Windows（PowerShell）：**

```powershell
$SkillDir = "$env:USERPROFILE\.claude\skills\testcase-design-api"
uv run --project $SkillDir python "$SkillDir\scripts\<脚本名>.py" [参数]
```

---

### Step 0：确认输入并创建工作区

运行 `scripts/setup_workspace.py`，自动创建带时间戳的工作区并复制用户文件：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-api"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/setup_workspace.py" \
  --api_doc "<API文档路径>" \
  [--testcase "<已有用例文件路径>"] \
  [--project_info "<项目资料目录>"] \
  [--business_doc "<业务逻辑文档路径>"] \
  [--db_info "<数据库配置文件路径>"]
```

输出：
- 新工作区路径（如 `workspaces/20260312_143000/`）
- 已复制文件清单

---

### Step 1：解析 API 文档，确定目标 API 列表

**若用户已指定目标 API**，直接使用指定列表。

**若用户未指定**，运行 `scripts/find_uncovered_apis.py` 自动找缺口：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-api"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/find_uncovered_apis.py" \
  --api_doc "<工作区>/api_docs/<文件名>" \
  [--testcase "<工作区>/testcase/<文件名>"]
```

该脚本会：
1. 解析 OpenAPI JSON，提取所有 `{method} {path}` API 端点及其 summary
2. 读取已有测试用例中的"接口路径"/"API"相关列（模糊匹配）
3. 对比找出没有对应测试用例的 API
4. 输出 `<工作区>/api_list_to_design.json`

**向用户展示待设计 API 列表**，确认后继续。

---

### Step 2：并行调度 3 个子 Agent 设计测试用例

将待设计 API 平均分成 3 组，并行启动 3 个子 Agent。每个子 Agent 按以下流程工作：

#### 子 Agent 工作流程

对每个分配到的 API：

**2.1 提取 API 详情**
- 从 OpenAPI JSON 中读取该 API 的完整定义：path、method、parameters、requestBody schema、response schema、description
- 递归解析 `$ref` 引用，展开所有嵌套 schema

**2.2 查询关联数据库表结构**
- 从 API description 或 schema 中提取可能的表名关键词（下划线命名、驼峰命名均支持）
- 运行 `scripts/query_db_schema.py` 查询对应表结构：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-api"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/query_db_schema.py" \
  --db_config "<工作区>/db_info/db_config.json" \
  --table_keywords "<关键词1>,<关键词2>"
```

- 获取字段名、类型、约束、注释

**2.3 获取真实测试数据（非新增类接口必须执行）**

判断当前 API 的操作类型：

| HTTP Method / 语义 | 操作类型 | 测试数据来源 |
|-------------------|----------|-------------|
| POST（创建/新增） | **新增类** | 自行构造合法值 |
| GET / POST（查询/搜索/列表） | **非新增类** | **从数据库随机取真实数据** |
| PUT / PATCH（修改/更新） | **非新增类** | **从数据库随机取真实数据** |
| DELETE（删除） | **非新增类** | **从数据库随机取真实数据** |

**对非新增类接口**，在设计用例前先执行 SQL 随机采样：

```sql
-- 查询/搜索类：随机取真实关键字段值（如名称、编号、关键词）
SELECT <name_field> FROM <db>.<table> WHERE is_deleted = 0 ORDER BY RAND() LIMIT 3;

-- 修改/删除/详情类：随机取已存在的主键 ID
SELECT id FROM <db>.<table> WHERE is_deleted = 0 ORDER BY RAND() LIMIT 3;
```

将查询到的**真实值**填入用例的 `test_data` 字段，并注明来源：
- 查询类示例：`{"keyword": "浦东"}（来源：DB随机取样 suburb_name）`
- 修改类示例：`{"id": 12345, "name": "浦东新区"}（id 来源：DB随机取样）`
- 删除类示例：`{"id": 12345}（来源：DB随机取样，操作前确认记录存在）`

> ⚠️ 若无法连接数据库，在 `test_data` 字段注明取样 SQL：`需执行 SELECT id FROM <table> WHERE is_deleted=0 ORDER BY RAND() LIMIT 1 获取实际值填入`，不得编造不存在的值。

**2.4 读取业务逻辑与项目资料**
- 读取 `<工作区>/project_info/` 下所有文档中与该 API 相关的内容
- 重点关注：字段枚举值、业务规则、状态机流转、权限控制

**2.5 使用多种测试设计方法生成用例**

参考 `references/design-methods.md`，综合运用：
- **等价类划分**：每个输入参数识别有效类/无效类
- **边界值分析**：min/min+1/max-1/max/null/empty
- **结对思维（Pairwise）**：使用正交表，每两个参数的取值组合至少覆盖一次
- **场景法**：端到端正向主流程、异常流程
- **错误猜测**：根据 DB 约束和业务规则猜测易出错点

**覆盖率要求：**
- 正向用例 ≥ 40%
- 负向用例 ≥ 30%
- 边界用例 ≥ 20%
- 安全用例 ≥ 10%
- 每个 API 上限 20 个用例

**2.7 为每条用例编写验证 SQL**

预期结果必须包含：
- 响应字段断言（HTTP status code、success 标志、关键字段值）
- 数据库验证 SQL（SELECT 语句验证数据变更效果）
- 例如：`SELECT * FROM lsp_address_suburb WHERE keyword LIKE '%上海%' LIMIT 5;`

**2.8 输出格式**

每个子 Agent 将结果写入 `<工作区>/output/cases_batch_N.json`，格式与功能测试用例保持一致（25列）：

> `test_type` 为内部字段（正向/负向/边界/安全/权限），用于 Excel 行颜色区分，**不导出为列**。
> `case_type` 固定填 `"API测试"`，导出至 Excel 第 Q 列。

```json
[
  {
    "project": "",
    "module": "地址管理",
    "feature": "地址搜索",
    "test_item": "有效关键字模糊搜索",
    "title": "有效关键字标准搜索返回匹配结果",
    "preconditions": "服务正常运行；数据库中存在包含'上海'的地址记录",
    "db_tables": "lsp_dev.lsp_address_suburb",
    "test_data": "{\"pages\":{\"keyword\":\"上海\",\"limit\":20,\"page\":1}}",
    "steps": "1. POST /address/search\n2. Body: {\"pages\":{\"keyword\":\"上海\",\"limit\":20,\"page\":1}}\n3. 查看响应",
    "expected_result": "HTTP 200；success=true；data列表不为空；tp>=0",
    "validation_sql": "SELECT COUNT(*) FROM lsp_address_suburb WHERE suburb_name LIKE '%上海%';",
    "actual_result": "",
    "is_passed": "",
    "estimated_hours": "0.5",
    "execute_date": "",
    "test_progress": "",
    "case_type": "API测试",
    "priority": "P0",
    "is_regression": "是",
    "is_blocker": "是",
    "requirement_id": "",
    "api_url": "POST /address/search",
    "bug_count": "0",
    "bug_unresolved": "0",
    "case_version": "1",
    "test_type": "正向"
  }
]
```

---

### Step 3：汇总并导出 Excel

运行 `scripts/export_excel.py` 将所有批次的结果合并导出：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-api"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/export_excel.py" \
  --workspace "<工作区路径>" \
  --template "<工作区>/testcase_template/template_headers.json"
```

```powershell
# Windows（PowerShell）
$SkillDir = "$env:USERPROFILE\.claude\skills\testcase-design-api"
uv run --project $SkillDir python "$SkillDir\scripts\export_excel.py" `
  --workspace "<工作区路径>" `
  --template "<工作区>\testcase_template\template_headers.json"
```

输出：`<工作区>/output/api_testcases_YYYYMMDD_HHMMSS.xlsx`

Excel 格式：
- **标题行**：按 `references/testcase-headers.md` 定义的标准表头
- **样式**：表头蓝底白字；正向用例白底；负向用例浅黄底；边界用例浅蓝底；安全用例浅橙底
- **分组**：按 API 分组，相同 API 的用例连续排列（合并首列单元格）

---

### Step 4：汇报结果

向用户展示：
- 工作区路径
- 已设计 API 数量
- 总用例数及覆盖率分布（正向/负向/边界/安全）
- 输出 Excel 文件路径
- 有哪些 API 未能查到数据库表结构（提示用户补充）

---

## 参考文档

- **测试设计方法**：`references/design-methods.md` — 结对思维、等价类、边界值详细说明
- **标准表头定义**：`references/testcase-headers.md` — 每个字段的含义、取值范围
- **数据库查询代码**：`scripts/query_db_schema.py`
