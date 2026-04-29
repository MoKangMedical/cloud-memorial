#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# 念念 Eterna - 一键启动脚本
# ==========================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  念念 Eterna - AI 思念亲人平台${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python
if ! command -v python3.12 &>/dev/null; then
    if command -v python3 &>/dev/null; then
        PYTHON=python3
    else
        echo -e "${RED}Error: Python not found${NC}"
        exit 1
    fi
else
    PYTHON=python3.12
fi

echo -e "${GREEN}Using Python: $($PYTHON --version)${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
$PYTHON -m pip install -q -r requirements.txt 2>/dev/null || true

# Create data directories
mkdir -p memorial_data/uploads/{voice,photo,video,model3d}
mkdir -p memorial_data/media

# Check .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env found, copying from .env.example...${NC}"
    cp .env.example .env 2>/dev/null || true
fi

# Get port from .env or use default
PORT=${PORT:-8102}

echo ""
echo -e "${GREEN}Starting server on port $PORT...${NC}"
echo -e "${BLUE}Open http://localhost:$PORT in your browser${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo ""

# Start the server
$PYTHON -m uvicorn api.main:app --host 0.0.0.0 --port "$PORT" --reload
