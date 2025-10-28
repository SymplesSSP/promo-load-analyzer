#!/bin/bash

# Stop Grafana + InfluxDB monitoring stack
# Usage: ./scripts/stop_monitoring.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🛑 Stopping monitoring stack..."

docker compose -f docker-compose.monitoring.yml down

echo ""
echo "✅ Monitoring stack stopped"
echo ""
echo "💡 Data is preserved in ./monitoring/ directory"
echo "   To start again: ./scripts/start_monitoring.sh"
echo ""
