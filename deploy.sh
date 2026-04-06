#!/bin/bash
# 🌸 云思园部署脚本
PORT=${1:-8097}

echo "🌸 云思园部署中..."
echo "📍 让思念不再有距离"

# 安装依赖
pip install -r requirements.txt -q

# 停止旧进程
pkill -f "uvicorn.*app:app.*$PORT" 2>/dev/null

# 启动
nohup python -m uvicorn api.app:app --host 0.0.0.0 --port $PORT > cloud_memorial.log 2>&1 &

sleep 2

if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "✅ 云思园已启动！"
    echo "📍 API: http://localhost:$PORT"
    echo "📍 文档: http://localhost:$PORT/docs"
    echo "📍 PID: $(pgrep -f 'uvicorn.*app:app.*$PORT')"
else
    echo "❌ 启动失败，请检查日志"
fi
