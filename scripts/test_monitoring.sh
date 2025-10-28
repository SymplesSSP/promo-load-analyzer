#!/bin/bash

# Test monitoring stack is working correctly
# Usage: ./scripts/test_monitoring.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🧪 Testing monitoring stack..."
echo ""

# Test 1: Docker running
echo "Test 1/5: Docker running"
if docker info > /dev/null 2>&1; then
    echo "   ✅ Docker is running"
else
    echo "   ❌ Docker is not running"
    exit 1
fi

# Test 2: Containers running
echo "Test 2/5: Containers running"
if docker ps | grep -q "promo-grafana" && docker ps | grep -q "promo-influxdb"; then
    echo "   ✅ Both containers are running"
else
    echo "   ❌ Containers not running (run: ./scripts/start_monitoring.sh)"
    exit 1
fi

# Test 3: Grafana accessible
echo "Test 3/5: Grafana accessible"
if curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo "   ✅ Grafana is accessible"
else
    echo "   ❌ Grafana is not responding"
    exit 1
fi

# Test 4: InfluxDB accessible
echo "Test 4/5: InfluxDB accessible"
if curl -s http://localhost:8086/health | grep -q "pass"; then
    echo "   ✅ InfluxDB is accessible"
else
    echo "   ❌ InfluxDB is not responding"
    exit 1
fi

# Test 5: InfluxDB bucket exists
echo "Test 5/5: InfluxDB bucket configured"
BUCKET_CHECK=$(curl -s -H "Authorization: Token my-super-secret-token" \
  "http://localhost:8086/api/v2/buckets?org=promo-analyzer" | grep -c "k6" || true)

if [ "$BUCKET_CHECK" -gt 0 ]; then
    echo "   ✅ InfluxDB bucket 'k6' exists"
else
    echo "   ⚠️  InfluxDB bucket 'k6' not found (may auto-create on first test)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 All tests passed!"
echo ""
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo "🔍 InfluxDB: http://localhost:8086 (admin/admin123)"
echo ""
echo "💡 Ready to run tests with --enable-dashboard"
echo ""
