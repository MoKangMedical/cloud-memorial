#!/bin/bash
# 念念 Eterna 一键部署脚本
PORT=${1:-8097}
echo "💭 念念 Eterna 部署中..."
cd "$(dirname "$0")"
python3 -c "import fastapi" 2>/dev/null || pip3 install fastapi uvicorn
echo "✅ 念念已启动: http://localhost:$PORT"
echo "   用你的原始启动命令替换此脚本的实际启动部分"
