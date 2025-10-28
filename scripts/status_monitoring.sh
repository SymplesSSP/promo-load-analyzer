#!/bin/bash

# Show monitoring stack status
# Usage: ./scripts/status_monitoring.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🔍 Monitoring Stack Status"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Docker status
if docker info > /dev/null 2>&1; then
    echo "🐳 Docker: ✅ Running"
else
    echo "🐳 Docker: ❌ Not running"
    echo ""
    echo "💡 Start Docker Desktop and try again"
    exit 1
fi

echo ""

# Containers status
if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(promo-grafana|promo-influxdb|NAMES)"; then
    echo ""
else
    echo "📦 Containers: ❌ Not running"
    echo ""
    echo "💡 Start monitoring: ./scripts/start_monitoring.sh"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Service health
GRAFANA_STATUS="❌"
INFLUXDB_STATUS="❌"

if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    GRAFANA_STATUS="✅"
fi

if curl -s http://localhost:8086/health > /dev/null 2>&1; then
    INFLUXDB_STATUS="✅"
fi

echo "📊 Grafana:  $GRAFANA_STATUS http://localhost:3000"
echo "🔍 InfluxDB: $INFLUXDB_STATUS http://localhost:8086"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Disk usage
echo "💾 Disk Usage:"
du -sh monitoring/influxdb-data 2>/dev/null | awk '{print "   InfluxDB data: " $1}' || echo "   InfluxDB data: (empty)"
du -sh monitoring/grafana-data 2>/dev/null | awk '{print "   Grafana data:  " $1}' || echo "   Grafana data: (empty)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Quick actions
echo "🛠️  Quick Actions:"
echo ""
echo "   Start:   ./scripts/start_monitoring.sh"
echo "   Stop:    ./scripts/stop_monitoring.sh"
echo "   Test:    ./scripts/test_monitoring.sh"
echo "   Logs:    docker logs promo-grafana"
echo "            docker logs promo-influxdb"
echo ""
