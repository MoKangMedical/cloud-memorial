#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo "  念念 Eterna - 部署脚本"
echo "========================================="

# Build Docker image
echo "Building Docker image..."
docker build -t eterna-cloud-memorial .

# Run with docker-compose
echo "Starting services..."
docker-compose up -d

echo ""
echo "Deployed! Open http://localhost:8102"
echo "Check logs: docker-compose logs -f"
echo "Stop: docker-compose down"
