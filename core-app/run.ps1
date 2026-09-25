$ErrorActionPreference = 'Stop'
$owner = 'JLBBARCO'
$repo = 'programs-manager'
$branch = if ($env:AIP_BRANCH) { $env:AIP_BRANCH } elseif ($env:SCRIPT_BRANCH) { $env:SCRIPT_BRANCH } else { 'main' }
$branch = $branch.Trim().ToLowerInvariant()
$appName = 'Programs Manager'

function Find-Python {
    foreach ($candidate in @('python', 'py')) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            if ($candidate -eq 'py') { & $command.Source -3 -c "import sys; raise SystemExit(sys.version_info < (3, 12))" *> $null }
            else { & $command.Source -c "import sys; raise SystemExit(sys.version_info < (3, 12))" *> $null }
            if ($LASTEXITCODE -eq 0) { return @{ Path = $command.Source; Launcher = $candidate } }
        }
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    $pythonVersion = '3.13.15'
    $pythonInstallDir = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313'
    $pythonInstallerName = if ([Environment]::Is64BitOperatingSystem) { "python-$pythonVersion-amd64.exe" } else { "python-$pythonVersion.exe" }
    $pythonInstaller = Join-Path $env:TEMP $pythonInstallerName
    $pythonInstallerUrl = "https://www.python.org/ftp/python/$pythonVersion/$pythonInstallerName"

    Write-Host "[$appName] Python 3.12+ not found. Installing Python $pythonVersion..."
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $pythonInstaller
    $installerArgs = @(
        '/quiet',
        'InstallAllUsers=0',
        'Include_launcher=1',
        'Include_pip=1',
        'Include_tcltk=1',
        'PrependPath=0',
        "TargetDir=`"$pythonInstallDir`""
    )
    $install = Start-Process -FilePath $pythonInstaller -ArgumentList $installerArgs -Wait -PassThru
    Remove-Item $pythonInstaller -Force -ErrorAction SilentlyContinue
    if ($install.ExitCode -ne 0) { throw "Python installation failed with exit code $($install.ExitCode)." }

    $env:PATH = "$pythonInstallDir;$pythonInstallDir\Scripts;$env:PATH"
    $python = Find-Python
    if (-not $python) {
        $installedPython = Join-Path $pythonInstallDir 'python.exe'
        if (Test-Path $installedPython) { $python = @{ Path = $installedPython; Launcher = 'python' } }
    }
    if (-not $python) { throw "Python $pythonVersion installed, but the launcher could not find it." }
}

$workRoot = Join-Path $env:TEMP ("programs-manager-" + [guid]::NewGuid().ToString('N'))
$scriptPath = $PSCommandPath
$projectRoot = $null
if ($scriptPath) {
    $candidateRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)
    if (Test-Path (Join-Path $candidateRoot 'core-app\main.py')) { $projectRoot = $candidateRoot }
}

try {
    if (-not $projectRoot) {
        New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
        $archive = Join-Path $workRoot 'source.zip'
        $uri = "https://github.com/$owner/$repo/archive/refs/heads/$branch.zip"
        Write-Host "[$appName] Downloading Python source ($branch)..."
        Invoke-WebRequest -Uri $uri -OutFile $archive
        Expand-Archive -Path $archive -DestinationPath $workRoot -Force
        $projectRoot = Get-ChildItem $workRoot -Directory | Select-Object -First 1 -ExpandProperty FullName
    }

    $pythonPath = $python.Path
    $pythonArgs = @()
    if ($python.Launcher -eq 'py') { $pythonArgs += '-3' }
    $venvPath = Join-Path $env:LOCALAPPDATA '.programs-manager\venv'
    $runtimePython = Join-Path $venvPath 'Scripts\python.exe'
    $venvUsable = $false
    if (Test-Path $runtimePython) {
        & $runtimePython -c "import sys; raise SystemExit(sys.version_info < (3, 12))" *> $null
        $venvUsable = $LASTEXITCODE -eq 0
    }
    if (-not $venvUsable) {
        if (Test-Path $venvPath) { Remove-Item $venvPath -Recurse -Force }
        & $pythonPath @pythonArgs -m venv $venvPath
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python virtual environment.' }
    }
    Write-Host "[$appName] Installing runtime dependencies..."
    & $runtimePython -m pip install -r (Join-Path $projectRoot 'core-app\runtime-requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Failed to install Python dependencies.' }
    Write-Host "[$appName] Starting interpreted Python app..."
    & $runtimePython (Join-Path $projectRoot 'core-app\main.py')
    if ($LASTEXITCODE -ne 0) { throw "Application exited with code $LASTEXITCODE." }
} finally {
    if (Test-Path $workRoot) { Remove-Item $workRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
