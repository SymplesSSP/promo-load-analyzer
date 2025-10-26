#!/bin/bash

# Dependency Check Script
# Promo Load Analyzer
#
# This script verifies all dependencies are correctly installed
#
# Usage: ./scripts/check_dependencies.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

COLOR_GREEN="\033[0;32m"
COLOR_RED="\033[0;31m"
COLOR_BLUE="\033[0;34m"
COLOR_RESET="\033[0m"

echo ""
echo "======================================="
echo "  Dependency Verification"
echo "======================================="
echo ""

ERRORS=0

# Check Python
echo -e "${COLOR_BLUE}Checking Python...${COLOR_RESET}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${COLOR_GREEN}✓ $PYTHON_VERSION${COLOR_RESET}"
else
    echo -e "${COLOR_RED}✗ Python 3 not found${COLOR_RESET}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check Virtual Environment
echo -e "${COLOR_BLUE}Checking Virtual Environment...${COLOR_RESET}"
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${COLOR_GREEN}✓ Virtual environment exists${COLOR_RESET}"

    if [ -n "$VIRTUAL_ENV" ]; then
        echo -e "${COLOR_GREEN}✓ Virtual environment is activated${COLOR_RESET}"
    else
        echo -e "${COLOR_RED}✗ Virtual environment is NOT activated${COLOR_RESET}"
        echo "  Run: source venv/bin/activate"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${COLOR_RED}✗ Virtual environment not found${COLOR_RESET}"
    echo "  Run: ./scripts/setup_dev.sh"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check Python packages (if venv is activated)
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${COLOR_BLUE}Checking Python Packages...${COLOR_RESET}"

    PACKAGES=("playwright" "requests" "jinja2" "pydantic" "loguru" "pytest" "mypy" "ruff")

    for package in "${PACKAGES[@]}"; do
        if pip show "$package" &> /dev/null; then
            VERSION=$(pip show "$package" | grep Version | cut -d' ' -f2)
            echo -e "${COLOR_GREEN}✓ $package ($VERSION)${COLOR_RESET}"
        else
            echo -e "${COLOR_RED}✗ $package not found${COLOR_RESET}"
            ERRORS=$((ERRORS + 1))
        fi
    done
    echo ""
fi

# Check K6
echo -e "${COLOR_BLUE}Checking K6...${COLOR_RESET}"
if command -v k6 &> /dev/null; then
    K6_VERSION=$(k6 version | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+')
    echo -e "${COLOR_GREEN}✓ K6 $K6_VERSION${COLOR_RESET}"
else
    echo -e "${COLOR_RED}✗ K6 not found${COLOR_RESET}"
    echo "  Install: brew install k6 (macOS)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check Playwright browsers
echo -e "${COLOR_BLUE}Checking Playwright Browsers...${COLOR_RESET}"
if [ -n "$VIRTUAL_ENV" ]; then
    if [ -d "$HOME/Library/Caches/ms-playwright" ] || [ -d "$HOME/.cache/ms-playwright" ]; then
        echo -e "${COLOR_GREEN}✓ Playwright browsers installed${COLOR_RESET}"
    else
        echo -e "${COLOR_RED}✗ Playwright browsers not found${COLOR_RESET}"
        echo "  Run: playwright install chromium"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# Summary
echo "======================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${COLOR_GREEN}✓ All dependencies are correctly installed${COLOR_RESET}"
    echo "======================================="
    echo ""
    echo "You're ready to develop! 🚀"
    exit 0
else
    echo -e "${COLOR_RED}✗ Found $ERRORS issue(s)${COLOR_RESET}"
    echo "======================================="
    echo ""
    echo "Please run: ./scripts/setup_dev.sh"
    exit 1
fi
echo ""
