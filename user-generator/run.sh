#!/usr/bin/env bash
set -euo pipefail

REPO="JLBBARCO/programs-manager"
APP_NAME="Programs Manager User Generator"
SCRIPT_BRANCH="${AIP_BRANCH:-${SCRIPT_BRANCH:-main}}"
SCRIPT_BRANCH="$(printf '%s' "$SCRIPT_BRANCH" | tr '[:upper:]' '[:lower:]' | xargs)"

case "$(uname -s)" in
    Linux*) ASSET="programs-manager-user-generator-linux.tar.gz" ;;
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
if [ "$SCRIPT_BRANCH" = "develop" ]; then
    if command -v python3 >/dev/null 2>&1; then
        URL=$(python3 - "$REPO" "$ASSET" <<'PY'
import json
import sys
import urllib.request

repo, asset_name = sys.argv[1:3]
with urllib.request.urlopen(f"https://api.github.com/repos/{repo}/releases") as response:
    releases = json.load(response)

for release in sorted((r for r in releases if r.get("prerelease")), key=lambda r: r.get("published_at") or "", reverse=True):
    for asset in release.get("assets", []):
        if asset.get("name") == asset_name:
            print(asset.get("browser_download_url", ""))
            raise SystemExit(0)

raise SystemExit(1)
PY
)
    else
        URL=""
    fi
else
    URL="https://github.com/${REPO}/releases/latest/download/${ASSET}"
fi

if [ -z "${URL:-}" ]; then
    URL="https://github.com/${REPO}/releases/latest/download/${ASSET}"
fi

"${DOWNLOAD_CMD[@]}" "$URL" > "${WORKDIR}/${ASSET}"

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
