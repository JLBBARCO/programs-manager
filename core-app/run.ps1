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

# 1. Try local build first
$exePath = Resolve-LocalBuildPath
if ($exePath) {
    Write-Host "[programs-manager] Local build found: $exePath"
}

# 2. If no local build, try installed version
if (-not $exePath) {
    $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
}

# 3. If still not found, try to download
if (-not $exePath) {
    Write-Host "[programs-manager] Trying to download the compiled version for Windows..."

    try {
        # Decide which release to fetch based on the script branch.
        if ($ScriptBranch -eq 'develop') {
            # Find the most recent prerelease
            $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases" -UseBasicParsing
            $prerelease = $releases | Where-Object { $_.prerelease } | Sort-Object -Property published_at -Descending | Select-Object -First 1
            if ($prerelease) {
                $asset = $prerelease.assets | Where-Object { $_.name -eq "programs-manager-windows.zip" } | Select-Object -First 1
            }

            if (-not $asset) {
                Write-Host "[programs-manager] No prerelease found; using the latest stable release." -ForegroundColor Yellow
                $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest" -UseBasicParsing
                $asset = $release.assets | Where-Object { $_.name -eq "programs-manager-windows.zip" } | Select-Object -First 1
            }
        } else {
            # Stable channel: use latest stable release endpoint
            $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest" -UseBasicParsing
            $asset = $release.assets | Where-Object { $_.name -eq "programs-manager-windows.zip" } | Select-Object -First 1
        }

        if (-not $asset) {
            throw "Asset 'programs-manager-windows.zip' not found in the chosen release." 
        }

        $zipTemp = Join-Path $env:TEMP "aip_win.zip"
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipTemp -UseBasicParsing

        Expand-Archive -Path $zipTemp -DestinationPath $installRoot -Force
        Remove-Item $zipTemp -Force

        $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
    } catch {
        Write-Host "[programs-manager] Error downloading: $_" -ForegroundColor Yellow
        Write-Host "[programs-manager] Trying to compile locally..." -ForegroundColor Yellow

        # Try to compile locally as last resort
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
}

# Final check
if (-not $exePath -or -not (Test-Path $exePath)) {
    throw "Executable not found. Try run: python core-app/main.py ou .\core-app\build.bat"
}

# 2. Executa o binário diretamente (Sem Python, sem VENV)
Write-Host "[programs-manager] Running..."
Write-Host "[programs-manager] Executable: $exePath"
Set-WindowsShortcuts -ExePath $exePath
$exeWorkingDirectory = Split-Path -Parent $exePath
Start-Process -FilePath $exePath -WorkingDirectory $exeWorkingDirectory

# 3. Fecha o terminal do PowerShell (Se estiver rodando via terminal)
if ($host.Name -eq 'ConsoleHost') {
    Write-Host "[programs-manager] Closing PowerShell terminal..."
    Start-Sleep -Seconds 1
    Stop-Process -Id $PID
}
