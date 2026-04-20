#!/bin/bash
# Download and update AWS Architecture Icons for aws-diagram skill
# Source: @nxavis/aws-icons npm package (derived from official AWS Architecture Icons)
# License: CC-BY-4.0
#
# Usage: ./download-icons.sh
#
# This script:
# 1. Downloads the @nxavis/aws-icons npm package
# 2. Extracts SVG icon data from React components
# 3. Writes standalone SVG files to ../icons/
#
# Prerequisites: node, npm

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ICONS_DIR="$SCRIPT_DIR/../icons"
TEMP_DIR="/tmp/aws-icons-update-$$"

echo "Downloading @nxavis/aws-icons package..."
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"
npm pack @nxavis/aws-icons 2>/dev/null
tar -xzf nxavis-aws-icons-*.tgz

echo "Extracting icons..."
node "$SCRIPT_DIR/../scripts/../scripts/extract-icons.js" 2>&1 || \
  echo "Run extract-icons.js from the project root with node"

echo "Cleaning up..."
rm -rf "$TEMP_DIR"

echo "Icons updated in $ICONS_DIR"
echo "Total icons: $(ls "$ICONS_DIR"/*.svg 2>/dev/null | wc -l)"
