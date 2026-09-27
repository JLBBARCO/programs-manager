#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Cleaning old builds..."
rm -rf dist build
rm -f "Programs Manager.spec"

echo "Installing required dependencies..."
python3 -m pip install --upgrade pip --break-system-packages
python3 -m pip install -r requirements.txt --break-system-packages

echo "Starting build with PyInstaller..."
python3 -m PyInstaller --noconfirm --clean --onedir --windowed \
    --name "Programs Manager" \
    --paths "core-app" \
    --paths "." \
    --add-data "core-app/lib:lib" \
    --add-data "core-app/assets:assets" \
    --add-data "core-app/system:system" \
    --add-data "src:src" \
    --collect-all customtkinter \
    --collect-all psutil \
    --noupx \
    "core-app/main.py"

test -d "dist/Programs Manager"
echo "Build completed successfully!"
echo "Executable is at: dist/Programs Manager/"