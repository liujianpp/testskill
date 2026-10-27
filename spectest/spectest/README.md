# SpecTest - 统一测试设计工作流

**版本：** V1.1
**创建日期：** 2026-03-19
**最后更新：** 2026-03-24

---

## 📖 简介

SpecTest 是一个统一的测试设计工作流工具，整合了工作流管理能力和智能设计能力，提供从需求分析到归档的完整测试用例管理流程。

### 核心特性

- ✅ **统一的工作流**：9 步完成从需求到归档的完整流程（含可选测试计划）
- ✅ **灵活的输入源**：支持测试点、API 文档、功能清单；需求文档可直接读取 PDF/Word
- ✅ **智能的设计能力**：自动生成测试点和用例
- ✅ **增强的 Excel 输出**：3 个 Sheet（用例、覆盖矩阵、统计汇总）
- ✅ **多格式支持**：Excel（彩色标记）+ XMind 思维导图
- ✅ **字段映射**：支持新旧字段名自动识别
- ✅ **质量控制闭环**：可选的评审和报告
- ✅ **便捷同步**：一键同步脚本，快速更新技能

---

## 🚀 快速开始

### 安装技能

**方法 1：使用同步脚本（推荐）**

运行提供的同步脚本自动同步所有 SpecTest 技能：

```bash
# Linux/macOS/WSL
bash E:/AI/spectest/spectest/sync_skills.sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File E:\AI\spectest\spectest\sync_skills.ps1
```

**方法 2：手动复制**

```bash
# Linux/macOS
cp -r E:/AI/spectest/spectest ~/.claude/skills/

# Windows PowerShell
Copy-Item -Recurse E:\AI\spectest\spectest $env:USERPROFILE\.claude\skills\
```

**方法 3：逐个技能复制（仅复制技能目录）**

```bash
# 只复制 9 个 SpecTest 技能（不包含 changes/）
for skill in E:/AI/spectest/spectest/spectest-*/; do
  cp -rf "$skill" ~/.claude/skills/
done
```

⚠️ **重要提示**：

- 开发目录：`E:/AI/spectest/spectest/spectest-*/`（源代码）
- 使用目录：`C:/Users/admin/.claude/skills/spectest-*/`（Claude Code 调用位置）
- **每次修改脚本后，需要重新同步到使用目录**

### 依赖安装

部分技能需要 Python 依赖，使用 `uv` 管理：

```bash
# Excel 生成（spectest-generate）
pip install openpyxl pandas

# 数据库查询（智能生成模式）
pip install pymysql

# API 请求
pip install anthropic
```

### 创建第一个测试工作

```bash
# 1. 创建变更目录
/spectest-new 地址管理测试

# 2. 智能需求分析
/spectest-analysis

# 3. 自动生成测试点
/spectest-points 自动

# 4. 生成测试用例
/spectest-generate from-specs --format Excel,XMind

# 5. 评审用例（可选）
/spectest-review artifacts/地址管理_testcases.xlsx

# 6. 生成执行报告（执行测试后）
/spectest-report

# 7. 归档
/spectest-archive
```

---

## 📚 技能列表

### 核心技能（8个）

| 技能       | 命令                            | 功能                 |
| ---------- | ------------------------------- | -------------------- |
| 创建变更   | `/spectest-new <名称>`        | 创建变更目录并初始化 |
| 需求分析   | `/spectest-analysis`          | 智能提取功能点和 API |
| 测试计划   | `/spectest-plan`              | 生成 test-plan.md（可选） |
| 生成测试点 | `/spectest-points 自动/手动`  | 按设计方法推导测试点 |
| 生成用例   | `/spectest-generate from-xxx` | 先出 design.md 再生成用例 |
| 评审用例   | `/spectest-review <文件>`     | 评审用例质量和覆盖率 |
| 生成报告   | `/spectest-report`            | 生成执行报告         |
| 归档       | `/spectest-archive`           | 归档完成的变更       |

### 辅助技能（2个）

| 技能     | 命令                         | 功能                       |
| -------- | ---------------------------- | -------------------------- |
| 格式转换 | `/spectest-convert <文件>` | 转换不同表头格式到标准25列 |
| 修复用例 | `/spectest-fix <问题>`     | 根据评审意见修复用例       |

---

## 🔄 完整工作流

```
1. spectest-new     → 创建变更目录
        ↓
2. spectest-analysis → 智能需求分析（可直接读 PDF/Word，提取功能点、API）
        ↓
3. spectest-plan    → 测试计划 test-plan.md（可选）
        ↓
4. spectest-points   → 生成测试点（按设计方法推导，自动/手动）
        ↓
5. spectest-generate → 生成测试用例（先出 design.md，3种输入源）
        ↓
6. spectest-review   → 评审用例（可选）
        ↓
7. spectest-fix      → 修复用例（可选）
        ↓
8. spectest-report   → 生成执行报告
        ↓
9. spectest-archive  → 归档变更
```

---

## 📂 目录结构

```
spectest/
├── changes/                 # 测试变更目录
│   ├── <变更名>/
│   │   ├── proposal.md              # 测试提案
│   │   ├── requirements-analysis.md # 需求分析
│   │   ├── specs/                   # 测试点文件
│   │   ├── artifacts/               # 产物（Excel、XMind）
│   │   ├── project_info/            # 项目资料
│   │   ├── db_info/                 # 数据库配置
│   │   ├── review/                  # 评审资料
│   │   └── report.md                # 执行报告
│   └── archive/                    # 已归档的变更
├── spectest-new/            # 创建变更技能
├── spectest-analysis/       # 需求分析技能
├── spectest-points/         # 测试点生成技能
├── spectest-generate/       # 用例生成技能
├── spectest-review/         # 用例评审技能
├── spectest-report/         # 报告生成技能
├── spectest-archive/        # 归档技能
├── spectest-convert/        # 格式转换技能
└── spectest-fix/            # 用例修复技能
```

---

## 💡 使用场景

### 场景 1：完整工作流（智能模式）

从零开始设计测试用例，有完整的需求文档和 API 文档。

```bash
/spectest-new 地址管理测试
/spectest-analysis
/spectest-points 自动
/spectest-generate from-specs --format Excel,XMind
/spectest-review artifacts/地址管理_testcases.xlsx
/spectest-report
/spectest-archive
```

### 场景 2：快速生成用例（跳过工作流）

只有 API 文档或功能清单，快速生成用例。

```bash
# 从 API 文档生成
/spectest-generate from-api \
  --doc ~/Downloads/api.json \
  --output ~/my_testcases.xlsx

# 从功能清单生成
/spectest-generate from-feature \
  --doc ~/Downloads/feature_list.md \
  --output ~/my_testcases.xlsx
```

### 场景 3：格式转换（独立使用）

收到其他团队的测试用例，表头格式不一致。

```bash
/spectest-convert ~/Downloads/其他团队_用例.xlsx
# 输出：其他团队_用例_标准格式.xlsx（25列标准格式）
```

---

## 🎯 测试用例格式

### Excel 输出（3 个 Sheet）

**Sheet 1: 测试用例**

- 标准 25 列格式
- 按测试类型彩色标记：
  - 正向测试：白色背景
  - 负向测试：淡红色背景
  - 边界测试：淡黄色背景
  - 安全测试：淡绿色背景

**Sheet 2: 功能点覆盖矩阵**

- 8 个覆盖维度统计：
  - 正常流程、数据展示、边界条件
  - 异常流程、空数据、权限控制
  - 业务规则、数据一致性
- 每个功能点的覆盖情况

**Sheet 3: 覆盖率汇总**

- 总用例数统计
- 按测试类型统计（正向/负向/边界/安全）
- 按优先级统计（P0/P1/P2）
- 覆盖率达标情况

### 标准 25 列格式

1. 系统/项目
2. 模块
3. 功能
4. 测试项
5. 用例标题
6. 前置条件
7. 涉及相关数据库表
8. 测试数据准备
9. 测试步骤
10. 预期结果
11. 验证SQL
12. 实际结果
13. 是否通过
14. 预估工时
15. 执行时间
16. 测试进度
17. 用例类型（API测试/功能测试）
18. 用例优先级（P0/P1/P2）
19. 是否回归用例
20. 是否阻塞上线
21. 关联需求ID
22. API URL
23. BUG数
24. BUG未解决数
25. 用例版本

### 覆盖率目标

- 正向测试 ≥ 40%
- 负向测试 ≥ 30%
- 边界测试 ≥ 20%
- 安全测试 ≥ 10%

---

## 🔧 高级功能

### 多 Sheet Excel 生成

```bash
/spectest-generate from-specs --format Excel
```

自动生成包含 3 个 Sheet 的 Excel 文件：

1. **测试用例 Sheet**：所有测试用例详细数据，彩色标记
2. **功能点覆盖矩阵 Sheet**：8 维度覆盖情况
3. **覆盖率汇总 Sheet**：
   - 总用例数统计
   - 按测试类型统计（正向/负向/边界/安全）
   - 按优先级统计（P0/P1/P2）
   - 覆盖率达标检查

**彩色标记说明：**

- 🟩 正向测试：白色 (#FFFFFF)
- 🟥 负向测试：淡红色 (#FCE4D6)
- 🟨 边界测试：淡黄色 (#FFF2CC)
- 🟦 安全测试：淡绿色 (#E2EFDA)

### 字段映射和兼容

支持新旧字段名自动映射：

| 新字段名        | 旧字段名 | 说明     |
| --------------- | -------- | -------- |
| title           | name     | 用例标题 |
| test_type       | type     | 测试类型 |
| expected_result | expected | 预期结果 |

自动识别两种格式，无需手动转换。

### 自动生成测试点

```bash
/spectest-points 自动
```

内部调用 testcase 智能设计能力：

- 查询数据库表结构
- 识别测试维度
- 生成功能测试点和 API 测试点
- 自动生成验证 SQL

### 智能设计用例

```bash
# 从 API 文档智能生成
/spectest-generate from-api --doc api_docs.json

# 从功能清单智能生成
/spectest-generate from-feature --doc feature_list.md
```

内部调用 testcase 智能：

- 并行调度 3 个子 Agent
- 查询数据库获取真实测试数据
- 应用测试设计方法（等价类、边界值等）
- 确保覆盖率目标

---

## 🔄 技能同步

### 为什么需要同步？

SpecTest 技能存在两个位置：

| 位置               | 用途             | 路径                                          |
| ------------------ | ---------------- | --------------------------------------------- |
| **开发位置** | 编辑和开发技能   | `E:/AI/spectest/spectest/spectest-*/`       |
| **使用位置** | Claude Code 调用 | `C:/Users/admin/.claude/skills/spectest-*/` |

**每次修改脚本后，必须同步到使用位置才能生效！**

### 同步方法

#### 使用同步脚本（推荐）

项目提供了两个同步脚本：

**Bash 版本**：[sync_skills.sh](E:/AI/spectest/spectest/sync_skills.sh)

```bash
bash E:/AI/spectest/spectest/sync_skills.sh
```

**PowerShell 版本**：[sync_skills.ps1](E:/AI/spectest/spectest/sync_skills.ps1)

```powershell
powershell -ExecutionPolicy Bypass -File E:\AI\spectest\spectest\sync_skills.ps1
```

**脚本特性：**

- ✅ 自动同步所有 SpecTest 技能
- ✅ 显示同步进度和统计信息
- ✅ 彩色输出（PowerShell 版本）
- ✅ 验证同步结果

#### 手动同步

修改脚本后，手动执行：

```bash
# 同步单个技能的脚本
cp E:/AI/spectest/spectest/spectest-generate/scripts/generate_excel.py \
   C:/Users/admin/.claude/skills/spectest-generate/scripts/

# 同步所有技能
for skill in E:/AI/spectest/spectest/spectest-*/; do
  name=$(basename "$skill")
  [ -d "$skill/scripts" ] && cp -rf "$skill/scripts/"* "C:/Users/admin/.claude/skills/$name/scripts/"
done
```

### 验证同步

检查关键文件是否同步成功：

```bash
# 检查脚本文件大小和时间
ls -lh C:/Users/admin/.claude/skills/spectest-generate/scripts/

# 对比文件是否一致
diff E:/AI/spectest/spectest/spectest-generate/scripts/generate_excel.py \
     C:/Users/admin/.claude/skills/spectest-generate/scripts/generate_excel.py

# 快速验证所有技能
for skill in analysis archive convert fix generate new points report review; do
  dir="C:/Users/admin/.claude/skills/spectest-$skill"
  if [ -d "$dir" ]; then
    echo "✓ spectest-$skill"
    [ -f "$dir/SKILL.md" ] && echo "  - SKILL.md ✓"
    [ -d "$dir/scripts" ] && echo "  - scripts/ ✓"
  fi
done
```

### 最佳实践

1. **每次修改脚本后立即同步**
2. **定期运行完整同步脚本**（如每周一次）
3. **修改前后对比文件大小和时间戳**
4. **重要修改后测试技能是否生效**

---

## 📝 更新日志

### V1.2 (2026-10-27)

**整合 OpenTest 1.0.5 新版能力：**

- ➕ 新增 `spectest-plan` 技能：测试计划 test-plan.md（范围/策略/环境/人力人天/进度/进出标准/风险/交付物），流程变更为 9 步（plan 可选）
- 🔧 `spectest-generate` from-specs：先出用例设计方案 `design.md`（覆盖矩阵 + 用例提纲，可审可改）再展开导出
- 🔧 `spectest-points`：按等价类/边界值/场景法/错误推测推导并标注设计方法；联动 test-plan 范围与优先级
- 🔧 `spectest-analysis`：新增 `extract_doc.py` 直接抽取 PDF/Word(.docx)/MD/TXT 需求正文（依赖 pypdf、python-docx）
- 🐛 修复 pyproject.toml 声明 hatchling 但无包可建导致 `uv sync`/`uv run` 失败的既有问题（改为 uv 虚拟项目）
- 📄 testflow（SKILL.md / workflow-map / user-guide）与各级 CLAUDE.md 流程描述同步为 9 步

### V1.1 (2026-03-24)

**新增功能：**

- ✨ Excel 输出支持 3 个 Sheet（测试用例、覆盖矩阵、统计汇总）
- ✨ 测试用例按类型彩色标记（正向/负向/边界/安全）
- ✨ 覆盖率汇总新增"按优先级统计"（P0/P1/P2）
- ✨ 支持中文字段名（title、test_type、expected_result 等）
- ✨ 字段映射功能（自动识别新旧字段名）

**优化改进：**

- 🔧 修复 Excel 生成只包含表头的 Bug
- 🔧 修复 XMind 生成不支持包装格式的 Bug
- 🔧 修复测试点解析字段内容丢失的 Bug
- 🔧 优化测试点解析逻辑（独立处理各字段）
- 🔧 同步脚本支持彩色输出和详细统计

**工具增强：**

- 🛠️ 新增 `sync_skills.sh` Bash 同步脚本
- 🛠️ 新增 `sync_skills.ps1` PowerShell 同步脚本
- 🛠️ 更新 README.md 添加同步指南和最佳实践

### V1.0 (2026-03-19)

**初始版本：**

- 📋 8 步完整工作流
- 🔧 9 个核心技能
- 📊 标准 25 列 Excel + XMind 输出

---

## 📖 更多文档

- [整合方案 V2](../整合文档/OpenTest与Testcase整合方案_V2.md)
- [实施完成报告](../整合文档/整合实施完成报告.md)
- [技能文档](./各技能目录/SKILL.md)

---

## 🐛 已知问题 & 解决方案

### 问题 1：Excel 文件只包含表头，没有数据

**现象**：生成的 Excel 文件只有 1 行（表头），测试用例数据丢失。

**原因**：`generate_excel.py` 创建了新的空 Workbook，但 `generate_excel()` 函数保存了自己的 Workbook。

**解决**：修改 `generate_excel()` 返回 Workbook 对象，在 `run()` 中统一保存。

**状态**：✅ 已修复（V1.1）

### 问题 2：XMind 生成失败

**现象**：`/spectest-generate from-specs --format XMind` 没有生成 XMind 文件。

**原因**：脚本不支持包装格式 `{"testcases": [...]}`，只支持直接的数组格式。

**解决**：添加格式检测和字段映射功能。

**状态**：✅ 已修复（V1.1）

### 问题 3：测试用例字段内容为空

**现象**：测试数据准备、测试步骤、预期结果、前置条件等字段没有内容。

**原因**：

1. 使用 if-elif 结构处理字段，只有最后一个字段被保存
2. 遇到 `**优先级**：` 时重置 `current_field`，导致内容丢失

**解决**：

1. 改为独立的 if 语句处理每个字段
2. 维护独立的内容列表，不重置 `current_field`

**状态**：✅ 已修复（V1.1）

### 问题 4：技能脚本未同步

**现象**：修改了脚本但 `/spectest-generate` 命令还是用旧版本。

**原因**：开发目录和使用目录是独立的副本，修改后需要手动同步。

**解决**：

1. 使用 `sync_skills.sh` 或 `sync_skills.ps1` 同步脚本
2. 每次修改后立即同步

**状态**：✅ 已提供同步工具（V1.1）

---

## ⚠️ 注意事项

1. **渐进迁移**：新旧技能并存，可逐步适应
3. **数据库配置**：智能生成模式需要配置 `db_info/db_config.json`
4. **依赖安装**：首次使用需安装 Python 依赖

---

## 📎 快速参考

### 常用命令

| 任务       | 命令                                             |
| ---------- | ------------------------------------------------ |
| 同步技能   | `bash E:/AI/spectest/spectest/sync_skills.sh`  |
| 创建新测试 | `/spectest-new <名称>`                         |
| 需求分析   | `/spectest-analysis`                           |
| 生成测试点 | `/spectest-points 自动`                        |
| 生成 Excel | `/spectest-generate from-specs --format Excel` |
| 生成 XMind | `/spectest-generate from-specs --format XMind` |
| 评审用例   | `/spectest-review artifacts/<文件.xlsx>`       |
| 生成报告   | `/spectest-report`                             |
| 归档       | `/spectest-archive`                            |

### 文件路径速查

| 类型                   | 路径                                          |
| ---------------------- | --------------------------------------------- |
| 开发目录               | `E:/AI/spectest/spectest/spectest-*/`       |
| 使用目录               | `C:/Users/admin/.claude/skills/spectest-*/` |
| 同步脚本（Bash）       | `E:/AI/spectest/spectest/sync_skills.sh`    |
| 同步脚本（PowerShell） | `E:/AI/spectest/spectest/sync_skills.ps1`   |
| 文档                   | `E:/AI/spectest/spectest/README.md`         |

### Bug 速查

| 问题           | 检查项                    | 解决方法                         |
| -------------- | ------------------------- | -------------------------------- |
| Excel 只有表头 | Workbook 对象是否正确返回 | 重新同步 `generate_excel.py`   |
| XMind 生成失败 | 是否支持包装格式          | 重新同步 `generate_xmind.py`   |
| 字段内容为空   | 测试点解析逻辑            | 重新同步 `parse_testpoints.py` |
| 命令用旧版本   | 脚本是否同步              | 运行同步脚本                     |

---

**文档结束**
