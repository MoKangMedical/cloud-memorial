#!/bin/bash
set -euo pipefail

PORT=${1:-8102}
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$APP_DIR/cloud_memorial.log"

echo "念念部署中..."
echo "工作目录: $APP_DIR"
echo "监听端口: $PORT"

cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q

pkill -f ".venv/bin/python -m uvicorn api.app:app.*$PORT" 2>/dev/null || true

nohup .venv/bin/python -m uvicorn api.app:app --host 0.0.0.0 --port "$PORT" > "$LOG_FILE" 2>&1 &

sleep 3

if curl -fsS "http://127.0.0.1:$PORT/health" > /dev/null 2>&1; then
    echo "念念已启动"
    echo "API: http://127.0.0.1:$PORT"
    echo "文档: http://127.0.0.1:$PORT/docs"
    echo "日志: $LOG_FILE"
else
    echo "启动失败，请检查日志: $LOG_FILE"
    exit 1
fi
