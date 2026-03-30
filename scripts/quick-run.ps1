$ErrorActionPreference = "Stop"

$owner = "JLBBARCO"
$repo = "auto-programs"
$branch = if ($env:AIP_BRANCH) { $env:AIP_BRANCH } else { "main" }

$installRoot = Join-Path $HOME ".auto-install-programs"
$stageDir = Join-Path $installRoot "src"
$zipUrl = "https://codeload.github.com/$owner/$repo/zip/refs/heads/$branch"
$zipFile = Join-Path $env:TEMP "$repo-$branch.zip"

Write-Host "[quick-run] Updating source from $branch..."
New-Item -ItemType Directory -Path $installRoot -Force | Out-Null

Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile

if (Test-Path $stageDir) {
    Remove-Item -Path $stageDir -Recurse -Force
}

Expand-Archive -Path $zipFile -DestinationPath $installRoot -Force

$extractedDir = Join-Path $installRoot "$repo-$branch"
if (!(Test-Path $extractedDir)) {
    throw "Could not find extracted directory: $extractedDir"
}

Move-Item -Path $extractedDir -Destination $stageDir -Force
Remove-Item -Path $zipFile -Force

$mainPy = Join-Path $stageDir "main.py"
if (!(Test-Path $mainPy)) {
    throw "main.py not found in $stageDir"
}

$requirementsFile = Join-Path $stageDir "requirements.txt"
$venvPath = Join-Path $stageDir ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (!($pythonLauncher -or $pythonCmd)) {
    throw "Python 3 not found. Install Python and try again."
}

if (!(Test-Path $venvPython)) {
    Write-Host "[quick-run] Creating .venv..."
    if ($pythonLauncher) {
        & py -3 -m venv $venvPath
    }
    else {
        & python -m venv $venvPath
    }
}

Write-Host "[quick-run] Installing dependencies..."
& $venvPython -m pip install --upgrade pip
if (Test-Path $requirementsFile) {
    & $venvPython -m pip install -r $requirementsFile
}

Write-Host "[quick-run] Launching app..."
& $venvPython $mainPy
