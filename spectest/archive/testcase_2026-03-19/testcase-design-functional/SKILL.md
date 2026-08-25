---
name: testcase-design-functional
description: 从功能清单（Markdown格式）自动生成高覆盖率功能测试用例，并输出标准格式 Excel 文档。当用户说"生成功能测试用例"、"设计功能用例"、"帮我写功能测试用例"、"根据功能清单生成测试用例"、"design functional test cases"、"对XXX功能设计测试用例"、"根据需求设计用例"、"功能测试用例设计"时触发此技能。支持Markdown格式功能清单输入，自动解析功能点，对比已有用例找缺口，并行调度3个子Agent进行测试用例设计，最终输出带数据库验证SQL的标准测试用例Excel文档。
---

# 功能测试用例设计技能

你是一名资深QA工程师，擅长基于功能清单、需求文档、业务逻辑、数据库结构进行高质量功能测试用例设计。本技能从功能清单自动生成覆盖率最大化的功能测试用例，输出可直接使用的标准测试用例文档。

## 技能工作目录

```
~/.claude/skills/testcase-design-functional/
├── workspaces/                    # 每次执行自动创建工作区（按时间戳命名）
│   └── YYYYMMDD_HHMMSS/
│       ├── project_info/          # 项目资料（用户手册、需求文档、业务逻辑文档）
│       ├── api_docs/              # API 接口文档（OpenAPI JSON，可选）
│       ├── testcase/              # 已有测试用例文档（Excel）
│       ├── db_info/               # 数据库连接配置
│       ├── testcase_template/     # 测试用例表头参考文件
│       └── output/                # 最终输出目录
├── scripts/                       # 可复用执行脚本
│   ├── setup_workspace.py         # 创建工作区、复制用户文件
│   ├── parse_feature_list.py      # 解析 MD 功能清单，提取结构化功能点
│   ├── find_uncovered_features.py # 对比已有用例，找出未覆盖功能点
│   ├── query_db_schema.py         # 查询 MySQL 表结构
│   └── export_excel.py            # 导出标准 Excel
├── references/
│   ├── design-methods.md          # 功能测试设计方法（等价类、场景法、判定表等）
│   └── testcase-headers.md        # 标准测试用例表头定义
└── assets/
    └── testcase_header_template.md # 标准表头参考示例
```

---

## 功能清单格式说明

功能清单为 Markdown 文档，格式如下：

```markdown
# 模块名称（一级标题）

## 功能点名称（二级标题）

功能描述(用户故事)：[从用户视角描述功能场景]
设计数据库表：[库名.表名，多个用逗号分隔]
技术栈：[前端框架, 后端框架]
关联接口：[可选，关联的 API 路径]
业务规则：[可选，具体业务约束条件]
```

---

## 用户输入

向用户确认以下信息后启动流程：

| 参数 | 必填 | 说明 |
|------|------|------|
| 功能清单文档 | ✅ 必填 | Markdown 格式（.md）功能清单文件路径 |
| 需求文档 | 可选 | PDF/Word/Markdown 格式需求文档 |
| API 接口文档 | 可选 | OpenAPI JSON 格式（辅助了解接口细节） |
| 目标功能点 | 可选 | 指定哪些功能要设计用例（不填则自动对比找缺口） |
| 已有测试用例 | 可选 | Excel 格式已有用例，用于对比覆盖缺口 |
| 项目资料路径 | 可选 | 需求、业务逻辑等文档目录 |
| 业务逻辑文档 | 可选 | 补充功能清单未涵盖的业务规则 |
| 数据库连接信息 | 可选 | 默认使用 `测试mysql` 配置 |

**默认数据库配置文件（若用户未提供，自动使用）：**

`~/.claude/skills/testcase-design-functional/db_config.json`（可直接编辑修改连接信息）

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

### 观测初始化（技能启动时第一步执行）

```bash
# ── 观测初始化（不可省略）──────────────────────────────
source ~/skill-observer/scripts/logger.sh
skill_start "testcase-design-functional" "$(date '+%Y-%m-%d %H:%M')"
# 在另一个终端运行以下命令实时监控：
# tail -f /tmp/skill-observer/testcase-design-functional_*.jsonl | python3 ~/skill-observer/scripts/tail_viewer.py
mkdir -p /tmp/skill-observer
# ──────────────────────────────────────────────────────
```

---

### 环境准备：检查并初始化 uv Python 环境

> **每次启动技能前自动执行。首次运行约需 30 秒安装依赖；后续直接复用已有环境，几乎无等待。**
> **所有脚本必须用 `uv run` 执行，禁止直接使用 `python` 命令。**

#### 1. 确认 uv 已安装

**Linux / macOS / WSL：**

```bash
# ── Step ENV-1: 检查 uv 安装 ────────────────────────────
skill_step 0 "检查 uv 环境" "验证 uv 是否已安装"

if ! command -v uv &> /dev/null; then
    echo "uv 未安装，正在自动安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
uv --version

if [ $? -ne 0 ]; then
  skill_step_fail "uv 安装或检测失败"
  skill_end "fail" "环境准备失败：uv 不可用"
  exit 1
fi

UV_VERSION=$(uv --version)
skill_var "uv_version" "$UV_VERSION"
skill_step_ok "uv 环境就绪：$UV_VERSION"
# ─────────────────────────────────────────────────────
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
# ── Step ENV-2: 同步 Python 依赖 ────────────────────────
skill_step 0 "同步 Python 环境" "uv sync 安装/检查依赖"

SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
skill_var "skill_dir" "$SKILL_DIR"

uv sync --project "$SKILL_DIR"

if [ $? -ne 0 ]; then
  skill_step_fail "uv sync 失败，依赖安装异常"
  skill_end "fail" "Python 环境同步失败"
  exit 1
fi

skill_step_ok "Python 环境就绪，依赖已同步"
# ─────────────────────────────────────────────────────
```

**Windows（PowerShell）：**

```powershell
$SkillDir = "$env:USERPROFILE\.claude\skills\testcase-design-functional"
uv sync --project $SkillDir
```

环境就绪位置：
- Linux / WSL：`~/.claude/skills/testcase-design-functional/.venv/`
- Windows：`%USERPROFILE%\.claude\skills\testcase-design-functional\.venv\`

#### 3. 后续所有脚本的执行方式

> ⚠️ **重要：`SKILL_DIR=` 变量赋值行与 `uv run` 命令行必须在同一个 Bash 工具调用中执行，不可拆分为两次调用，否则变量会丢失，导致脚本路径错误（如 `/scripts/xxx.py`）。**

**Linux / macOS / WSL：**

```bash
SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/<脚本名>.py" [参数]
```

**Windows（PowerShell）：**

```powershell
$SkillDir = "$env:USERPROFILE\.claude\skills\testcase-design-functional"
uv run --project $SkillDir python "$SkillDir\scripts\<脚本名>.py" [参数]
```

---

### Step 0：确认输入并创建工作区

#### ⚠️ 必填检查：功能清单文档

**首先判断用户是否提供了功能清单文档（.md 格式）。**

**如果用户未提供功能清单**，立即输出以下提示，并 **终止任务，不得继续执行后续步骤**：

---

> ❌ **缺少必填项：功能清单文档**
>
> 本技能需要一份 Markdown 格式的功能清单才能继续。
>
> **请按以下格式准备功能清单文档（.md 文件），然后重新告诉我文件路径：**
>
> ```markdown
> # 模块名称（一级标题，对应业务模块）
>
> ## 功能点名称（二级标题，对应具体功能）
>
> 功能描述(用户故事)：作为 [角色]，我希望 [操作]，以便 [目的]
> 设计数据库表：库名.表名（多个用逗号分隔，如 lsp_dev.lsp_address_suburb）
> 技术栈：前端vue, 后端springboot
> 关联接口：/api/xxx（可选）
> 业务规则：具体业务约束条件（可选）
> ```
>
> **样例模板文档路径：**
> `~/.claude/skills/testcase-design-functional/assets/testcase_header_template.md`
>
> **样例功能清单：**
> ```markdown
> # 地址管理
>
> ## 地址搜索
>
> 功能描述(用户故事)：在地址列表页面，用户输入关键字点击搜索，页面展示匹配的地址列表，支持模糊搜索。
> 设计数据库表：lsp_dev.lsp_address_suburb
> 技术栈：前端vue, 后端springboot
> 关联接口：POST /address/search
>
> ## 地址新增
>
> 功能描述(用户故事)：用户填写地址表单并提交，系统校验数据合法性，保存成功后列表刷新显示新记录。
> 设计数据库表：lsp_dev.lsp_address_suburb
> 技术栈：前端vue, 后端springboot
> 业务规则：地址名称不可重复；所属区域为必填项
> ```
>
> 准备好后，请告知：**功能清单文件的完整路径**，以及其他可选文件（需求文档、已有测试用例等）。

---

**若用户已提供功能清单路径**，继续执行以下步骤。

```bash
# ── Step 0: 创建工作区 ────────────────────────────────
skill_step 0 "创建工作区" "setup_workspace.py 初始化工作目录并复制输入文件"

FEATURE_LIST_PATH="<功能清单路径>"
skill_var "feature_list_path" "$FEATURE_LIST_PATH"

SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/setup_workspace.py" \
  --feature_list "$FEATURE_LIST_PATH" \
  [--requirement "<需求文档路径>"] \
  [--api_doc "<API文档路径>"] \
  [--testcase "<已有用例文件路径>"] \
  [--project_info "<项目资料目录>"] \
  [--business_doc "<业务逻辑文档路径>"] \
  [--db_info "<数据库配置文件路径>"]

if [ $? -ne 0 ]; then
  skill_step_fail "工作区创建失败"
  skill_end "fail" "Step 0 失败：setup_workspace.py 执行错误"
  exit 1
fi

# 获取创建的工作区路径（从脚本输出提取）
WORKSPACE=$(ls -td "$HOME/.claude/skills/testcase-design-functional/workspaces"/*/  | head -1 | sed 's|/$||')
skill_var "workspace_path" "$WORKSPACE"
skill_log "工作区已创建" "$WORKSPACE"

skill_step_ok "工作区创建成功：$WORKSPACE"
# ─────────────────────────────────────────────────────
```

运行 `scripts/setup_workspace.py`，创建带时间戳工作区并复制用户文件：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/setup_workspace.py" \
  --feature_list "<功能清单路径>" \
  [--requirement "<需求文档路径>"] \
  [--api_doc "<API文档路径>"] \
  [--testcase "<已有用例文件路径>"] \
  [--project_info "<项目资料目录>"] \
  [--business_doc "<业务逻辑文档路径>"] \
  [--db_info "<数据库配置文件路径>"]
```

```powershell
# Windows（PowerShell）
$SkillDir = "$env:USERPROFILE\.claude\skills\testcase-design-functional"
uv run --project $SkillDir python "$SkillDir\scripts\setup_workspace.py" `
  --feature_list "<功能清单路径>" `
  [--requirement "<需求文档路径>"] `
  [--testcase "<已有用例文件路径>"]
```

---

### Step 1：解析功能清单，提取结构化功能点

```bash
# ── Step 1: 解析功能清单 ──────────────────────────────
skill_step 1 "解析功能清单" "$WORKSPACE/project_info/<功能清单文件名>"

SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/parse_feature_list.py" \
  --feature_list "<工作区>/project_info/<功能清单文件名>" \
  --output "<工作区>/feature_list.json"

if [ $? -ne 0 ]; then
  skill_step_fail "功能清单解析失败"
  skill_end "fail" "Step 1 失败：parse_feature_list.py 执行错误"
  exit 1
fi

# 统计解析出的功能点数量
FEATURE_COUNT=$(python3 -c "import json; data=json.load(open('<工作区>/feature_list.json')); print(len(data))" 2>/dev/null || echo "未知")
skill_var "feature_count" "$FEATURE_COUNT 个功能点"
skill_log "功能清单解析完成" "共 $FEATURE_COUNT 个功能点"

# 保存中间结果
cp "<工作区>/feature_list.json" /tmp/skill-observer/ckpt_step1_feature_list.json 2>/dev/null || true
skill_checkpoint "feature-list" "/tmp/skill-observer/ckpt_step1_feature_list.json"

skill_step_ok "解析完成，共 $FEATURE_COUNT 个功能点"
# ─────────────────────────────────────────────────────
```

运行 `scripts/parse_feature_list.py` 解析 Markdown 文档：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/parse_feature_list.py" \
  --feature_list "<工作区>/project_info/<功能清单文件名>" \
  --output "<工作区>/feature_list.json"
```

解析结果结构：
```json
[
  {
    "module": "地址管理",
    "feature": "地址搜索",
    "description": "在地址列表页面，输入地址，点击搜索，页面显示搜索结果...",
    "db_tables": ["lsp_dev.lsp_address_suburb"],
    "tech_stack": "前端vue, 后端springboot",
    "related_api": "",
    "business_rules": "",
    "feature_key": "地址管理/地址搜索"
  }
]
```

---

### Step 2：对比已有用例，确定待设计功能点列表

```bash
# ── Step 2: 确定待设计功能点 ─────────────────────────
skill_step 2 "对比已有用例，确定待设计功能点" "<工作区>/feature_list.json"

SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/find_uncovered_features.py" \
  --feature_list "<工作区>/feature_list.json" \
  [--testcase "<工作区>/testcase/<文件名>"]

if [ $? -ne 0 ]; then
  skill_step_fail "未覆盖功能点分析失败"
  skill_end "fail" "Step 2 失败：find_uncovered_features.py 执行错误"
  exit 1
fi

UNCOVERED_COUNT=$(python3 -c "import json; data=json.load(open('<工作区>/features_to_design.json')); print(len(data))" 2>/dev/null || echo "未知")
skill_var "uncovered_feature_count" "$UNCOVERED_COUNT 个待设计功能点"
skill_log "未覆盖功能点分析完成" "共 $UNCOVERED_COUNT 个需要设计用例"

# 保存中间结果
cp "<工作区>/features_to_design.json" /tmp/skill-observer/ckpt_step2_features_to_design.json 2>/dev/null || true
skill_checkpoint "features-to-design" "/tmp/skill-observer/ckpt_step2_features_to_design.json"

skill_step_ok "确定 $UNCOVERED_COUNT 个待设计功能点"
# ─────────────────────────────────────────────────────
```

**若用户已指定目标功能点**，直接使用指定列表。

**若未指定**，运行 `scripts/find_uncovered_features.py`：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/find_uncovered_features.py" \
  --feature_list "<工作区>/feature_list.json" \
  [--testcase "<工作区>/testcase/<文件名>"]
```

该脚本会：
1. 读取全量功能点列表
2. 读取已有测试用例中的"所属模块"+"功能点"列（模糊匹配）
3. 找出没有对应用例的功能点
4. 输出 `<工作区>/features_to_design.json`

**向用户展示待设计功能点列表（含功能描述、关联表名）**，确认后继续。

---

### Step 3：查询关联数据库表结构

```bash
# ── Step 3: 查询数据库表结构 ──────────────────────────
skill_step 3 "查询关联数据库表结构" "<工作区>/db_info/db_config.json"

# 提取所有功能点涉及的表名
TABLE_KEYWORDS=$(python3 -c "
import json
data = json.load(open('<工作区>/features_to_design.json'))
tables = set()
for f in data:
    for t in f.get('db_tables', []):
        tables.add(t.split('.')[-1])
print(','.join(tables))
" 2>/dev/null || echo "")

skill_var "db_table_keywords" "$TABLE_KEYWORDS"
skill_log "待查询的表关键词" "$TABLE_KEYWORDS"

SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/query_db_schema.py" \
  --db_config "<工作区>/db_info/db_config.json" \
  --table_keywords "$TABLE_KEYWORDS" \
  --output "<工作区>/db_schemas.json"

if [ $? -ne 0 ]; then
  skill_step_fail "数据库表结构查询失败（可能是连接问题）"
  skill_log "警告" "DB 查询失败，子 Agent 将在 test_data 字段标注取样 SQL"
  # 非致命错误，继续执行
else
  SCHEMA_COUNT=$(python3 -c "import json; d=json.load(open('<工作区>/db_schemas.json')); print(len(d))" 2>/dev/null || echo "0")
  skill_var "db_schema_count" "$SCHEMA_COUNT 张表"

  cp "<工作区>/db_schemas.json" /tmp/skill-observer/ckpt_step3_db_schemas.json 2>/dev/null || true
  skill_checkpoint "db-schemas" "/tmp/skill-observer/ckpt_step3_db_schemas.json"
fi

skill_step_ok "数据库表结构查询完成"
# ─────────────────────────────────────────────────────
```

对每个待设计功能点，提取 `db_tables` 字段中的表名，运行：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/query_db_schema.py" \
  --db_config "<工作区>/db_info/db_config.json" \
  --table_keywords "<表名关键词，逗号分隔>" \
  --output "<工作区>/db_schemas.json"
```

将所有功能点的表结构汇总到同一个 `db_schemas.json`，供子 Agent 使用。

---

### Step 4：并行调度 3 个子 Agent 设计测试用例

```bash
# ── Step 4: 并行调度 3 个子 Agent ─────────────────────
skill_step 4 "并行调度 3 个子 Agent 设计测试用例" "将功能点平均分成 3 组"

TOTAL=$(python3 -c "import json; print(len(json.load(open('<工作区>/features_to_design.json'))))" 2>/dev/null || echo "0")
skill_var "total_features_to_design" "$TOTAL 个功能点"
skill_log "开始并行调度" "共 $TOTAL 个功能点，分配给 3 个子 Agent"
```

将待设计功能点平均分成 3 组，并行启动 3 个子 Agent。

**启动子 Agent 1 前标记：**
```bash
skill_agent_spawn "agent-testcase-batch1" "设计第 1 批功能点的测试用例（约占总量 1/3），输出到 cases_batch_1.json"
```

**启动子 Agent 2 前标记：**
```bash
skill_agent_spawn "agent-testcase-batch2" "设计第 2 批功能点的测试用例（约占总量 1/3），输出到 cases_batch_2.json"
```

**启动子 Agent 3 前标记：**
```bash
skill_agent_spawn "agent-testcase-batch3" "设计第 3 批功能点的测试用例（约占总量 1/3），输出到 cases_batch_3.json"
```

#### 子 Agent 工作流程

对每个分配到的功能点：

**4.1 理解功能上下文**
- 读取功能描述（用户故事）
- 读取 `<工作区>/project_info/` 下相关需求、业务文档
- 读取关联 API 文档（如有）
- 读取 `db_schemas.json` 中该功能涉及的表结构
- **确定用例版本号**：读取 `<工作区>/testcase/` 目录下已有用例文件（如有），按 `module + feature` 匹配当前功能点，读取"用例版本"列的最大值 `max_version`：
  - 若无匹配（全新功能）：本批所有用例 `case_version = 1`
  - 若有匹配（已有旧用例基础上新增或修改）：`case_version = max_version + 1`

**4.2 获取真实测试数据（非新增类必须执行）**

首先判断当前功能点的操作类型：

| 操作类型 | 典型关键词 | 测试数据来源 |
|----------|-----------|-------------|
| **新增类** | 新增、创建、添加、注册、上传 | 自行构造合法值（不依赖已有数据） |
| **非新增类** | 查询、搜索、修改、编辑、删除、详情、导出 | **必须从数据库随机取真实数据** |

**非新增类功能点**，在设计用例前先执行以下 SQL 随机采样，获取真实数据作为测试输入：

```sql
-- 查询/搜索类：随机取一条真实记录的关键字段（如名称、编号）
SELECT <name_field> FROM <db>.<table> WHERE is_deleted = 0 ORDER BY RAND() LIMIT 3;

-- 修改/删除/详情类：随机取已存在的主键 ID
SELECT id FROM <db>.<table> WHERE is_deleted = 0 ORDER BY RAND() LIMIT 3;
```

将查询到的**真实值**填入用例的 `test_data` 字段，并注明来源：
- 查询类示例：`搜索关键字：浦东（来源：DB随机取样 suburb_name）`
- 修改类示例：`id=12345（来源：DB随机取样）；修改字段：suburb_name="浦东新区"`
- 删除类示例：`id=12345（来源：DB随机取样，操作前确认记录存在）`

> ⚠️ 若无法连接数据库，在 `test_data` 字段注明取样 SQL：`需执行 SELECT id FROM <table> WHERE is_deleted=0 ORDER BY RAND() LIMIT 1 获取实际值`，不得填写编造的不存在的值。

---

**4.3 识别测试维度**

从功能描述出发，识别以下测试维度：

| 维度 | 说明 |
|------|------|
| 正常流程 | 输入合法数据，功能按预期执行 |
| 数据展示 | 页面展示的数据是否准确、完整 |
| 边界条件 | 输入值边界、空数据、最大值 |
| 异常流程 | 无数据、系统异常、网络超时 |
| 权限控制 | 不同角色看到的内容和可操作范围 |
| 业务规则 | 功能描述中的特定业务约束 |
| 交互体验 | UI 反馈、加载态、空状态 |
| 数据一致性 | 操作后数据库数据与页面数据一致 |

**4.4 使用多种设计方法生成用例**

参考 `references/design-methods.md`，综合运用：
- **场景法**：主成功场景 + 备选场景 + 异常场景（必用）
- **等价类划分**：每个输入字段的有效/无效输入类
- **边界值分析**：空、最小、最大、超界
- **判定表**：条件组合（适用于业务规则复杂的功能）
- **结对思维（Pairwise）**：多输入条件组合优化
- **错误猜测**：基于经验预测的常见问题点

**测试用例数量控制：每个功能点 1～10 个用例，追求覆盖率最大化。**

覆盖率目标：
- 正向用例 ≥ 40%（正常流程、数据准确展示）
- 负向用例 ≥ 30%（异常输入、空数据、错误提示）
- 边界用例 ≥ 20%（边界值、临界场景）
- 安全/权限用例 ≥ 10%（权限控制、越权访问）

**4.5 编写可操作的测试步骤**

每条步骤必须：
- 明确操作对象（哪个页面、哪个控件）
- 具体操作动作（点击、输入、选择、滑动）
- 预期中间状态（页面跳转、弹框出现）

**示例（地址搜索 - 有匹配结果）：**
```
步骤：
1. 登录系统，进入「地址管理」→「地址列表」页面
2. 在搜索框中输入"上海"
3. 点击「搜索」按钮（或按 Enter 键）
4. 等待页面加载完成

预期结果：
1. 页面搜索结果区域展示含"上海"的地址列表
2. 列表每条记录包含：地址名称、所属区域等字段
3. 页面顶部显示搜索结果总数（如"共找到 X 条记录"）
4. 搜索框保留输入的"上海"关键字

验证SQL（数据准确性）：
SELECT COUNT(*) FROM lsp_dev.lsp_address_suburb
WHERE suburb_name LIKE '%上海%' OR district LIKE '%上海%';
-- 期望值：≥1，且与页面显示总数一致
```

**4.6 输出格式**

每个子 Agent 将结果写入 `<工作区>/output/cases_batch_N.json`：

```json
[
  {
    "project": "系统/项目名（可空）",
    "module": "地址管理",
    "feature": "地址搜索",
    "test_item": "关键字模糊搜索准确性",
    "test_type": "正向",
    "title": "有效关键字模糊搜索返回匹配地址列表",
    "preconditions": "1. 已登录系统\n2. 数据库中存在包含'上海'的地址记录\n3. 进入地址列表页",
    "db_tables": "lsp_dev.lsp_address_suburb",
    "test_data": "搜索关键字：上海",
    "steps": "1. 进入地址列表页\n2. 搜索框输入'上海'\n3. 点击搜索\n4. 等待结果加载",
    "expected_result": "UI层：列表显示含'上海'记录，总数正确\n数据层：COUNT(*)=页面总数",
    "validation_sql": "SELECT COUNT(*) FROM lsp_dev.lsp_address_suburb WHERE suburb_name LIKE '%上海%';",
    "actual_result": "",
    "is_passed": "",
    "estimated_hours": "0.5",
    "execute_date": "",
    "test_progress": "",
    "case_type": "功能测试",
    "priority": "P0",
    "is_regression": "是",
    "is_blocker": "是",
    "requirement_id": "",
    "api_url": "/api/address/search",
    "bug_count": "0",
    "bug_unresolved": "0",
    "case_version": "1"
  }
]
```

**子 Agent 完成后，在主流程中记录结果：**

```bash
# 子 Agent 1 完成后
BATCH1_COUNT=$(python3 -c "import json; print(len(json.load(open('<工作区>/output/cases_batch_1.json'))))" 2>/dev/null || echo "0")
skill_agent_done "agent-testcase-batch1" "ok" "生成 $BATCH1_COUNT 条用例"
skill_var "batch1_case_count" "$BATCH1_COUNT"

# 子 Agent 2 完成后
BATCH2_COUNT=$(python3 -c "import json; print(len(json.load(open('<工作区>/output/cases_batch_2.json'))))" 2>/dev/null || echo "0")
skill_agent_done "agent-testcase-batch2" "ok" "生成 $BATCH2_COUNT 条用例"
skill_var "batch2_case_count" "$BATCH2_COUNT"

# 子 Agent 3 完成后
BATCH3_COUNT=$(python3 -c "import json; print(len(json.load(open('<工作区>/output/cases_batch_3.json'))))" 2>/dev/null || echo "0")
skill_agent_done "agent-testcase-batch3" "ok" "生成 $BATCH3_COUNT 条用例"
skill_var "batch3_case_count" "$BATCH3_COUNT"

TOTAL_CASES=$((BATCH1_COUNT + BATCH2_COUNT + BATCH3_COUNT))
skill_var "total_cases_generated" "$TOTAL_CASES 条测试用例"
skill_log "3 个子 Agent 全部完成" "总用例数：$TOTAL_CASES"

# 保存中间结果（checkpoint）
cat "<工作区>/output/cases_batch_1.json" "<工作区>/output/cases_batch_2.json" "<工作区>/output/cases_batch_3.json" \
  > /tmp/skill-observer/ckpt_step4_all_cases.json 2>/dev/null || true
skill_checkpoint "all-cases-json" "/tmp/skill-observer/ckpt_step4_all_cases.json"

skill_step_ok "3 个子 Agent 完成，共生成 $TOTAL_CASES 条用例"
# ─────────────────────────────────────────────────────
```

---

### Step 5：汇总并导出 Excel

```bash
# ── Step 5: 导出 Excel ────────────────────────────────
skill_step 5 "汇总并导出 Excel" "<工作区>/output/"

SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/export_excel.py" \
  --workspace "<工作区路径>" \
  --type functional

if [ $? -ne 0 ]; then
  skill_step_fail "Excel 导出失败"
  skill_end "fail" "Step 5 失败：export_excel.py 执行错误"
  exit 1
fi

# 获取输出文件路径
OUTPUT_FILE=$(ls -t "<工作区>/output/"functional_testcases_*.xlsx 2>/dev/null | head -1)
skill_var "output_excel_path" "$OUTPUT_FILE"
skill_log "Excel 文件已生成" "$OUTPUT_FILE"

# 保存 checkpoint
skill_checkpoint "output-excel" "$OUTPUT_FILE"

skill_step_ok "Excel 导出成功：$OUTPUT_FILE"
# ─────────────────────────────────────────────────────
```

运行 `scripts/export_excel.py` 将所有批次结果合并导出：

```bash
# Linux / macOS / WSL
SKILL_DIR="$HOME/.claude/skills/testcase-design-functional"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/export_excel.py" \
  --workspace "<工作区路径>" \
  --type functional
```

输出：`<工作区>/output/functional_testcases_YYYYMMDD_HHMMSS.xlsx`

Excel 格式：
- **Sheet 1「功能测试用例」**：标准17列，按模块+功能点分组，颜色区分用例类型
- **Sheet 2「功能点覆盖统计」**：功能点 × 覆盖维度矩阵（显示哪些维度已覆盖）
- **Sheet 3「覆盖率汇总」**：正向/负向/边界/安全覆盖率统计

---

### Step 6：汇报结果

```bash
# ── Step 6: 汇报结果 ──────────────────────────────────
skill_step 6 "汇报结果" "生成执行摘要"

skill_var "workspace_path" "$WORKSPACE"
skill_var "feature_count_total" "$FEATURE_COUNT"
skill_var "uncovered_feature_count" "$UNCOVERED_COUNT"
skill_var "total_cases_generated" "$TOTAL_CASES"
skill_var "output_excel_path" "$OUTPUT_FILE"

skill_log "技能执行完成" "输出文件：$OUTPUT_FILE"
skill_step_ok "结果汇报完成"
# ─────────────────────────────────────────────────────
```

向用户展示：
- 工作区路径
- 已解析功能点数量（含模块分组）
- 新设计用例数量 vs 已有用例数量
- 覆盖率分布（正向/负向/边界/安全）
- 未能查到数据库表结构的功能点（提示补充）
- 输出 Excel 文件路径

---

### 技能结束（最后执行）

```bash
# ── 结束 & 生成观测报告 ───────────────────────────────
skill_end "ok" "功能测试用例设计完成：共 $TOTAL_CASES 条用例，输出至 $OUTPUT_FILE"

# 自动生成本次运行的 HTML 观测报告
LATEST_LOG=$(ls -t /tmp/skill-observer/testcase-design-functional_*.jsonl 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
  python3 ~/skill-observer/scripts/report.py "$LATEST_LOG"
  echo "📊 观测报告路径：${LATEST_LOG%.jsonl}.html"
else
  echo "⚠️  未找到观测日志文件，请确认 skill-observer 已正确安装"
fi
# ─────────────────────────────────────────────────────
```

---

## 参考文档

- **功能测试设计方法**：`references/design-methods.md`
- **标准表头定义**：`references/testcase-headers.md`
- **数据库查询代码**：`scripts/query_db_schema.py`
- **表头模板示例**：`assets/testcase_header_template.md`
- **观测实时监控**：`tail -f /tmp/skill-observer/testcase-design-functional_*.jsonl | python3 ~/skill-observer/scripts/tail_viewer.py`
- **观测报告生成**：`python3 ~/skill-observer/scripts/report.py $(ls -t /tmp/skill-observer/testcase-design-functional_*.jsonl | head -1)`
