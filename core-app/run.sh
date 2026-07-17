#!/usr/bin/env bash
owner="JLBBARCO"
repo="programs-manager"

# When this script is fetched from the 'develop' branch it should use the
# latest prerelease artifact; when fetched from 'main' it should use the
# latest stable release. Set here according to file branch.
SCRIPT_BRANCH="${AIP_BRANCH:-${SCRIPT_BRANCH:-main}}"
SCRIPT_BRANCH="$(printf '%s' "$SCRIPT_BRANCH" | tr '[:upper:]' '[:lower:]' | xargs)"

OS_TYPE=$(uname -s)
INSTALL_ROOT="${HOME}/.programs-manager"
APP_NAME="Programs Manager"
APP_SLUG="programs-manager"
mkdir -p "$INSTALL_ROOT"

if [ "$OS_TYPE" == "Linux" ]; then
    ASSET_PATTERN="programs-manager-linux.tar.gz"
    BINARY_NAME="Programs Manager/Programs Manager"
    VERSION_FILE_NAME="Programs Manager/version.txt"
fi

shell_quote() {
    printf "%q" "$1"
}

ensure_unix_shortcut() {
    local executable_path="$1"

    if [ -z "$executable_path" ] || [ ! -x "$executable_path" ]; then
        return 0
    fi

    if [ "$OS_TYPE" = "Linux" ]; then
        local app_dir="${HOME}/.local/share/applications"
        local shortcut_path="${app_dir}/${APP_SLUG}.desktop"
        mkdir -p "$app_dir"
        cat > "$shortcut_path" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=${APP_NAME}
Exec="${executable_path}"
Terminal=false
Categories=Utility;Security;
StartupWMClass=${APP_SLUG}
EOF
        chmod +x "$shortcut_path"
        echo "[programs-manager] Shortcut created: $shortcut_path"
    elif [ "$OS_TYPE" = "Darwin" ]; then
        local app_dir="${HOME}/Applications"
        local shortcut_path="${app_dir}/${APP_NAME}.command"
        local executable_dir
        executable_dir="$(dirname "$executable_path")"
        mkdir -p "$app_dir"
        cat > "$shortcut_path" <<EOF
#!/usr/bin/env bash
# ${APP_SLUG}
cd $(shell_quote "$executable_dir")
exec $(shell_quote "$executable_path")
EOF
        chmod +x "$shortcut_path"
        echo "[programs-manager] Shortcut created: $shortcut_path"
    fi
}

resolve_local_build() {
    local source_path
    source_path="${BASH_SOURCE[0]}"

    if [ -z "$source_path" ] || [ ! -f "$source_path" ]; then
        return 1
    fi

    local script_dir
    script_dir="$(cd "$(dirname "$source_path")" && pwd)"

    for candidate_dir in dist build; do
        local search_root="${script_dir}/${candidate_dir}"
        if [ -d "$search_root" ]; then
            local found_exe
            found_exe="$(find "$search_root" -type f \( -name "Programs Manager" -o -name "Programs Manager.exe" \) 2>/dev/null | sort -r | head -n 1)"
            if [ -n "$found_exe" ]; then
                printf '%s\n' "$found_exe"
                return 0
            fi
        fi
    done

    return 1
}

# Prints "download_url<TAB>tag_name" for the release that should be used
# (latest prerelease on develop, latest stable release otherwise).
fetch_release_info() {
    local asset_pattern="$1"

    if [ "$SCRIPT_BRANCH" = "develop" ]; then
        if command -v python3 >/dev/null 2>&1; then
            python3 - "$owner" "$repo" "$asset_pattern" <<'PY'
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
        return 1
    fi

    if command -v python3 >/dev/null 2>&1; then
        python3 - "$owner" "$repo" "$asset_pattern" <<'PY'
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
    json_data="$(curl -fsSL "https://api.github.com/repos/$owner/$repo/releases/latest")"
    url="$(printf '%s' "$json_data" | grep "browser_download_url" | grep "$asset_pattern" | head -n1 | cut -d '"' -f4)"
    tag="$(printf '%s' "$json_data" | grep '"tag_name"' | head -n1 | cut -d '"' -f4)"
    if [ -z "$url" ]; then
        return 1
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
    echo "[programs-manager] Downloading native binary for $OS_TYPE..."
    rm -rf "$INSTALL_ROOT"
    mkdir -p "$INSTALL_ROOT"
    curl -L "$url" -o "$INSTALL_ROOT/temp.tar.gz"
    tar -xzf "$INSTALL_ROOT/temp.tar.gz" -C "$INSTALL_ROOT"
    rm -f "$INSTALL_ROOT/temp.tar.gz"
}

LOCAL_BUILD_PATH="$(resolve_local_build 2>/dev/null || true)"
if [ -n "$LOCAL_BUILD_PATH" ]; then
    echo "[programs-manager] Local build found: $LOCAL_BUILD_PATH"
    ensure_unix_shortcut "$LOCAL_BUILD_PATH"
    exec "$LOCAL_BUILD_PATH"
fi

# Busca e baixa apenas se o programa ainda não existir
if [ ! -x "$INSTALL_ROOT/$BINARY_NAME" ]; then
    echo "[programs-manager] Program not found. Downloading the latest version..."
    RELEASE_INFO="$(fetch_release_info "$ASSET_PATTERN" || true)"
    if [ -z "$RELEASE_INFO" ]; then
        echo "[programs-manager] Error: could not locate the asset for $ASSET_PATTERN"
        exit 1
    fi
    URL="$(printf '%s' "$RELEASE_INFO" | cut -f1)"
    download_and_install "$URL"
else
    echo "[programs-manager] Installed program found. Checking version..."
    LOCAL_VERSION="$(get_local_version "$INSTALL_ROOT/$VERSION_FILE_NAME" || true)"
    RELEASE_INFO="$(fetch_release_info "$ASSET_PATTERN" || true)"

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

# Executa
ensure_unix_shortcut "$INSTALL_ROOT/$BINARY_NAME"
exec "$INSTALL_ROOT/$BINARY_NAME"

# Fecha o terminal do shell (Se estiver rodando via terminal)
if [ -n "$PS1" ]; then
    echo "[programs-manager] Closing terminal..."
    sleep 1
    kill -9 $PPID
fi
