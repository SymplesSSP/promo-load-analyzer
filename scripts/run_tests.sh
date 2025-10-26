#!/bin/bash

# Test Runner Script
# Promo Load Analyzer
#
# This script runs the complete test suite with coverage reporting
#
# Usage: ./scripts/run_tests.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

COLOR_GREEN="\033[0;32m"
COLOR_BLUE="\033[0;34m"
COLOR_RESET="\033[0m"

echo ""
echo "======================================="
echo "  Running Test Suite"
echo "======================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Run pytest with coverage
echo -e "${COLOR_BLUE}Running pytest with coverage...${COLOR_RESET}"
echo ""

cd "$PROJECT_ROOT"
pytest tests/ \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    -v

echo ""
echo "======================================="
echo -e "${COLOR_GREEN}✓ Test suite completed${COLOR_RESET}"
echo "======================================="
echo ""
echo "Coverage report available at: htmlcov/index.html"
echo ""
