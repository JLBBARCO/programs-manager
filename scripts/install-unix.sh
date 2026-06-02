#!/usr/bin/env bash
set -euo pipefail

OWNER="JLBBARCO"
REPO="passwords-manager"
API_URL="https://api.github.com/repos/${OWNER}/${REPO}/releases/latest"

if command -v curl >/dev/null 2>&1; then
  fetch() { curl -fsSL "$1"; }
  download() { curl -fL "$1" -o "$2"; }
elif command -v wget >/dev/null 2>&1; then
  fetch() { wget -qO- "$1"; }
  download() { wget -qO "$2" "$1"; }
else
  echo "Error: curl or wget is required." >&2
  exit 1
fi

OS_NAME="$(uname -s)"
ASSET_NAME=""
case "${OS_NAME}" in
  Linux)
    ASSET_NAME="passwords-manager-linux.tar.gz"
    ;;
  Darwin)
    ASSET_NAME="passwords-manager-macos.tar.gz"
    ;;
  *)
    echo "Error: unsupported OS: ${OS_NAME}" >&2
    exit 1
    ;;
esac

TARGET_DIR_DEFAULT="/usr/local/Passwords Manager"
TARGET_DIR="${1:-${TARGET_DIR_DEFAULT}}"
if [ ! -w "$(dirname "${TARGET_DIR}")" ] && [ "$(id -u)" -ne 0 ]; then
  TARGET_DIR="${HOME}/.local/share/Passwords Manager"
fi

TMP_DIR="$(mktemp -d)"
ARCHIVE_FILE="${TMP_DIR}/${ASSET_NAME}"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "Resolving latest release for ${OWNER}/${REPO}..."
ASSET_URL="$(fetch "${API_URL}" | grep -o "https://[^[:space:]]*${ASSET_NAME}" | head -n 1)"
if [ -z "${ASSET_URL}" ]; then
  echo "Error: could not find asset ${ASSET_NAME} in latest release." >&2
  exit 1
fi

echo "Downloading ${ASSET_NAME}..."
download "${ASSET_URL}" "${ARCHIVE_FILE}"

echo "Installing to ${TARGET_DIR}..."
if [ "$(id -u)" -ne 0 ] && [ "${TARGET_DIR}" = "${TARGET_DIR_DEFAULT}" ]; then
  sudo mkdir -p "${TARGET_DIR}"
  sudo tar -xzf "${ARCHIVE_FILE}" -C "${TARGET_DIR}"
  sudo chmod +x "${TARGET_DIR}/passwords-manager" || true
else
  mkdir -p "${TARGET_DIR}"
  tar -xzf "${ARCHIVE_FILE}" -C "${TARGET_DIR}"
  chmod +x "${TARGET_DIR}/passwords-manager" || true
fi

cat > "${TARGET_DIR}/uninstall.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Removing ${INSTALL_DIR}..."
rm -rf "${INSTALL_DIR}"
echo "Uninstall completed."
EOF
chmod +x "${TARGET_DIR}/uninstall.sh"

if [ "${OS_NAME}" = "Linux" ]; then
  APP_DIR="${HOME}/.local/share/applications"
  mkdir -p "${APP_DIR}"
  cat > "${APP_DIR}/passwords-manager.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Passwords Manager
Exec=${TARGET_DIR}/passwords-manager
Terminal=false
Categories=Utility;Security;
EOF

  cat > "${APP_DIR}/passwords-manager-uninstall.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Uninstall Passwords Manager
Exec=${TARGET_DIR}/uninstall.sh
Terminal=true
Categories=Utility;
EOF
fi

if [ "${OS_NAME}" = "Darwin" ]; then
  APP_DIR="${HOME}/Applications"
  mkdir -p "${APP_DIR}"

  cat > "${APP_DIR}/Passwords Manager.command" <<EOF
#!/bin/bash
"${TARGET_DIR}/passwords-manager"
EOF
  chmod +x "${APP_DIR}/Passwords Manager.command"

  cat > "${APP_DIR}/Uninstall Passwords Manager.command" <<EOF
#!/bin/bash
"${TARGET_DIR}/uninstall.sh"
EOF
  chmod +x "${APP_DIR}/Uninstall Passwords Manager.command"
fi

echo "Installed successfully."
echo "Run: ${TARGET_DIR}/passwords-manager"
