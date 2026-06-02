#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR_DEFAULT="/usr/local/Passwords Manager"
TARGET_DIR="${1:-${TARGET_DIR_DEFAULT}}"

if [ ! -d "${TARGET_DIR}" ] && [ -d "${HOME}/.local/share/Passwords Manager" ]; then
  TARGET_DIR="${HOME}/.local/share/Passwords Manager"
fi

if [ ! -d "${TARGET_DIR}" ]; then
  echo "Nothing to uninstall. Directory not found: ${TARGET_DIR}"
  exit 0
fi

echo "Removing ${TARGET_DIR}..."
if [ "$(id -u)" -ne 0 ] && [ "${TARGET_DIR}" = "${TARGET_DIR_DEFAULT}" ]; then
  sudo rm -rf "${TARGET_DIR}"
else
  rm -rf "${TARGET_DIR}"
fi

if [ "$(uname -s)" = "Linux" ]; then
  rm -f "${HOME}/.local/share/applications/passwords-manager.desktop"
  rm -f "${HOME}/.local/share/applications/passwords-manager-uninstall.desktop"
fi

if [ "$(uname -s)" = "Darwin" ]; then
  rm -f "${HOME}/Applications/Passwords Manager.command"
  rm -f "${HOME}/Applications/Uninstall Passwords Manager.command"
fi

echo "Uninstall completed."
