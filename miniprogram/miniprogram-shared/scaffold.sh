#!/usr/bin/env bash
# 将 skill 内 templates 拷贝到用户自动化仓库根。
# Usage:
#   bash <skills-root>/miniprogram-shared/scaffold.sh [目标仓库根]
# 默认目标：当前工作目录。

set -euo pipefail

SKILL_SHARED="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES="$SKILL_SHARED/templates"
TARGET="${1:-$(pwd)}"

if [[ ! -d "$TEMPLATES" ]]; then
  echo "Error: templates not found at $TEMPLATES" >&2
  exit 1
fi

mkdir -p "$TARGET/scripts" \
  "$TARGET/miniprogram/tests/helpers" \
  "$TARGET/miniprogram/tests/auth" \
  "$TARGET/miniprogram/tests/home" \
  "$TARGET/miniprogram/tests/maintenance" \
  "$TARGET/miniprogram/tests/profile" \
  "$TARGET/miniprogram/inspect" \
  "$TARGET/miniprogram/probes" \
  "$TARGET/reports"

cp -f "$TEMPLATES/scripts/"*.js "$TARGET/scripts/"
cp -f "$TEMPLATES/helpers/"*.js "$TARGET/miniprogram/tests/helpers/"
cp -f "$TEMPLATES/jest.config.js" "$TARGET/jest.config.js"
cp -f "$TEMPLATES/jest.setup.js" "$TARGET/jest.setup.js"

if [[ ! -f "$TARGET/miniprogram/suite.json" ]]; then
  cp -f "$TEMPLATES/suite.json.example" "$TARGET/miniprogram/suite.json"
fi

EXAMPLE_CFG="$SKILL_SHARED/miniprogram.local.config.example"
if [[ -f "$EXAMPLE_CFG" && ! -f "$TARGET/miniprogram.local.config" ]]; then
  cp -f "$EXAMPLE_CFG" "$TARGET/miniprogram.local.config"
  echo "Created miniprogram.local.config — please edit projectPath / cliPath / wsEndpoint"
fi

# .gitignore 片段
GITIGNORE="$TARGET/.gitignore"
touch "$GITIGNORE"
for line in 'node_modules/' 'reports/artifacts/' 'miniprogram.local.config' '.DS_Store'; do
  if ! grep -qxF "$line" "$GITIGNORE" 2>/dev/null; then
    echo "$line" >> "$GITIGNORE"
  fi
done

echo "Scaffolded into: $TARGET"
echo "Next:"
echo "  1. Edit miniprogram.local.config"
echo "  2. npm install --save-dev jest miniprogram-automator xlsx  (see templates/package.deps.md)"
echo "  3. export MP_ACCOUNT / MP_PASSWORD"
echo "  4. @miniprogram-script-author 生成用例"
