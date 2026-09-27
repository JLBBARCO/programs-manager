# Repository info
$owner = "JLBBARCO"
$repo = "programs-manager"


# Install Python 3.12 if not present
if (-not (Get-Command python3.12 -ErrorAction SilentlyContinue)) {
    Write-Host "[programs-manager] Python 3.12 not found. Installing..."
    winget install --id=Python.Python.3.12 -e --source winget
}


# Set this script's branch. When this file is fetched from:
#  - https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1  -> set to 'main'
#  - https://raw.githubusercontent.com/JLBBARCO/programs-manager/beta/run.ps1 -> set to 'beta'
# The branch controls whether the script downloads the latest stable release (main)
# or the most-recent prerelease (beta). Allow an environment override for testing.
$ScriptBranch = if ($env:AIP_BRANCH) {
    $env:AIP_BRANCH
} elseif ($env:SCRIPT_BRANCH) {
    $env:SCRIPT_BRANCH
} else {
    'main'
}
$ScriptBranch = $ScriptBranch.Trim().ToLowerInvariant()
$RequestedVersion = if ($env:AIP_VERSION) { $env:AIP_VERSION.Trim().TrimStart('v', 'V') } else { $null }

$architecture = if ($env:AIP_ARCHITECTURE) {
    $env:AIP_ARCHITECTURE.Trim().ToLowerInvariant()
} elseif ($env:PROCESSOR_ARCHITEW6432) {
    $env:PROCESSOR_ARCHITEW6432.Trim().ToLowerInvariant()
} else {
    $env:PROCESSOR_ARCHITECTURE.Trim().ToLowerInvariant()
}

if ($architecture -in @('x86', 'i386', 'i686')) {
    $assetName = "programs-manager-windows-x86.zip"
} else {
    $assetName = "programs-manager-windows-x64.zip"
}

# Use the current user's profile directory (works on Windows reliably).
$installRoot = Join-Path $env:USERPROFILE ".programs-manager"
$expectedExePath = Join-Path $installRoot "Programs Manager\Programs Manager.exe"
$expectedVersionPath = Join-Path $installRoot "Programs Manager\version.txt"
$appName = "Programs Manager"

Write-Host "[programs-manager] Script em execução: $PSCommandPath"

function Resolve-ExePath {
    param(
        [string]$Root,
        [string]$ExpectedPath
    )

    if (Test-Path $ExpectedPath) {
        return $ExpectedPath
    }

    $foundExe = Get-ChildItem -Path $Root -Filter "Programs Manager.exe" -Recurse -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($foundExe) {
        return $foundExe.FullName
    }

    return $null
}

function Get-LocalVersion {
    param(
        [string]$VersionPath
    )

    if (-not (Test-Path $VersionPath)) {
        return $null
    }

    $content = Get-Content -Path $VersionPath -Raw -ErrorAction SilentlyContinue
    if ($content -match 'system_version\s*=\s*([^\r\n]+)') {
        return $matches[1].Trim()
    }

    return $null
}

function Get-VersionFromTag {
    param(
        [string]$TagName
    )

    if ([string]::IsNullOrWhiteSpace($TagName)) {
        return $null
    }

    return $TagName.TrimStart('v', 'V')
}

function Get-LatestRelease {
    param(
        [string]$Branch
    )

    if ($RequestedVersion) {
        return Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/tags/v$RequestedVersion" -UseBasicParsing
    }

    $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases?per_page=100" -UseBasicParsing
    $candidateReleases = if ($Branch -in @('beta', 'develop')) {
        $releases | Where-Object { $_.prerelease -and -not $_.draft }
    } else {
        $releases | Where-Object { -not $_.prerelease -and -not $_.draft }
    }

    $release = $candidateReleases |
        Sort-Object -Property published_at -Descending |
        Where-Object { Get-WindowsAsset -Release $_ } |
        Select-Object -First 1

    if (-not $release -and $Branch -in @('beta', 'develop')) {
        Write-Host "[programs-manager] No prerelease with a Windows application asset found; using the latest stable release." -ForegroundColor Yellow
        $release = ($releases |
            Where-Object { -not $_.prerelease -and -not $_.draft } |
            Sort-Object -Property published_at -Descending |
            Where-Object { Get-WindowsAsset -Release $_ } |
            Select-Object -First 1)
    }

    if (-not $release) {
        throw "No release with a compatible Windows application asset was found."
    }

    return $release
}

function Get-WindowsAsset {
    param(
        $Release
    )

    $asset = $Release.assets |
        Where-Object { $_.name -eq $assetName } |
        Select-Object -First 1

    if (-not $asset) {
        $asset = $Release.assets |
            Where-Object { $_.name -eq 'programs-manager-windows.zip' } |
            Select-Object -First 1
    }

    return $asset
}

function Install-LatestRelease {
    param(
        $Release,
        [string]$Root
    )

    $asset = Get-WindowsAsset -Release $Release
    if (-not $asset) {
        throw "No compatible Windows application asset found in release '$($Release.tag_name)'. Expected '$assetName' or 'programs-manager-windows.zip'."
    }

    $zipTemp = Join-Path $env:TEMP "aip_win.zip"
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipTemp -UseBasicParsing

    if (Test-Path $Root) {
        Remove-Item -Path $Root -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Root -Force | Out-Null

    Expand-Archive -Path $zipTemp -DestinationPath $Root -Force
    Remove-Item $zipTemp -Force
}

function Set-WindowsShortcuts {
    param(
        [string]$ExePath
    )

    if (-not $ExePath -or -not (Test-Path $ExePath)) {
        return
    }

    $shortcutDirectories = @()
    if ($env:APPDATA) {
        $shortcutDirectories += Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
    }
    if ($env:USERPROFILE) {
        $shortcutDirectories += Join-Path $env:USERPROFILE "Desktop"
    }

    foreach ($shortcutDirectory in $shortcutDirectories) {
        try {
            New-Item -ItemType Directory -Path $shortcutDirectory -Force | Out-Null
            $shortcutPath = Join-Path $shortcutDirectory "$appName.lnk"
            $shell = New-Object -ComObject WScript.Shell
            $shortcut = $shell.CreateShortcut($shortcutPath)
            $shortcut.TargetPath = $ExePath
            $shortcut.Arguments = ""
            $shortcut.WorkingDirectory = Split-Path -Parent $ExePath
            $shortcut.IconLocation = $ExePath
            $shortcut.Save()
            Write-Host "[programs-manager] Shortcut created: $shortcutPath"
        } catch {
            Write-Host "[programs-manager] Failed to create shortcut in '$shortcutDirectory': $_" -ForegroundColor Yellow
        }
    }
}

function Resolve-LocalBuildPath {
    # Try to find the local build from the project directory
    # When script is executed via iex, $PSCommandPath may be null; use $MyInvocation as fallback
    $scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }

    if (-not $scriptPath) {
        # Script location unknown (likely executed via iex from web), skip local build check
        return $null
    }

    $scriptDir = Split-Path -Parent $scriptPath
    foreach ($candidateDir in @("dist", "build")) {
        $searchRoot = Join-Path $scriptDir $candidateDir

        if (Test-Path $searchRoot) {
            $foundExe = Get-ChildItem -Path $searchRoot -Filter "Programs Manager.exe" -Recurse -File -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1

            if ($foundExe) {
                return $foundExe.FullName
            }
        }
    }

    return $null
}

New-Item -ItemType Directory -Path $installRoot -Force | Out-Null

# 1. Try local build first (development convenience, skips install/update checks)
$exePath = Resolve-LocalBuildPath
if ($exePath) {
    Write-Host "[programs-manager] Local build found: $exePath"
}

# 2. If no local build, check whether the program is already installed
if (-not $exePath) {
    $installedExePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath

    if (-not $installedExePath) {
        # 2a. Not installed yet -> download the latest available version
        Write-Host "[programs-manager] Program not found. Downloading the latest version for Windows..."
        try {
            $release = Get-LatestRelease -Branch $ScriptBranch
            Install-LatestRelease -Release $release -Root $installRoot
            $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
        } catch {
            Write-Host "[programs-manager] Error downloading: $_" -ForegroundColor Yellow
            Write-Host "[programs-manager] Trying to compile locally..." -ForegroundColor Yellow

            $scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }
            if ($scriptPath) {
                $scriptDir = Split-Path -Parent $scriptPath
                $buildScript = Join-Path $scriptDir "build.bat"
                if (Test-Path $buildScript) {
                    Write-Host "[programs-manager] Run build.bat..."
                    & $buildScript
                    $exePath = Resolve-LocalBuildPath
                }
            }
        }
    } else {
        # 2b. Already installed -> verify version.txt and update if necessary
        Write-Host "[programs-manager] Installed program found. Checking version..."
        $exePath = $installedExePath
        try {
            $localVersion = Get-LocalVersion -VersionPath $expectedVersionPath
            $release = Get-LatestRelease -Branch $ScriptBranch
            $latestVersion = Get-VersionFromTag -TagName $release.tag_name

            if (-not $localVersion) {
                Write-Host "[programs-manager] version.txt not found in the installed copy. Updating to the latest version..."
                Install-LatestRelease -Release $release -Root $installRoot
                $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
            } elseif ($latestVersion -and ($localVersion -ne $latestVersion)) {
                Write-Host "[programs-manager] New version available ($latestVersion). Updating from $localVersion..."
                Install-LatestRelease -Release $release -Root $installRoot
                $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
            } else {
                Write-Host "[programs-manager] Program is up to date (version $localVersion)."
            }
        } catch {
            Write-Host "[programs-manager] Could not check for updates: $_" -ForegroundColor Yellow
            Write-Host "[programs-manager] Using the installed version." -ForegroundColor Yellow
        }
    }
}

# Final check
if (-not $exePath -or -not (Test-Path $exePath)) {
    throw "Executable not found. Try run: python core-app/main.py ou .\core-app\build.bat"
}

# 3. Executa o binário diretamente (Sem Python, sem VENV)
Write-Host "[programs-manager] Running..."
Write-Host "[programs-manager] Executable: $exePath"
Set-WindowsShortcuts -ExePath $exePath
$exeWorkingDirectory = Split-Path -Parent $exePath
Start-Process -FilePath $exePath -WorkingDirectory $exeWorkingDirectory
