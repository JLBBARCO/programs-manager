$ErrorActionPreference = "Stop"

$repo = "JLBBARCO/programs-manager"
$appName = "Programs Manager User Generator"
$asset = "programs-manager-user-generator-windows.zip"
$scriptBranch = if ($env:AIP_BRANCH) {
    $env:AIP_BRANCH
} elseif ($env:SCRIPT_BRANCH) {
    $env:SCRIPT_BRANCH
} else {
    "main"
}
$scriptBranch = $scriptBranch.Trim().ToLowerInvariant()
$workdir = Join-Path ([System.IO.Path]::GetTempPath()) ("pmug-" + [System.Guid]::NewGuid().ToString("N"))
$archive = Join-Path $workdir $asset

try {
    New-Item -ItemType Directory -Path $workdir | Out-Null

    Write-Host "Downloading latest $appName release..."
    if ($scriptBranch -eq "develop") {
        $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases" -UseBasicParsing
        $prerelease = $releases | Where-Object { $_.prerelease } | Sort-Object -Property published_at -Descending | Select-Object -First 1
        $releaseAsset = if ($prerelease) {
            $prerelease.assets | Where-Object { $_.name -eq $asset } | Select-Object -First 1
        } else {
            $null
        }
        $downloadUrl = if ($releaseAsset) {
            $releaseAsset.browser_download_url
        } else {
            "https://github.com/$repo/releases/latest/download/$asset"
        }
    } else {
        $downloadUrl = "https://github.com/$repo/releases/latest/download/$asset"
    }

    Invoke-WebRequest `
        -Uri $downloadUrl `
        -OutFile $archive

    Expand-Archive -Path $archive -DestinationPath $workdir -Force

    $executable = Get-ChildItem -Path $workdir -Recurse -Filter "$appName.exe" |
        Select-Object -First 1

    if (-not $executable) {
        throw "Executable not found in downloaded release."
    }

    $startOptions = @{
        FilePath = $executable.FullName
        Wait = $true
        PassThru = $true
    }

    if ($args.Count -gt 0) {
        $startOptions.ArgumentList = $args
    }

    $process = Start-Process @startOptions
    if ($process.ExitCode -ne 0) {
        exit $process.ExitCode
    }
}
finally {
    if (Test-Path -LiteralPath $workdir) {
        for ($attempt = 1; $attempt -le 10; $attempt++) {
            try {
                Remove-Item -LiteralPath $workdir -Recurse -Force -ErrorAction Stop
                break
            }
            catch {
                if ($attempt -eq 10) {
                    Write-Warning "Could not remove temporary directory '$workdir': $($_.Exception.Message)"
                }
                else {
                    Start-Sleep -Milliseconds 500
                }
            }
        }
    }
}

# If the script is running in a console host, close the PowerShell terminal after execution
if ($host.Name -eq 'ConsoleHost') {
    Write-Host "[programs-manager] Closing PowerShell terminal..."
    Start-Sleep -Seconds 1
    Stop-Process -Id $PID
}