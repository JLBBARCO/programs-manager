$ErrorActionPreference = "Stop"

$owner = "JLBBARCO"
$repo = "programs-manager"
$appName = "Programs Manager User Generator"
$assetName = "programs-manager-user-generator-windows.zip"
$scriptBranch = if ($env:AIP_BRANCH) {
    $env:AIP_BRANCH
} elseif ($env:SCRIPT_BRANCH) {
    $env:SCRIPT_BRANCH
} else {
    "main"
}
$scriptBranch = $scriptBranch.Trim().ToLowerInvariant()

# Use the current user's profile directory so the install persists between runs.
$installRoot = Join-Path $env:USERPROFILE ".programs-manager-user-generator"
$expectedExePath = Join-Path $installRoot "$appName\$appName.exe"
$expectedVersionPath = Join-Path $installRoot "$appName\version.txt"

function Resolve-ExePath {
    param(
        [string]$Root,
        [string]$ExpectedPath
    )

    if (Test-Path $ExpectedPath) {
        return $ExpectedPath
    }

    $foundExe = Get-ChildItem -Path $Root -Filter "$appName.exe" -Recurse -File -ErrorAction SilentlyContinue |
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

    if ($Branch -eq "develop") {
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

    $releaseAsset = $Release.assets | Where-Object { $_.name -eq $assetName } | Select-Object -First 1
    $downloadUrl = if ($releaseAsset) {
        $releaseAsset.browser_download_url
    } else {
        "https://github.com/$owner/$repo/releases/latest/download/$assetName"
    }

    $zipTemp = Join-Path ([System.IO.Path]::GetTempPath()) ("pmug-" + [System.Guid]::NewGuid().ToString("N") + ".zip")

    Write-Host "[programs-manager] Downloading latest $appName release..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipTemp -UseBasicParsing

    if (Test-Path $Root) {
        Remove-Item -Path $Root -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Root -Force | Out-Null

    Expand-Archive -Path $zipTemp -DestinationPath $Root -Force
    Remove-Item $zipTemp -Force
}

New-Item -ItemType Directory -Path $installRoot -Force | Out-Null

# 1. Check whether the program is already installed
$exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath

if (-not $exePath) {
    # 1a. Not installed yet -> download the latest available version
    Write-Host "[programs-manager] Program not found. Downloading the latest version for Windows..."
    $release = Get-LatestRelease -Branch $scriptBranch
    Install-LatestRelease -Release $release -Root $installRoot
    $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
} else {
    # 1b. Already installed -> verify version.txt and update if necessary
    Write-Host "[programs-manager] Installed program found. Checking version..."
    try {
        $localVersion = Get-LocalVersion -VersionPath $expectedVersionPath
        $release = Get-LatestRelease -Branch $scriptBranch
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

if (-not $exePath -or -not (Test-Path $exePath)) {
    throw "Executable not found. Try running .\user-generator\build.bat"
}

# 2. Executa o binário instalado
Write-Host "[programs-manager] Running..."
Write-Host "[programs-manager] Executable: $exePath"

$startOptions = @{
    FilePath = $exePath
    WorkingDirectory = Split-Path -Parent $exePath
    Wait = $true
    PassThru = $true
}

if ($args.Count -gt 0) {
    $startOptions.ArgumentList = $args
}

$process = Start-Process @startOptions
$exitCode = $process.ExitCode

# 3. Fecha o terminal do PowerShell (Se estiver rodando via terminal)
if ($host.Name -eq 'ConsoleHost') {
    Write-Host "[programs-manager] Closing PowerShell terminal..."
    Start-Sleep -Seconds 1
    Stop-Process -Id $PID
}

if ($exitCode -ne 0) {
    exit $exitCode
}
