#!/usr/bin/env bash
set -euo pipefail

OWNER="JLBBARCO"
REPO="auto-programs"
BRANCH="${AIP_BRANCH:-main}"

INSTALL_ROOT="${HOME}/.auto-install-programs"
STAGE_DIR="${INSTALL_ROOT}/src"
ARCHIVE_URL="https://codeload.github.com/${OWNER}/${REPO}/tar.gz/refs/heads/${BRANCH}"
TMP_FILE="$(mktemp)"

echo "[quick-run] Updating source from ${BRANCH}..."
mkdir -p "${INSTALL_ROOT}"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "${ARCHIVE_URL}" -o "${TMP_FILE}"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "${TMP_FILE}" "${ARCHIVE_URL}"
else
  echo "curl or wget is required to download the source."
  exit 1
fi

rm -rf "${STAGE_DIR}"
tar -xzf "${TMP_FILE}" -C "${INSTALL_ROOT}"
rm -f "${TMP_FILE}"

EXTRACTED_DIR="${INSTALL_ROOT}/${REPO}-${BRANCH}"
if [ ! -d "${EXTRACTED_DIR}" ]; then
  echo "Could not find extracted directory: ${EXTRACTED_DIR}"
  exit 1
fi

mv "${EXTRACTED_DIR}" "${STAGE_DIR}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python 3 not found. Install Python and try again."
  exit 1
fi

MAIN_PY="${STAGE_DIR}/main.py"
REQ_FILE="${STAGE_DIR}/requirements.txt"
VENV_DIR="${STAGE_DIR}/.venv"
VENV_PY="${VENV_DIR}/bin/python"

if [ ! -f "${MAIN_PY}" ]; then
  echo "main.py not found in ${STAGE_DIR}"
  exit 1
fi

if [ ! -x "${VENV_PY}" ]; then
  echo "[quick-run] Creating .venv..."
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

echo "[quick-run] Installing dependencies..."
"${VENV_PY}" -m pip install --upgrade pip
if [ -f "${REQ_FILE}" ]; then
  "${VENV_PY}" -m pip install -r "${REQ_FILE}"
fi

echo "[quick-run] Launching app..."
"${VENV_PY}" "${MAIN_PY}"
