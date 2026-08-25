---
name: spectest-new
description: SpecTest 新建测试工作（流程第 1 步：需求文档）- 创建一次测试变更目录并编写 proposal，关联需求文档。当用户要新建 SpecTest 测试工作、创建测试变更、或执行 spectest-new 时使用。创建 spectest/changes/<name>/ 及 proposal.md、specs/、artifacts/、project_info/、db_info/。
---

# spectest-new：新建测试工作（需求文档）

## 职责

新建一次 SpecTest 测试工作：创建变更目录并编写测试提案初稿，在 proposal 中**关联或引用需求文档**（PRD、用户故事、接口说明等），对应流程中的「需求文档」步骤。

## 确定变更名

- 从用户输入中提取被测对象（功能名、模块名、版本号等）。
- 将名称规范为短名：英文或拼音，空格与特殊字符替换为 `-`（如「用户登录」→ `user-login`，`release 2.0` → `release-2.0`）。

## 执行步骤

1. **确保根目录存在**：若项目下没有 `spectest/changes`，先创建。
2. **创建变更目录**：`spectest/changes/<name>/`，以及子目录：
   - `specs/` - 测试点文件
   - `artifacts/` - 产物文件（Excel、XMind、JSON）
   - `project_info/` - 项目资料（需求文档、功能清单、API文档）
   - `db_info/` - 数据库配置
   - `review/` - 评审资料（可选）
3. **编写 proposal.md**：在变更目录下创建 `proposal.md`，包含：
   - 被测对象（功能/模块/版本）
   - **关联需求文档**：路径或链接（PRD、用户故事、接口文档等）
   - 测试目标与原因
   - 可选：关联的 OpenSpec
   - 模板与字段说明见：`reference/proposal-template.md`。
4. **创建 db_config.json**：在 `db_info/` 目录下创建数据库配置文件（可选）。
5. **告知用户**：变更目录路径及下一步可执行「需求分析和梳理」（spectest-analysis）或「测试点」（spectest-points）。

## 产物

- `spectest/changes/<name>/proposal.md`
- `spectest/changes/<name>/specs/`（空目录）
- `spectest/changes/<name>/artifacts/`（空目录）
- `spectest/changes/<name>/project_info/`（空目录）
- `spectest/changes/<name>/db_info/`（空目录）
- `spectest/changes/<name>/review/`（空目录）

## 下一步

完成 proposal.md 后，可以执行：
- `/spectest-analysis` - 智能需求分析，提取功能点和 API
- `/spectest-points` - 手动编写测试点
