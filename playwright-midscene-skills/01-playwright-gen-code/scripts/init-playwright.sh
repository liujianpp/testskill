#!/bin/bash
# 初始化 Playwright Test 项目（TypeScript + Chromium）
# 可选：--with-midscene 安装 @midscene/web 并写入 tests/fixture.ts
set -euo pipefail

WITH_MIDSCENE=0
TARGET_DIR="."

for arg in "$@"; do
  case "$arg" in
    --with-midscene) WITH_MIDSCENE=1 ;;
    -*)
      echo "未知参数: $arg" >&2
      echo "用法: $0 [目标目录] [--with-midscene]" >&2
      exit 1
      ;;
    *) TARGET_DIR="$arg" ;;
  esac
done

cd "$TARGET_DIR"

ensure_gitignore() {
  local f=".gitignore"
  touch "$f"
  grep -qxF 'midscene_run/' "$f" 2>/dev/null || echo 'midscene_run/' >> "$f"
  grep -qxF '.env' "$f" 2>/dev/null || echo '.env' >> "$f"
}

ensure_env_example() {
  if [ -f ".env.example" ]; then
    echo "  .env.example 已存在，跳过。"
    return
  fi
  cat > .env.example << 'EOF'
# 复制为 .env 后填写真实值（.env 已在 .gitignore，勿提交）
# cp .env.example .env

# 应用
BASE_URL=http://localhost:3000
LOGIN_USERNAME=admin
LOGIN_PASSWORD=123456

# Midscene（含验证码 / 视觉步时必填；模型须支持视觉/多模态读图，纯 chat 不可用）
MIDSCENE_MODEL_API_KEY=
MIDSCENE_MODEL_BASE_URL=
MIDSCENE_MODEL_NAME=
MIDSCENE_MODEL_FAMILY=
EOF
  echo "  已创建 .env.example（请复制为 .env 并填写，勿提交 .env）"
}

install_midscene() {
  echo "正在安装 @midscene/web ..."
  npm install -D @midscene/web

  mkdir -p tests
  if [ ! -f "tests/fixture.ts" ]; then
    cat > tests/fixture.ts << 'EOF'
import { test as base } from '@playwright/test';
import type { PlayWrightAiFixtureType } from '@midscene/web/playwright';
import { PlaywrightAiFixture } from '@midscene/web/playwright';

export const test = base.extend<PlayWrightAiFixtureType>(
  PlaywrightAiFixture({
    waitForNetworkIdleTimeout: 2000,
    cache: true,
  }),
);
EOF
    echo "  已创建 tests/fixture.ts"
  else
    echo "  tests/fixture.ts 已存在，跳过。"
  fi

  if [ -f "playwright.config.ts" ]; then
    if ! grep -q "timeout:" playwright.config.ts 2>/dev/null; then
      # 在 defineConfig({ 后插入 timeout（macOS sed）
      sed -i '' '/defineConfig({/a\
  timeout: 90 * 1000,
' playwright.config.ts 2>/dev/null || true
    fi
    if ! grep -q "@midscene/web/playwright-reporter" playwright.config.ts 2>/dev/null; then
      echo "  请手动确认 playwright.config.ts：timeout ≥ 90s，并追加 Midscene reporter。"
      echo "  参考: reporter: [['list'], ['html', { open: 'never' }], ['@midscene/web/playwright-reporter', { type: 'merged' }]]"
    fi
  fi

  ensure_gitignore
  ensure_env_example
  echo "Midscene 依赖已就绪。请 cp .env.example .env 并填写 MIDSCENE_MODEL_* / BASE_URL。"
}

if [ -f "playwright.config.ts" ] || [ -f "playwright.config.js" ]; then
  echo "Playwright 已初始化，跳过基础安装。"
  if [ "$WITH_MIDSCENE" -eq 1 ]; then
    install_midscene
  fi
  exit 0
fi

echo "正在初始化 Playwright 项目..."
npm init -y > /dev/null 2>&1
npm init playwright@latest -- --quiet --lang=ts --browser=chromium --install-deps
npm install -D @playwright/cli@latest
npx playwright-cli install 2>/dev/null || true

mkdir -p tests/pages tests/explore tests/reports

# 默认无头 + 启用视频与 trace 录制（无头下照常生成）
if ! grep -q "headless:" playwright.config.ts 2>/dev/null; then
  sed -i '' '/use: {/a\
    headless: true,
' playwright.config.ts
fi
if ! grep -q "video:" playwright.config.ts 2>/dev/null; then
  sed -i '' '/use: {/a\
    video: '\''on'\'',
' playwright.config.ts
fi
if ! grep -q "trace:" playwright.config.ts 2>/dev/null; then
  sed -i '' '/use: {/a\
    trace: '\''on'\'',
' playwright.config.ts
fi

# 添加 show-report npm script
if ! grep -q '"show-report"' package.json 2>/dev/null; then
  npm pkg set scripts.show-report="playwright show-report"
fi

echo "Playwright 项目初始化完成。"
echo "  配置文件: playwright.config.ts"
echo "  测试目录: tests/"
echo "  Page Object: tests/pages/"
echo "  测试计划: tests/reports/"
echo "  探索素材: tests/explore/（snapshot / 截图 / auth）"

if [ "$WITH_MIDSCENE" -eq 1 ]; then
  install_midscene
fi
