---
name: spectest-archive
description: SpecTest 归档 - 将当前测试变更移动到 archive 目录。当用户要归档测试、结束本次测试工作、或执行 spectest-archive 时使用。将 spectest/changes/<name>/ 移动到 spectest/changes/archive/<date>-<name>/。
---

# spectest-archive：归档测试变更

## 职责

将当前 SpecTest 变更目录整体移动到 `spectest/changes/archive/<date>-<name>/`，完成本次测试工作的收尾；归档名建议带日期（如 `2026-03-19-address-management`）。

**复用 opentest-archive 的能力。**

## 当前变更目录

- 若用户指定了变更名，使用 `spectest/changes/<name>/`。
- 若未指定且项目下仅有一个非归档变更目录（即 `spectest/changes/` 下仅有一个非 `archive` 的子目录），则默认使用该目录。
- 若有多个未归档变更，询问用户要归档哪一个。

## 执行步骤

1. **确定当前变更目录**，记为 `<name>`。
2. **确定归档名**：`<date>-<name>`，其中日期建议为 YYYY-MM-DD（可用当前日期）。
3. **移动目录**：将 `spectest/changes/<name>/` 整体移动到 `spectest/changes/archive/<date>-<name>/`。若 `spectest/changes/archive/` 不存在，先创建。
4. **告知用户**：归档后的路径 `spectest/changes/archive/<date>-<name>/`，并说明该变更已结束，可开始新的测试工作（使用 spectest-new）。

## 产物

- 原 `spectest/changes/<name>/` 不再存在；其内容现位于 `spectest/changes/archive/<date>-<name>/`。

## 完成后

归档完成后，可以执行：
- `/spectest-new <新变更名>` - 开始新的测试工作
