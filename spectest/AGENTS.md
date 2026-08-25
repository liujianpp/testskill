# OpenSpec Agent 规范

**版本**: v2.0
**最后更新**: 2026年3月13日
**维护者**: 指挥官

---

## 🎯 全局交互规则（最高优先级）

### 基本交互规范

- **称呼**：每次回复时都必须称呼用户为"**指挥官**"
- **语言**：除技术关键字、专有名词、代码、命令外，**所有解释和说明都使用中文**
- **语气**：保持专业、高效、军旅风格，体现执行力

### 执行原则

1. **理解优先**：接到任务后，先明确理解需求再行动
2. **主动确认**：遇到模糊需求时，使用MECE方法论澄清问题
   - **完全穷尽**：列出所有可能的需求维度（功能、数据、时间、质量、约束）
   - **相互独立**：将复杂需求拆解为不重叠的子任务
   - **确认要点**：优先确认关键假设和决策点
   - **示例提问**：
     - "这个任务是否涉及以下方面：[A]数据转换 [B]报告生成 [C]系统配置？"
     - "优先级排序是：[1]必须完成 [2]重要但可延后 [3]可选？"
3. **透明沟通**：清晰说明行动计划和进度
4. **规范执行**：严格遵守本文档所有规范
5. **保持整洁**：项目文件组织规范（详见下方"文件组织规范"）

---

## 📁 文件组织规范（保持整洁原则）

### 核心要求

**所有执行内容必须基于OpenSpec proposal进行**，严禁随意在项目根目录创建文件。

### 基本原则

- ✅ 任何功能性任务都必须先创建proposal
- ✅ 所有生成的脚本、数据、报告文件都必须放在对应的proposal目录
- ✅ 文件要分门别类组织，不能堆在根目录
- ⚠️ 只有项目配置文件可以放在根目录

### Proposal目录结构标准

每个proposal必须按以下结构组织。

#### Change-ID 编号规则

**格式要求**：

- **格式**: 四位数字 + 原标题（用连字符连接）
- **示例**: `0001-convert-customer-service-docs`
- **示例**: `0002-generate-value-report`
- **编号范围**: 0001-9999
- **标题规则**: 使用小写字母、连字符、数字，简短描述任务内容
- **唯一性**: 每个change-id必须唯一，不得重复
- **持久性**: 转入archive时保持原ID中的编号，按archive要求修改文件名，比如增加日期前缀。

**编号分配流程**：

1. 查询现有proposal的最大编号
2. 分配下一个顺序编号（四位数字）
3. 根据任务内容生成简短标题
4. 组合为最终ID：`编号-标题`
5. 创建proposal目录

**编号查询方法**：

```bash
# 查看所有活跃的proposal（提取编号）
ls openspec/changes/ | grep -oP '^\d{4}' | sort -n | tail -1

# 查看最大完整ID
ls openspec/changes/ | grep -oP '^\d{4}-' | sed 's/-//' | sort -n | tail -1
```

#### 标准目录结构

```
openspec/changes/0001-convert-docs/
├── proposal.md              # 提案说明（必须）
├── tasks.md                 # 任务清单（必须）
├── design.md                # 技术设计（可选）
├── specs/                   # 规格变更（必须）
│   └── [capability]/
│       └── spec.md
├── scripts/                 # 执行脚本（如有）
│   ├── setup/              # 初始化脚本
│   ├── convert/            # 转换脚本
│   ├── analyze/            # 分析脚本
│   └── report/             # 报告生成脚本
├── data/                   # 数据文件（如有）
│   ├── input/              # 输入数据
│   ├── output/             # 输出数据
│   └── cache/              # 临时缓存
├── logs/                   # 日志文件（如有）
├── tests/                  # 测试文件（如有）
└── README.md               # 说明文档（如有）
```

### 文件放置规则

#### ✅ 必须放在proposal目录的文件：

- **脚本文件**：`.py`, `.js`, `.sh`, `.bat` 等
- **数据文件**：`.json`, `.csv`, `.xlsx` 等
- **报告文件**：`.md`, `.txt`, `.html` 等
- **图片文件**：`.png`, `.jpg`, `.svg` 等
- **临时文件**：中间结果、缓存文件等
- **配置文件**：脚本专用的配置

#### ⚠️ 可以放在项目根目录的文件：

- **项目配置**：`CLAUDE.md`, `AGENTS.md` 等
- **项目文档**：`README.md`, `CHANGELOG.md` 等
- **版本控制**：`.gitignore`, `.gitattributes` 等
- **依赖文件**：`package.json`, `requirements.txt` 等
- **OpenSpec核心**：`openspec/specs/` 下的正式规格

### 文件命名规范

- 脚本文件：`[action]_[target].py` (如: `convert_docs.py`, `generate_report.py`)
- 数据文件：`[source]_[type].json` (如: `customer_analysis.json`)
- 报告文件：`[type]_report.md` (如: `conversion_summary.md`)
- 日志文件：`[date]_[action].log` (如: `20260313_conversion.log`)

### 示例对比

❌ **不规范的文件放置**：

```
project-root/
├── convert_docs.py          # 错！脚本在根目录
├── data.json                # 错！数据文件在根目录
├── report.md                # 错！报告文件在根目录
└── openspec/changes/convert-docs/
    └── proposal.md
```

✅ **规范的文件放置**：

```
project-root/
├── openspec/changes/convert-docs/
│   ├── proposal.md
│   ├── scripts/
│   │   └── convert_docs.py
│   ├── data/
│   │   ├── input/
│   │   │   └── source_data.json
│   │   └── output/
│   │       └── converted_data.json
│   └── reports/
│       └── conversion_summary.md
└── CLAUDE.md
```

### 执行前的自检清单

创建文件前，必须确认：

- [ ] 这个文件是基于某个proposal创建的吗？
- [ ] 这个文件应该放在proposal的哪个子目录？
- [ ] 文件命名符合规范吗？
- [ ] 是否需要在proposal.md或tasks.md中记录这个文件？

---

## 🔄 工作流程规范

### 阶段1：需求理解

- 明确用户意图和期望输出
- 判断是否需要创建proposal
- 如需proposal，先获得用户批准

### 阶段2：Proposal创建

#### 步骤2.1：分配Change-ID

- 查询现有最大编号（使用bash命令或脚本）
- 分配下一个顺序编号（三位数字格式）
- 立即创建proposal目录，避免冲突

#### 步骤2.2：创建Proposal文件

- 使用OpenSpec标准格式创建proposal.md
- 包含：proposal.md, tasks.md, specs/
- 明确输出位置和文件组织

#### 步骤2.3：验证ID唯一性

- 确认新建的ID未与现有或archived的ID冲突
- 在proposal.md中记录ID分配信息

### 阶段3：执行实施

- 严格按照tasks.md执行
- 所有脚本放在 `scripts/` 目录
- 所有数据放在 `data/` 目录
- 所有报告放在 `reports/` 目录（或docs/如果是对外交付物）
- 实时记录进度和遇到的问题

### 阶段4：完成归档

- 验证所有文件放置正确
- 更新tasks.md的完成状态
- 生成执行总结
- 确认用户满意后再归档

---

## 🔍 违规检测与纠正

### 常见违规情形

1. ❌ 在根目录创建脚本文件
2. ❌ 数据文件散落在各处
3. ❌ 文件堆在proposal根目录不分类
4. ❌ 未按规范命名文件
5. ❌ 执行任务前未创建proposal

### 发现违规时的处理

1. **立即停止**：停止当前操作
2. **识别问题**：明确违反了哪条规范
3. **主动纠正**：将文件移动到正确位置
4. **更新文档**：在proposal.md中记录变更
5. **继续执行**：确认无误后继续工作

---

## 📚 规范使用指南

### 何时使用OpenSpec流程

✅ **必须使用**：

- 创建新功能或服务
- 进行架构性变更
- 处理大量数据或文件（>10个文件）
- 生成复杂报告或分析
- 多步骤的综合性任务
- 涉及多个文件的操作

❌ **无需使用**：

- 简单的文件查看或读取
- 单行代码修改
- 文档格式调整
- 问题诊断和调试
- 临时性测试

### 快速参考

#### Change-ID编号管理

**使用专用工具**（推荐）：

```bash
# 查看所有proposal
python3 openspec/changes/manage_id.py list

# 获取下一个可用ID
python3 openspec/changes/manage_id.py next

# 创建新proposal目录
python3 openspec/changes/manage_id.py create

# 创建指定ID的proposal
python3 openspec/changes/manage_id.py create --id 5

# 检查ID是否可用
python3 openspec/changes/manage_id.py check --id 5
```

**手动查询方法**：

```bash
# 查询当前最大编号
ls openspec/changes/ | grep -oP '^\d{4}' | sort -n | tail -1

# 验证ID唯一性（包括archived）
grep -r "^0001-" openspec/changes/ openspec/changes/archive/
```

#### 其他参考

- **创建proposal**：参考 `openspec/changes/` 下的现有示例
- **规范格式**：严格按照本文档执行
- **文件组织**：遵循"文件组织规范"章节
- **遇到问题**：主动向指挥官确认

---

## 📝 编号规则说明

### 新建Proposal（执行本规范后）

所有新建的proposal必须使用**四位数字+标题**：

- 格式：`0001-任务简短描述`
- 示例：`0001-convert-customer-service-docs`
- 示例：`0002-generate-value-report`
- 标题规则：小写字母、连字符、数字，简洁明了
- 使用 `manage_id.py` 工具辅助创建

### 现有Proposal（过渡期处理）

对于已存在的描述性名称proposal（如 `convert-docs`）：

- ✅ 继续保持现有名称
- ✅ 可以继续使用和更新
- ⚠️ 建议在proposal.md中记录实际编号（如有）

### 归档规则

无论proposal使用何种命名方式：

- 归档时保持原名称不变
- 归档位置：`openspec/changes/archive/`
- 永久保留，不重复使用编号或名称

---

## 🎖️ 执行力标准

### 优秀执行的特征

- ✅ 严格遵守所有规范
- ✅ 文件组织清晰整洁
- ✅ 沟通主动透明
- ✅ 问题及时发现和纠正
- ✅ 交付物质量高

### 需要改进的信号

- ⚠️ 文件散落各处
- ⚠️ 未创建proposal就执行
- ⚠️ 沟通不及时或不清晰
- ⚠️ 违反规范未主动纠正

---

## 📋 快速检查清单

### 开始任务前

- [ ] 理解了用户需求
- [ ] 判断是否需要proposal
- [ ] 如需proposal，已获得批准
- [ ] 明确了输出位置

### 创建文件时

- [ ] 文件基于proposal创建
- [ ] 放在正确的子目录
- [ ] 命名符合规范
- [ ] 已在tasks.md中记录

### 完成任务后

- [ ] 所有文件放置正确
- [ ] tasks.md已更新
- [ ] 生成执行总结
- [ ] 用户确认满意

---

**更新历史**：

- v2.0 (2026-03-13): 新增"文件组织规范"，强化项目整洁要求
- v1.0: 初始版本

---

<!-- OPENSPEC:START -->

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:

- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:

- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->
