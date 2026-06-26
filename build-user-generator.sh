#!/usr/bin/env bash
set -euo pipefail

echo "Cleaning old builds..."
rm -rf dist build "Programs Manager User Generator.spec"

echo "Installing required dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Starting Linux build with PyInstaller..."
python -m PyInstaller --noconfirm --onedir \
    --name "Programs Manager User Generator" \
    --paths "user-generator" \
    --add-data "user-generator/lib:lib" \
    --add-data "src/assets/icon/icon.ico:src/assets/icon" \
    --collect-all customtkinter \
    --collect-all psutil \
    --noupx \
    "user-generator/main.py"

echo
echo "Build completed successfully!"
echo "Executable directory: dist/Programs Manager User Generator/"
