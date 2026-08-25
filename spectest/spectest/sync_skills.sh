#!/bin/bash
# SpecTest 技能同步脚本
# 用途：将 E:/AI/spectest/spectest/spectest-*/ 同步到 C:/Users/admin/.claude/skills/spectest-*/

SOURCE_DIR="E:/AI/spectest/spectest"
TARGET_DIR="C:/Users/admin/.claude/skills"

echo "=== 开始同步 SpecTest 技能 ==="
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_DIR"
echo ""

# 统计变量
total_skills=0
synced_scripts=0
synced_skill_md=0

for skill_dir in "$SOURCE_DIR/spectest-"*/; do
  skill_name=$(basename "$skill_dir")
  target_dir="$TARGET_DIR/$skill_name"

  echo "📦 处理: $skill_name"
  total_skills=$((total_skills + 1))

  # 创建目标目录（如果不存在）
  if [ ! -d "$target_dir" ]; then
    mkdir -p "$target_dir"
    echo "  ✓ 创建目录: $target_dir"
  fi

  # 同步 scripts 目录
  if [ -d "$skill_dir/scripts" ]; then
    mkdir -p "$target_dir/scripts"
    cp -rf "$skill_dir/scripts/"* "$target_dir/scripts/"
    echo "  ✓ scripts/ 已同步"
    synced_scripts=$((synced_scripts + 1))
    # 显示同步的 Python 文件
    ls "$target_dir/scripts/" | grep -E "\.py$" | sed 's/^/      - /' 2>/dev/null
  fi

  # 同步 SKILL.md
  if [ -f "$skill_dir/SKILL.md" ]; then
    cp "$skill_dir/SKILL.md" "$target_dir/SKILL.md"
    echo "  ✓ SKILL.md 已同步"
    synced_skill_md=$((synced_skill_md + 1))
  fi

  # 同步 references 目录
  if [ -d "$skill_dir/references" ]; then
    mkdir -p "$target_dir/references"
    cp -rf "$skill_dir/references/"* "$target_dir/references/"
    echo "  ✓ references/ 已同步"
  fi

  # 同步 assets 目录
  if [ -d "$skill_dir/assets" ]; then
    mkdir -p "$target_dir/assets"
    cp -rf "$skill_dir/assets/"* "$target_dir/assets/"
    echo "  ✓ assets/ 已同步"
  fi

  # 同步 pyproject.toml
  if [ -f "$skill_dir/pyproject.toml" ]; then
    cp "$skill_dir/pyproject.toml" "$target_dir/pyproject.toml"
    echo "  ✓ pyproject.toml 已同步"
  fi

  echo "  ✅ $skill_name 同步完成"
  echo ""
done

echo "=== ✅ 所有 SpecTest 技能已同步完成 ==="
echo ""
echo "📊 同步统计："
echo "  总技能数: $total_skills"
echo "  同步 scripts/: $synced_scripts"
echo "  同步 SKILL.md: $synced_skill_md"
echo ""
echo "⏰ 同步时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "💡 提示：请验证关键脚本是否同步成功"
echo "   ls -lh $TARGET_DIR/spectest-generate/scripts/"
