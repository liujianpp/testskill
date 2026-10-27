# SpecTest 技能同步脚本
# 用途：将 E:\AI\skills\spectest\spectest\spectest-*\ 同步到 C:\Users\admin\.claude\skills\spectest-*\

$SourceDir = "E:\AI\skills\spectest\spectest"
$TargetDir = "C:\Users\admin\.claude\skills"

Write-Host "=== 开始同步 SpecTest 技能 ===" -ForegroundColor Green
Write-Host "源目录: $SourceDir"
Write-Host "目标目录: $TargetDir"
Write-Host ""

# 统计变量
$totalSkills = 0
$syncedScripts = 0
$syncedSkillMd = 0

foreach ($skillDir in Get-ChildItem -Path "$SourceDir\spectest-*" -Directory) {
    $skillName = $skillDir.Name
    $targetPath = Join-Path $TargetDir $skillName

    Write-Host "📦 处理: $skillName" -ForegroundColor Cyan
    $totalSkills++

    # 创建目标目录（如果不存在）
    if (-not (Test-Path $targetPath)) {
        New-Item -ItemType Directory -Path $targetPath | Out-Null
        Write-Host "  ✓ 创建目录: $targetPath" -ForegroundColor Yellow
    }

    # 同步 scripts 目录
    $scriptsPath = Join-Path $skillDir.FullName "scripts"
    if (Test-Path $scriptsPath) {
        $targetScripts = Join-Path $targetPath "scripts"
        if (-not (Test-Path $targetScripts)) {
            New-Item -ItemType Directory -Path $targetScripts | Out-Null
        }
        Copy-Item -Path "$scriptsPath\*" -Destination $targetScripts -Recurse -Force
        Write-Host "  ✓ scripts/ 已同步" -ForegroundColor Green
        $syncedScripts++
        # 显示同步的 Python 文件
        $pyFiles = Get-ChildItem -Path $targetScripts -Filter "*.py" -File
        foreach ($py in $pyFiles) {
            Write-Host "      - $($py.Name)" -ForegroundColor Gray
        }
    }

    # 同步 SKILL.md
    $skillMd = Join-Path $skillDir.FullName "SKILL.md"
    if (Test-Path $skillMd) {
        Copy-Item $skillMd -Destination $targetPath -Force
        Write-Host "  ✓ SKILL.md 已同步" -ForegroundColor Green
        $syncedSkillMd++
    }

    # 同步 references 目录
    $refsPath = Join-Path $skillDir.FullName "references"
    if (Test-Path $refsPath) {
        $targetRefs = Join-Path $targetPath "references"
        if (-not (Test-Path $targetRefs)) {
            New-Item -ItemType Directory -Path $targetRefs | Out-Null
        }
        Copy-Item -Path "$refsPath\*" -Destination $targetRefs -Recurse -Force
        Write-Host "  ✓ references/ 已同步" -ForegroundColor Green
    }

    # 同步 assets 目录
    $assetsPath = Join-Path $skillDir.FullName "assets"
    if (Test-Path $assetsPath) {
        $targetAssets = Join-Path $targetPath "assets"
        if (-not (Test-Path $targetAssets)) {
            New-Item -ItemType Directory -Path $targetAssets | Out-Null
        }
        Copy-Item -Path "$assetsPath\*" -Destination $targetAssets -Recurse -Force
        Write-Host "  ✓ assets/ 已同步" -ForegroundColor Green
    }

    # 同步 pyproject.toml
    $pyproject = Join-Path $skillDir.FullName "pyproject.toml"
    if (Test-Path $pyproject) {
        Copy-Item $pyproject -Destination $targetPath -Force
        Write-Host "  ✓ pyproject.toml 已同步" -ForegroundColor Green
    }

    Write-Host "  ✅ $skillName 同步完成" -ForegroundColor Green
    Write-Host ""
}

Write-Host "=== ✅ 所有 SpecTest 技能已同步完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "📊 同步统计：" -ForegroundColor Cyan
Write-Host "  总技能数: $totalSkills"
Write-Host "  同步 scripts/: $syncedScripts"
Write-Host "  同步 SKILL.md: $syncedSkillMd"
Write-Host ""
Write-Host "⏰ 同步时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""
Write-Host "💡 提示：请验证关键脚本是否同步成功" -ForegroundColor Yellow
Write-Host "   ls $TargetDir\spectest-generate\scripts\"

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

# ══════════════════════════════════════════════════════════
# miniprogram 三件套同步（整目录：script-author / run / shared）
# ══════════════════════════════════════════════════════════
$MpSource = "E:\AI\skills\miniprogram"

if (Test-Path $MpSource) {
    foreach ($mpDir in @("miniprogram-script-author", "miniprogram-run", "miniprogram-shared")) {
        $srcDir = Join-Path $MpSource $mpDir
        $dstDir = Join-Path $TargetDir $mpDir
        Write-Host "📦 处理: $mpDir" -ForegroundColor Cyan
        if (-not (Test-Path $dstDir)) {
            New-Item -ItemType Directory -Path $dstDir | Out-Null
        }
        Copy-Item -Path "$srcDir\*" -Destination $dstDir -Recurse -Force
        Write-Host "  ✅ $mpDir 同步完成" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ 未找到 $MpSource，跳过 miniprogram 同步" -ForegroundColor Yellow
}
