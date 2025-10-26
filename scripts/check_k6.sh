#!/bin/bash

# Script to verify K6 installation and version
# Requirements: K6 v0.47+

set -e

REQUIRED_VERSION="0.47"
COLOR_GREEN="\033[0;32m"
COLOR_RED="\033[0;31m"
COLOR_YELLOW="\033[1;33m"
COLOR_RESET="\033[0m"

echo "======================================="
echo "  K6 Installation Verification"
echo "======================================="
echo ""

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo -e "${COLOR_RED}✗ K6 is not installed${COLOR_RESET}"
    echo ""
    echo "Installation instructions:"
    echo ""
    echo "macOS (Homebrew):"
    echo "  brew install k6"
    echo ""
    echo "Linux (Debian/Ubuntu):"
    echo "  sudo gpg -k"
    echo "  sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69"
    echo "  echo 'deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main' | sudo tee /etc/apt/sources.list.d/k6.list"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install k6"
    echo ""
    echo "For other platforms, visit: https://k6.io/docs/get-started/installation/"
    echo ""
    exit 1
fi

# Get installed version
INSTALLED_VERSION=$(k6 version | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | sed 's/v//')

echo -e "${COLOR_GREEN}✓ K6 is installed${COLOR_RESET}"
echo "  Installed version: v${INSTALLED_VERSION}"
echo "  Required version:  v${REQUIRED_VERSION}+"
echo ""

# Compare versions (simple major.minor comparison)
INSTALLED_MAJOR=$(echo "$INSTALLED_VERSION" | cut -d. -f1)
INSTALLED_MINOR=$(echo "$INSTALLED_VERSION" | cut -d. -f2)
REQUIRED_MAJOR=$(echo "$REQUIRED_VERSION" | cut -d. -f1)
REQUIRED_MINOR=$(echo "$REQUIRED_VERSION" | cut -d. -f2)

if [ "$INSTALLED_MAJOR" -gt "$REQUIRED_MAJOR" ] || \
   ([ "$INSTALLED_MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$INSTALLED_MINOR" -ge "$REQUIRED_MINOR" ]); then
    echo -e "${COLOR_GREEN}✓ K6 version meets requirements${COLOR_RESET}"
    echo ""
    echo "K6 is ready to use!"
    exit 0
else
    echo -e "${COLOR_RED}✗ K6 version is too old${COLOR_RESET}"
    echo "  Please upgrade to v${REQUIRED_VERSION} or higher"
    echo ""
    echo "Upgrade instructions:"
    echo "  macOS: brew upgrade k6"
    echo "  Linux: sudo apt-get update && sudo apt-get upgrade k6"
    echo ""
    exit 1
fi
