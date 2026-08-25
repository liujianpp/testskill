# Task 4 Brief: 修复并扩展 sync_skills.ps1 + 部署验证

（摘自 e:/AI/skills/docs/superpowers/plans/2026-08-24-testflow.md 的 Task 4 全文，逐字为准）

## Global Constraints（对本任务生效的摘录）

- 工作区 `e:/AI/skills/` **不是 git 仓库**：**无 commit 步骤**，以「部署产物存在 + 冒烟通过」收尾
- 平台 win32：PowerShell 脚本用 `powershell -ExecutionPolicy Bypass -File` 执行
- 部署目标：`C:\Users\admin\.claude\skills\`

## 背景

- Task 1-3 已产出 `e:/AI/skills/testflow/`（SKILL.md、scripts/ 两个脚本 + tests、references/workflow-map.md）
- 现有 sync 脚本 `e:/AI/skills/spectest/spectest/sync_skills.ps1` 有两个问题：
  1. `$SourceDir` 指向已迁移的旧路径 `E:\AI\spectest\spectest`（仓库已迁到 `E:\AI\skills`）
  2. 只同步 spectest-* 技能，不覆盖 testflow 目录

## Files

- Modify: `e:/AI/skills/spectest/spectest/sync_skills.ps1`（改 `$SourceDir` 行 + 文末追加 testflow 同步块）

## Steps

### Step 1: 修 $SourceDir 旧路径

在 `e:/AI/skills/spectest/spectest/sync_skills.ps1` 中，把：

```powershell
$SourceDir = "E:\AI\spectest\spectest"
```

替换为：

```powershell
$SourceDir = "E:\AI\skills\spectest\spectest"
```

### Step 2: 追加 testflow 同步块

在文件末尾（`Write-Host "   ls $TargetDir\spectest-generate\scripts\"` 之后）追加：

```powershell

# ══════════════════════════════════════════════════════════
# testflow 调度套件同步（scripts/references 整目录 + SKILL.md）
# ══════════════════════════════════════════════════════════
$TestflowSource = "E:\AI\skills\testflow"
$TestflowTarget = Join-Path $TargetDir "testflow"

if (Test-Path $TestflowSource) {
    Write-Host "📦 处理: testflow" -ForegroundColor Cyan
    if (-not (Test-Path $TestflowTarget)) {
        New-Item -ItemType Directory -Path $TestflowTarget | Out-Null
    }
    foreach ($sub in @("scripts", "references")) {
        $srcSub = Join-Path $TestflowSource $sub
        $dstSub = Join-Path $TestflowTarget $sub
        if (Test-Path $srcSub) {
            if (-not (Test-Path $dstSub)) { New-Item -ItemType Directory -Path $dstSub | Out-Null }
            Copy-Item -Path "$srcSub\*" -Destination $dstSub -Recurse -Force
            Write-Host "  ✓ $sub/ 已同步" -ForegroundColor Green
        }
    }
    Copy-Item (Join-Path $TestflowSource "SKILL.md") -Destination $TestflowTarget -Force
    Write-Host "  ✓ SKILL.md 已同步" -ForegroundColor Green
    Write-Host "  ✅ testflow 同步完成" -ForegroundColor Green
} else {
    Write-Host "⚠️ 未找到 $TestflowSource，跳过 testflow 同步" -ForegroundColor Yellow
}
```

注意：同步 scripts/ 时会把 tests/ 子目录一并复制（Recurse），这是预期行为（部署后测试可就地运行）。

### Step 3: 执行同步

Run: `powershell -ExecutionPolicy Bypass -File e:/AI/skills/spectest/spectest/sync_skills.ps1`
Expected: 输出各 spectest 技能「同步完成」+ `✅ testflow 同步完成`，无红色错误

### Step 4: 验证部署产物

Run:
```bash
ls "C:/Users/admin/.claude/skills/testflow/SKILL.md" "C:/Users/admin/.claude/skills/testflow/scripts/convert_25col_to_ui_xlsx.py" "C:/Users/admin/.claude/skills/testflow/scripts/aggregate_reports.py" "C:/Users/admin/.claude/skills/testflow/references/workflow-map.md" && ls "C:/Users/admin/.claude/skills/spectest-generate/scripts/generate_excel.py"
```
Expected: 5 个 testflow 文件 + spectest-generate 脚本全部列出（证明 $SourceDir 修复生效）

### Step 5: 部署后冒烟（部署目录脚本可运行）

Run: `python "C:/Users/admin/.claude/skills/testflow/scripts/convert_25col_to_ui_xlsx.py" --help`
Expected: 打印 usage（`-i/-o/--sheet/--types`）
