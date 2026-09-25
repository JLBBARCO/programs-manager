#!/usr/bin/env bash
set -euo pipefail

OWNER="JLBBARCO"
REPO="programs-manager"
BRANCH="${AIP_BRANCH:-${SCRIPT_BRANCH:-main}}"
BRANCH="$(printf '%s' "$BRANCH" | tr '[:upper:]' '[:lower:]' | xargs)"
APP_NAME="Programs Manager"
WORK_ROOT="$(mktemp -d)"
cleanup() { rm -rf "$WORK_ROOT"; }
trap cleanup EXIT

find_python() {
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 12))' >/dev/null 2>&1; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

PYTHON="$(find_python || true)"
if [ -z "$PYTHON" ]; then
    echo "[$APP_NAME] Python 3.12+ not found. Installing Python from the terminal..."
    if command -v apt-get >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then apt-get update && apt-get install -y python3 python3-pip python3-tk
        else sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-tk; fi
    elif command -v dnf >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then dnf install -y python3 python3-pip python3-tkinter
        else sudo dnf install -y python3 python3-pip python3-tkinter; fi
    elif command -v pacman >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then pacman -Sy --noconfirm python python-pip tk
        else sudo pacman -Sy --noconfirm python python-pip tk; fi
    elif command -v brew >/dev/null 2>&1; then
        brew install python@3.12 tcl-tk
    else
        echo "[$APP_NAME] No supported package manager found. Install Python 3.12+ and run this script again." >&2
        exit 1
    fi
    PYTHON="$(find_python || true)"
    if [ -z "$PYTHON" ]; then echo "[$APP_NAME] Python installation failed." >&2; exit 1; fi
fi

SCRIPT_PATH="${BASH_SOURCE[0]:-}"
PROJECT_ROOT=""
if [ -n "$SCRIPT_PATH" ] && [ -f "$SCRIPT_PATH" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
    if [ -f "$SCRIPT_DIR/main.py" ]; then PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"; fi
fi

if [ -z "$PROJECT_ROOT" ]; then
    echo "[$APP_NAME] Downloading Python source ($BRANCH)..."
    curl -fsSL "https://github.com/$OWNER/$REPO/archive/refs/heads/$BRANCH.tar.gz" -o "$WORK_ROOT/source.tar.gz"
    tar -xzf "$WORK_ROOT/source.tar.gz" -C "$WORK_ROOT"
    PROJECT_ROOT="$(find "$WORK_ROOT" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
fi

echo "[$APP_NAME] Installing runtime dependencies..."
VENV_PATH="${XDG_DATA_HOME:-$HOME/.local/share}/programs-manager/venv"
if [ ! -x "$VENV_PATH/bin/python" ]; then "$PYTHON" -m venv "$VENV_PATH"; fi
RUNTIME_PYTHON="$VENV_PATH/bin/python"
"$RUNTIME_PYTHON" -m pip install -r "$PROJECT_ROOT/requirements.txt"
echo "[$APP_NAME] Starting interpreted Python app..."
"$RUNTIME_PYTHON" "$PROJECT_ROOT/core-app/main.py"
