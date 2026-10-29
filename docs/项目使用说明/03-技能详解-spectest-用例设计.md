# 03 · 技能详解：spectest（测试用例设计工作流，10 个技能）

> **一句话**：从需求文档出发，像老师傅一样按 9 步流程产出**规范的测试用例**，最终导出全工作区通用的**标准 25 列 Excel**（或 XMind 思维导图）。

[← 返回总导读](README.md) | 套件自带文档：[spectest/CLAUDE.md](../../spectest/CLAUDE.md)（25 列定义必读）

---

## 1. 套件全景

spectest 由 **10 个技能**组成：9 个流程步骤技能 + 1 个格式转换技能。每个都可**单独调用**，也可以按顺序串起来跑。

```
①new → ②analysis → ③plan(可选) → ④points → ⑤generate → ⑥review → ⑦fix → ⑧report → ⑨archive
                                                                  ＋ spectest-convert（格式转换，随时可用）
```

**状态都放在哪？** → **被测项目**的 `spectest/changes/<变更名>/` 目录（不是本仓库！）：

```
spectest/changes/<变更名>/
├── proposal.md          # ①立项提案（prd-review 的评审报告路径也附在这）
├── project_info/        # ②需求分析产物：requirements-analysis.md、feature_list.md、api_list.json
├── specs/               # ④测试点文件 *.md
├── artifacts/           # ⑤25 列用例 Excel、design.md 设计方案、⑧报告等
└── db_info/             # DB 断言配置（接口支线用）
```

## 2. 核心契约：25 列标准 Excel

所有用例都是**同一张 25 列表格**（Sheet 名「测试用例」），它是整个工作区的「通用货币」：

- 后续 UI 执行（testflow 3B）从它转出 8 列执行表；
- 小程序执行（3C）从它转出 mp_cases.xlsx；
- 资产分拣（promote_cases.py）按它的「是否回归用例」「API URL」列归类入库；
- 25 个列的准确定义见 [spectest/CLAUDE.md](../../spectest/CLAUDE.md)。

**覆盖率目标**（review 步骤按此检查）：正向 ≥40%、负向 ≥30%、边界 ≥20%、安全 ≥10%。

## 3. 十个技能逐个详解

### 3.1 spectest-new（第 1 步：新建测试变更）

| 项 | 说明 |
|----|------|
| 干什么 | 创建一次测试工作的目录 + 写立项提案 |
| 你提供 | 变更名（如 `order-v2`）+ 需求文档路径 |
| 产物 | `spectest/changes/<变更名>/` 目录骨架（proposal.md + specs/ artifacts/ project_info/ db_info/） |
| 话术 | 「/spectest-new 创建变更 order-v2，需求文档在 docs/PRD-订单.pdf」 |

### 3.2 spectest-analysis（第 2 步：智能需求分析）

| 项 | 说明 |
|----|------|
| 干什么 | 深读需求文档，拆解成「要测什么」的结构化清单 |
| 输入 | pdf/docx/md/txt 直接读（也支持 API 文档、功能清单） |
| 产物 | `requirements-analysis.md`（需求拆解）+ `project_info/feature_list.md`（功能点清单）+ `project_info/api_list.json`（API 接口清单） |
| 话术 | 「/spectest-analysis 分析当前变更的需求」 |

### 3.3 spectest-plan（第 3 步，可选：测试计划）

| 项 | 说明 |
|----|------|
| 干什么 | 生成正式测试计划：范围/策略/人天/进度 |
| 产物 | `test-plan.md` |
| 什么时候用 | 需要给领导/团队排期交计划时；快速测试可跳过 |
| 话术 | 「/spectest-plan 生成测试计划」 |

### 3.4 spectest-points（第 4 步：测试点推导）

| 项 | 说明 |
|----|------|
| 干什么 | 按**用例设计方法**（等价类 / 边界值 / 场景法 / 错误推测）推导「要测什么」的测试点 |
| 两种模式 | 自动生成（AI 智能设计）或手动编写（你写思路它整理） |
| 产物 | `specs/*.md` 测试点文件（第 5 步的原料） |
| 话术 | 「/spectest-points 按等价类和边界值推导登录模块测试点」 |

### 3.5 spectest-generate（第 5 步：生成用例）⭐ 核心

| 项 | 说明 |
|----|------|
| 干什么 | 先出**用例设计方案**（design.md：覆盖矩阵与提纲），再展开成完整用例并导出 |
| 三种输入源 | `from-specs`（从测试点展开，**最常用**）/ `from-api`（从 OpenAPI 文档智能设计）/ `from-feature`（从功能清单智能设计） |
| 产物 | `design.md` + **`artifacts/<变更名>_testcases.xlsx`（25 列）**，可选 XMind |
| 话术 | 「/spectest-generate from-specs 导出 Excel，顺便出一份 XMind」 |

> 关键机制：25 列中「API URL」列非空的行 = API 用例（留给接口支线）；其余 = UI/功能用例（进 UI 执行）。生成时就自动完成了分流标记。

### 3.6 spectest-review（第 6 步：用例评审）

| 项 | 说明 |
|----|------|
| 干什么 | 评审用例质量：覆盖率够不够、设计方法用没用对、有没有冗余/缺失 |
| 产物 | 评审报告（问题清单 + 覆盖率统计） |
| 话术 | 「/spectest-review 评审刚生成的用例」 |

### 3.7 spectest-fix（第 7 步：修复用例）

| 项 | 说明 |
|----|------|
| 干什么 | 按第 6 步的评审意见自动完善用例（补缺失场景、修格式） |
| 产物 | 修正后的 25 列 Excel |
| 话术 | 「/spectest-fix 按评审意见修复用例」 |

### 3.8 spectest-report（第 8 步：执行报告）

| 项 | 说明 |
|----|------|
| 干什么 | 汇总测试执行情况，生成测试执行报告 |
| 注意 | 在 testflow 全流程里，这一步由 testflow 的「阶段 4 统一报告」承接（更强大，五源汇总） |
| 话术 | 「/spectest-report 生成执行报告」 |

### 3.9 spectest-archive（第 9 步：归档）

| 项 | 说明 |
|----|------|
| 干什么 | 把完成的变更移入归档目录，结束本次测试工作 |
| 动作 | `spectest/changes/<name>/` → `spectest/changes/archive/<日期>-<name>/` |
| 话术 | 「/spectest-archive 归档当前变更」 |

### 3.10 spectest-convert（附：格式转换）

| 项 | 说明 |
|----|------|
| 干什么 | 测试用例格式互转：Excel ↔ XMind ↔ Markdown |
| 话术 | 「/spectest-convert 把 artifacts/xx_testcases.xlsx 转成 XMind」 |

## 4. 完整走一遍（对小白最重要的一节）

**第 0 步**：cd 到被测项目根目录，打开 Claude Code。

**第 1 步**：
> 「/spectest-new 创建变更 jifen-v2，需求文档在 docs/PRD-积分商城.docx」

**第 2 步**：
> 「/spectest-analysis 分析需求」

**第 3 步**（可选）：
> 「/spectest-plan 生成测试计划」

**第 4 步**：
> 「/spectest-points 推导测试点」

**第 5 步**：
> 「/spectest-generate from-specs 导出 Excel」

**第 6 步**：
> 「/spectest-review 评审用例」

**第 7 步**（如有问题）：
> 「/spectest-fix 修复」

→ 得到 `spectest/changes/jifen-v2/artifacts/jifen-v2_testcases.xlsx`。之后交给执行支线（见 [05](05-技能详解-browser-use与case-runner-WebUI执行.md)/[06](06-技能详解-miniprogram-小程序自动化.md) 册）或入库（见 [10](10-技能详解-test-automation-资产库与CI.md) 册）。

> 💡 **懒人版**：以上 1→7 步也可以一句话启动全流程：「按 spectest 流程从新建变更到生成修复用例一条龙，变更名 jifen-v2，需求文档 docs/PRD-积分商城.docx」——或在 testflow 里自动串行（见 [11](11-技能详解-testflow-全流程调度.md) 册）。

## 5. 常见问题

**Q：9 步必须全走吗？**
不必。最小可用路径：`new → analysis → points → generate` 四步就有 25 列用例了；plan/report/archive 按需。

**Q：已有用例表，只想让它评审/转换行不行？**
行。直接 `/spectest-review` 或 `/spectest-convert` 指定文件。

**Q：脚本怎么跑？（AI 一般自己跑，仅供了解）**
spectest 的 Python 脚本**必须用 uv** 且变量赋值与 uv run 同一条命令：

```bash
SKILL_DIR="e:/AI/skills/spectest/spectest/spectest-generate"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/<脚本>.py" [参数]
```

首次先 `uv sync --project "$SKILL_DIR"`。

## 6. 和其他技能的关系

- **上游**：prd-review（评审报告附入 proposal.md）；
- **下游**：25 列 Excel → testflow 转换器 → UI/小程序执行；→ promote_cases.py 入库；
- **在 testflow 中**：承担阶段 2（report/archive 由 testflow 阶段 4/5 承接；plan 与 design.md 在 testflow 内「不停等」直接继续，单独使用时才停靠确认）。

---

*本册基于 spectest V1（2026-10-29 现状）整理；25 列列定义以 [spectest/CLAUDE.md](../../spectest/CLAUDE.md) 为准。*
