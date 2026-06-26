#!/usr/bin/env bash
set -euo pipefail

REPO="JLBBARCO/programs-manager-user-generator"
APP_NAME="Programs Manager User Generator"

case "$(uname -s)" in
    Linux*) ASSET="programs-manager-user-generator-linux.tar.gz" ;;
    Darwin*) ASSET="programs-manager-user-generator-macos.tar.gz" ;;
    *)
        echo "Unsupported operating system. Use run.ps1 on Windows."
        exit 1
        ;;
esac

if command -v curl >/dev/null 2>&1; then
    DOWNLOAD_CMD=(curl -fL)
elif command -v wget >/dev/null 2>&1; then
    DOWNLOAD_CMD=(wget -O -)
else
    echo "curl or wget is required to download the latest release."
    exit 1
fi

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

echo "Downloading latest ${APP_NAME} release..."
"${DOWNLOAD_CMD[@]}" "https://github.com/${REPO}/releases/latest/download/${ASSET}" > "${WORKDIR}/${ASSET}"

tar -xzf "${WORKDIR}/${ASSET}" -C "${WORKDIR}"

EXECUTABLE="${WORKDIR}/${APP_NAME}/${APP_NAME}"
if [ ! -x "$EXECUTABLE" ]; then
    EXECUTABLE="$(find "$WORKDIR" -type f -name "$APP_NAME" -perm -111 | head -n 1)"
fi

if [ -z "${EXECUTABLE:-}" ] || [ ! -f "$EXECUTABLE" ]; then
    echo "Executable not found in downloaded release."
    exit 1
fi

chmod +x "$EXECUTABLE"
"$EXECUTABLE" "$@"
