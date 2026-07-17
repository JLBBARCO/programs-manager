# Repository info
$owner = "JLBBARCO"
$repo = "programs-manager"

# Set this script's branch. When this file is fetched from:
#  - https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1  -> set to 'main'
#  - https://raw.githubusercontent.com/JLBBARCO/programs-manager/develop/run.ps1 -> set to 'develop'
# The branch controls whether the script downloads the latest stable release (main)
# or the most-recent prerelease (develop). Allow an environment override for testing.
$ScriptBranch = if ($env:AIP_BRANCH) {
    $env:AIP_BRANCH
} elseif ($env:SCRIPT_BRANCH) {
    $env:SCRIPT_BRANCH
} else {
    'main'
}
$ScriptBranch = $ScriptBranch.Trim().ToLowerInvariant()
# Use the current user's profile directory (works on Windows reliably).
$installRoot = Join-Path $env:USERPROFILE ".programs-manager"
$expectedExePath = Join-Path $installRoot "Programs Manager\Programs Manager.exe"
$expectedVersionPath = Join-Path $installRoot "Programs Manager\version.txt"
$appName = "Programs Manager"
$assetName = "programs-manager-windows.zip"

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

    if ($Branch -eq 'develop') {
        $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases" -UseBasicParsing
        $release = $releases | Where-Object { $_.prerelease } | Sort-Object -Property published_at -Descending | Select-Object -First 1
        if (-not $release) {
            Write-Host "[programs-manager] No prerelease found; using the latest stable release." -ForegroundColor Yellow
            $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest" -UseBasicParsing
        }
    } else {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest" -UseBasicParsing
    }

    return $release
}

function Install-LatestRelease {
    param(
        $Release,
        [string]$Root
    )

    $asset = $Release.assets | Where-Object { $_.name -eq $assetName } | Select-Object -First 1
    if (-not $asset) {
        throw "Asset '$assetName' not found in the chosen release."
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

# 4. Fecha o terminal do PowerShell (Se estiver rodando via terminal)
if ($host.Name -eq 'ConsoleHost') {
    Write-Host "[programs-manager] Closing PowerShell terminal..."
    Start-Sleep -Seconds 1
    Stop-Process -Id $PID
}
