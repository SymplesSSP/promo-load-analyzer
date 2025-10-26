#!/bin/bash

# Development Environment Setup Script
# Promo Load Analyzer
#
# This script automates the setup of the development environment:
# - Checks Python version (3.11+)
# - Creates virtual environment
# - Installs all dependencies (production + dev)
# - Installs Playwright browsers
# - Verifies K6 installation
#
# Usage: ./scripts/setup_dev.sh

set -e  # Exit on error

COLOR_GREEN="\033[0;32m"
COLOR_RED="\033[0;31m"
COLOR_YELLOW="\033[1;33m"
COLOR_BLUE="\033[0;34m"
COLOR_RESET="\033[0m"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
REQUIRED_PYTHON_VERSION="3.11"

echo ""
echo "======================================="
echo "  Promo Load Analyzer Setup"
echo "======================================="
echo ""

# Step 1: Check Python version
echo -e "${COLOR_BLUE}[1/6] Checking Python version...${COLOR_RESET}"

if ! command -v python3 &> /dev/null; then
    echo -e "${COLOR_RED}✗ Python 3 is not installed${COLOR_RESET}"
    echo "  Please install Python 3.11+ first"
    echo "  Visit: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
REQUIRED_MAJOR=$(echo "$REQUIRED_PYTHON_VERSION" | cut -d. -f1)
REQUIRED_MINOR=$(echo "$REQUIRED_PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt "$REQUIRED_MAJOR" ] || \
   ([ "$PYTHON_MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$PYTHON_MINOR" -lt "$REQUIRED_MINOR" ]); then
    echo -e "${COLOR_RED}✗ Python version is too old${COLOR_RESET}"
    echo "  Installed: $PYTHON_VERSION"
    echo "  Required:  $REQUIRED_PYTHON_VERSION+"
    exit 1
fi

echo -e "${COLOR_GREEN}✓ Python $PYTHON_VERSION detected${COLOR_RESET}"
echo ""

# Step 2: Create virtual environment
echo -e "${COLOR_BLUE}[2/6] Creating virtual environment...${COLOR_RESET}"

if [ -d "$VENV_PATH" ]; then
    echo -e "${COLOR_YELLOW}⚠ Virtual environment already exists${COLOR_RESET}"
    read -p "  Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_PATH"
        python3 -m venv "$VENV_PATH"
        echo -e "${COLOR_GREEN}✓ Virtual environment recreated${COLOR_RESET}"
    else
        echo -e "${COLOR_YELLOW}→ Skipping venv creation${COLOR_RESET}"
    fi
else
    python3 -m venv "$VENV_PATH"
    echo -e "${COLOR_GREEN}✓ Virtual environment created${COLOR_RESET}"
fi
echo ""

# Step 3: Activate virtual environment and upgrade pip
echo -e "${COLOR_BLUE}[3/6] Installing dependencies...${COLOR_RESET}"

# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"

echo "  → Installing production dependencies..."
pip install -q -r "$PROJECT_ROOT/requirements.txt"
echo -e "${COLOR_GREEN}  ✓ Production dependencies installed${COLOR_RESET}"

echo "  → Installing development dependencies..."
pip install -q -r "$PROJECT_ROOT/requirements-dev.txt"
echo -e "${COLOR_GREEN}  ✓ Development dependencies installed${COLOR_RESET}"
echo ""

# Step 4: Install Playwright browsers
echo -e "${COLOR_BLUE}[4/6] Installing Playwright browsers...${COLOR_RESET}"

playwright install chromium
echo -e "${COLOR_GREEN}✓ Playwright Chromium installed${COLOR_RESET}"
echo ""

# Step 5: Verify K6 installation
echo -e "${COLOR_BLUE}[5/6] Verifying K6 installation...${COLOR_RESET}"

if ! command -v k6 &> /dev/null; then
    echo -e "${COLOR_RED}✗ K6 is not installed${COLOR_RESET}"
    echo ""
    echo "Please install K6:"
    echo "  macOS: brew install k6"
    echo "  Linux: See https://k6.io/docs/get-started/installation/"
    echo ""
    echo "After installing K6, you can verify with:"
    echo "  ./scripts/check_k6.sh"
    exit 1
else
    K6_VERSION=$(k6 version | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+')
    echo -e "${COLOR_GREEN}✓ K6 ${K6_VERSION} is installed${COLOR_RESET}"
fi
echo ""

# Step 6: Create necessary directories
echo -e "${COLOR_BLUE}[6/6] Creating runtime directories...${COLOR_RESET}"

mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/output"
mkdir -p "$PROJECT_ROOT/k6_scripts"
mkdir -p "$PROJECT_ROOT/k6_results"

echo -e "${COLOR_GREEN}✓ Runtime directories created${COLOR_RESET}"
echo ""

# Final success message
echo "======================================="
echo -e "${COLOR_GREEN}✓ Setup completed successfully!${COLOR_RESET}"
echo "======================================="
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Verify installation:"
echo "     python src/main.py --help"
echo ""
echo "  3. Run tests:"
echo "     pytest tests/"
echo ""
echo "  4. Check code quality:"
echo "     ruff check src/"
echo "     mypy src/"
echo ""
echo "Happy coding! 🚀"
echo ""
