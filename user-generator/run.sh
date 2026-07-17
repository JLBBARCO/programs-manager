#!/usr/bin/env bash
set -euo pipefail

OWNER="JLBBARCO"
REPO="programs-manager"
APP_NAME="Programs Manager User Generator"
APP_SLUG="programs-manager-user-generator"
SCRIPT_BRANCH="${AIP_BRANCH:-${SCRIPT_BRANCH:-main}}"
SCRIPT_BRANCH="$(printf '%s' "$SCRIPT_BRANCH" | tr '[:upper:]' '[:lower:]' | xargs)"

case "$(uname -s)" in
    Linux*) ASSET="programs-manager-user-generator-linux.tar.gz" ;;
    *)
        echo "Unsupported operating system. Use run.ps1 on Windows."
        exit 1
        ;;
esac

# Use a persistent install directory so the program does not need to be
# re-downloaded on every run.
INSTALL_ROOT="${HOME}/.${APP_SLUG}"
BINARY_NAME="${APP_NAME}/${APP_NAME}"
VERSION_FILE_NAME="${APP_NAME}/version.txt"
mkdir -p "$INSTALL_ROOT"

if command -v curl >/dev/null 2>&1; then
    DOWNLOAD_CMD=(curl -fL)
elif command -v wget >/dev/null 2>&1; then
    DOWNLOAD_CMD=(wget -O -)
else
    echo "curl or wget is required to download the latest release."
    exit 1
fi

# Prints "download_url<TAB>tag_name" for the release that should be used
# (latest prerelease on develop, latest stable release otherwise).
fetch_release_info() {
    local asset_pattern="$1"

    if [ "$SCRIPT_BRANCH" = "develop" ]; then
        if command -v python3 >/dev/null 2>&1; then
            python3 - "$OWNER" "$REPO" "$asset_pattern" <<'PY'
import json
import sys
import urllib.request

owner, repo, asset_pattern = sys.argv[1:4]
api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"

with urllib.request.urlopen(api_url) as response:
    releases = json.load(response)

prereleases = [r for r in releases if r.get("prerelease")]
prereleases.sort(key=lambda r: r.get("published_at") or "", reverse=True)

for release in prereleases:
    for asset in release.get("assets", []):
        if asset.get("name") == asset_pattern:
            print(f"{asset.get('browser_download_url', '')}\t{release.get('tag_name', '')}")
            raise SystemExit(0)

raise SystemExit(1)
PY
            return $?
        fi
        printf '%s\t\n' "https://github.com/${OWNER}/${REPO}/releases/latest/download/${asset_pattern}"
        return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
        python3 - "$OWNER" "$REPO" "$asset_pattern" <<'PY'
import json
import sys
import urllib.request

owner, repo, asset_pattern = sys.argv[1:4]
api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

with urllib.request.urlopen(api_url) as response:
    release = json.load(response)

for asset in release.get("assets", []):
    if asset.get("name") == asset_pattern:
        print(f"{asset.get('browser_download_url', '')}\t{release.get('tag_name', '')}")
        raise SystemExit(0)

raise SystemExit(1)
PY
        return $?
    fi

    local json_data url tag
    json_data="$(curl -fsSL "https://api.github.com/repos/$OWNER/$REPO/releases/latest")"
    url="$(printf '%s' "$json_data" | grep "browser_download_url" | grep "$asset_pattern" | head -n1 | cut -d '"' -f4)"
    tag="$(printf '%s' "$json_data" | grep '"tag_name"' | head -n1 | cut -d '"' -f4)"
    if [ -z "$url" ]; then
        url="https://github.com/${OWNER}/${REPO}/releases/latest/download/${asset_pattern}"
    fi
    printf '%s\t%s\n' "$url" "$tag"
    return 0
}

get_local_version() {
    local version_file="$1"
    if [ ! -f "$version_file" ]; then
        return 1
    fi
    local value
    value="$(grep -m1 '^system_version=' "$version_file" | cut -d '=' -f2- | tr -d '\r' | xargs)"
    if [ -z "$value" ]; then
        return 1
    fi
    printf '%s\n' "$value"
}

# Strips the leading 'v' from a tag, e.g. v3.02.4 -> 3.02.4
normalize_version() {
    printf '%s' "$1" | sed 's/^[vV]//'
}

download_and_install() {
    local url="$1"
    echo "[programs-manager] Downloading latest ${APP_NAME} release..."
    rm -rf "$INSTALL_ROOT"
    mkdir -p "$INSTALL_ROOT"
    "${DOWNLOAD_CMD[@]}" "$url" > "${INSTALL_ROOT}/${ASSET}"
    tar -xzf "${INSTALL_ROOT}/${ASSET}" -C "$INSTALL_ROOT"
    rm -f "${INSTALL_ROOT}/${ASSET}"
}

# Busca e baixa apenas se o programa ainda não existir
if [ ! -x "$INSTALL_ROOT/$BINARY_NAME" ]; then
    echo "[programs-manager] Program not found. Downloading the latest version..."
    RELEASE_INFO="$(fetch_release_info "$ASSET" || true)"
    if [ -z "$RELEASE_INFO" ]; then
        echo "[programs-manager] Error: could not locate the asset for $ASSET"
        exit 1
    fi
    URL="$(printf '%s' "$RELEASE_INFO" | cut -f1)"
    download_and_install "$URL"
else
    echo "[programs-manager] Installed program found. Checking version..."
    LOCAL_VERSION="$(get_local_version "$INSTALL_ROOT/$VERSION_FILE_NAME" || true)"
    RELEASE_INFO="$(fetch_release_info "$ASSET" || true)"

    if [ -n "$RELEASE_INFO" ]; then
        URL="$(printf '%s' "$RELEASE_INFO" | cut -f1)"
        TAG="$(printf '%s' "$RELEASE_INFO" | cut -f2)"
        LATEST_VERSION="$(normalize_version "$TAG")"

        if [ -z "$LOCAL_VERSION" ]; then
            echo "[programs-manager] version.txt not found in the installed copy. Updating to the latest version..."
            download_and_install "$URL"
        elif [ -n "$LATEST_VERSION" ] && [ "$LOCAL_VERSION" != "$LATEST_VERSION" ]; then
            echo "[programs-manager] New version available ($LATEST_VERSION). Updating from $LOCAL_VERSION..."
            download_and_install "$URL"
        else
            echo "[programs-manager] Program is up to date (version $LOCAL_VERSION)."
        fi
    else
        echo "[programs-manager] Could not check for updates. Using the installed version."
    fi
fi

EXECUTABLE="$INSTALL_ROOT/$BINARY_NAME"
if [ ! -x "$EXECUTABLE" ]; then
    EXECUTABLE="$(find "$INSTALL_ROOT" -type f -name "$APP_NAME" -perm -111 | head -n 1)"
fi

if [ -z "${EXECUTABLE:-}" ] || [ ! -f "$EXECUTABLE" ]; then
    echo "Executable not found in the installed copy."
    exit 1
fi

chmod +x "$EXECUTABLE"

# Executa
"$EXECUTABLE" "$@"

# Fecha o terminal do shell (Se estiver rodando via terminal)
if [ -n "${PS1:-}" ]; then
    echo "[programs-manager] Closing terminal..."
    sleep 1
    kill -9 $PPID
fi
