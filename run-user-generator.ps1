$ErrorActionPreference = "Stop"

$repo = "JLBBARCO/programs-manager-user-generator"
$appName = "Programs Manager User Generator"
$asset = "programs-manager-user-generator-windows.zip"
$workdir = Join-Path ([System.IO.Path]::GetTempPath()) ("pmug-" + [System.Guid]::NewGuid().ToString("N"))
$archive = Join-Path $workdir $asset

try {
    New-Item -ItemType Directory -Path $workdir | Out-Null

    Write-Host "Downloading latest $appName release..."
    Invoke-WebRequest `
        -Uri "https://github.com/$repo/releases/latest/download/$asset" `
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
