#!/bin/bash
# 初始化 testcase-convert 的 uv 虚拟环境
# 仅首次使用时运行；后续检测到环境已存在则跳过

SKILL_DIR="/home/che/.claude/skills/testcase-convert"
VENV_DIR="$SKILL_DIR/.venv"

echo "[setup] 检查 uv 环境..."

# 检查 uv 是否可用
if ! command -v uv &>/dev/null; then
    echo "[ERROR] uv 未安装，请先安装："
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 如果虚拟环境已存在且包已安装，跳过
if [ -f "$VENV_DIR/bin/python" ]; then
    if "$VENV_DIR/bin/python" -c "import pandas, openpyxl, python_calamine" 2>/dev/null; then
        echo "[setup] 环境已就绪，跳过安装"
        exit 0
    fi
fi

echo "[setup] 正在创建 uv 虚拟环境..."
cd "$SKILL_DIR" || exit 1
uv venv "$VENV_DIR"

echo "[setup] 正在安装依赖包..."
uv pip install --python "$VENV_DIR/bin/python" pandas openpyxl python-calamine

# 验证安装
if "$VENV_DIR/bin/python" -c "import pandas, openpyxl, python_calamine; print('[setup] 依赖验证通过')" 2>&1; then
    echo "[setup] 环境初始化完成！"
    echo "[setup] Python: $($VENV_DIR/bin/python --version)"
else
    echo "[ERROR] 依赖安装验证失败"
    exit 1
fi
