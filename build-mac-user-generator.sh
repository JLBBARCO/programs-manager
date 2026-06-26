#!/usr/bin/env bash
set -euo pipefail

echo "Cleaning old builds..."
rm -rf dist build "Programs Manager User Generator.spec"

echo "Installing required dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Starting macOS build with PyInstaller..."
python -m PyInstaller --noconfirm --onedir \
    --name "Programs Manager User Generator" \
    --add-data "user-generator/lib:lib" \
    --add-data "src/assets/icon/icon.ico:src/assets/icon" \
    --collect-all customtkinter \
    --collect-all psutil \
    --noupx \
    "main.py"

echo
echo "Build completed successfully!"
echo "Executable directory: dist/Programs Manager User Generator/"
