#!/bin/bash

# Start Grafana + InfluxDB monitoring stack
# Usage: ./scripts/start_monitoring.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🚀 Starting monitoring stack (Grafana + InfluxDB)..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo ""
    echo "💡 To fix:"
    echo "   1. Open Docker Desktop (Applications folder)"
    echo "   2. Wait for Docker to start (whale icon in menu bar)"
    echo "   3. Run this script again"
    echo ""
    exit 1
fi

# Check if services already running
if docker ps | grep -q "promo-grafana"; then
    echo "⚠️  Monitoring stack is already running"
    echo ""
    echo "📊 Grafana Dashboard: http://localhost:3000"
    echo "   Login: admin / admin"
    echo ""
    read -p "Do you want to restart? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    echo "🔄 Restarting services..."
    docker compose -f docker-compose.monitoring.yml restart
    sleep 5
else
    # Start services
    echo "🐳 Starting Docker containers..."
    docker compose -f docker-compose.monitoring.yml up -d
fi

echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for Grafana (max 60 seconds)
COUNTER=0
MAX_WAIT=60
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "✅ Grafana is ready"
        break
    fi
    printf "."
    sleep 2
    COUNTER=$((COUNTER + 2))
done

if [ $COUNTER -ge $MAX_WAIT ]; then
    echo ""
    echo "❌ Grafana did not start in time"
    echo "   Check logs: docker logs promo-grafana"
    exit 1
fi

# Wait for InfluxDB (max 60 seconds)
COUNTER=0
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8086/health > /dev/null 2>&1; then
        echo "✅ InfluxDB is ready"
        break
    fi
    printf "."
    sleep 2
    COUNTER=$((COUNTER + 2))
done

if [ $COUNTER -ge $MAX_WAIT ]; then
    echo ""
    echo "❌ InfluxDB did not start in time"
    echo "   Check logs: docker logs promo-influxdb"
    exit 1
fi

echo ""
echo "🎉 Monitoring stack is ready!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 GRAFANA DASHBOARD"
echo "   URL: http://localhost:3000"
echo "   Login: admin / admin"
echo ""
echo "🔍 INFLUXDB UI"
echo "   URL: http://localhost:8086"
echo "   Login: admin / admin123"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 USAGE"
echo ""
echo "   Run test with dashboard:"
echo "   python -m src.cli --url 'https://...' --enable-dashboard"
echo ""
echo "   Example:"
echo "   python -m src.cli \\"
echo "     --url 'https://preprod.ipln.fr/photo-video/3867-sony.html' \\"
echo "     --intensity medium \\"
echo "     --enable-dashboard"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🛑 To stop: ./scripts/stop_monitoring.sh"
echo ""

# Open Grafana in browser
if command -v open > /dev/null 2>&1; then
    echo "🌐 Opening Grafana in browser..."
    sleep 2
    open http://localhost:3000
fi
