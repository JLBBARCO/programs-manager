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
    Write-Host "[$appName] Python 3.12+ not found. Installing Python from the terminal..."
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        $installArgs = @('install', '--id', 'Python.Python.3.12', '--exact', '--scope', 'user', '--silent', '--accept-package-agreements', '--accept-source-agreements')
        if (-not [Environment]::Is64BitOperatingSystem) { $installArgs += @('--architecture', 'x86') }
        & $winget.Source @installArgs
        if ($LASTEXITCODE -ne 0) { throw 'Python installation with winget failed.' }
        $env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;$env:LOCALAPPDATA\Programs\Python\Python312-32;$env:LOCALAPPDATA\Programs\Python\Python312-32\Scripts;$env:PATH"
        $python = Find-Python
    }
    if (-not $python) { throw 'Could not install Python. Install Python 3.12 or newer and run this script again.' }
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
    if (-not (Test-Path (Join-Path $venvPath 'Scripts\python.exe'))) {
        & $pythonPath @pythonArgs -m venv $venvPath
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python virtual environment.' }
    }
    $runtimePython = Join-Path $venvPath 'Scripts\python.exe'
    Write-Host "[$appName] Installing runtime dependencies..."
    & $runtimePython -m pip install -r (Join-Path $projectRoot 'core-app\runtime-requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Failed to install Python dependencies.' }
    Write-Host "[$appName] Starting interpreted Python app..."
    & $runtimePython (Join-Path $projectRoot 'core-app\main.py')
    if ($LASTEXITCODE -ne 0) { throw "Application exited with code $LASTEXITCODE." }
} finally {
    if (Test-Path $workRoot) { Remove-Item $workRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
