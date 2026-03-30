$ErrorActionPreference = "Stop"

$owner = "JLBBARCO"
$repo = "auto-programs"
$branch = if ($env:AIP_BRANCH) { $env:AIP_BRANCH } else { "main" }

$installRoot = Join-Path $HOME ".auto-install-programs"
$stageDir = Join-Path $installRoot "src"
$safeBranch = $branch -replace '[^A-Za-z0-9._-]', '_'
$zipUrl = "https://codeload.github.com/$owner/$repo/zip/refs/heads/$branch"
$zipFile = Join-Path $env:TEMP "$repo-$branch.zip"
$stateFile = Join-Path $installRoot "quick-run-state.json"

function Get-State {
    param([string]$Path)

    if (!(Test-Path $Path)) {
        return @{}
    }

    try {
        $rawState = Get-Content -Path $Path -Raw | ConvertFrom-Json
        $state = @{}

        foreach ($prop in $rawState.PSObject.Properties) {
            $state[$prop.Name] = $prop.Value
        }

        return $state
    }
    catch {
        Write-Host "[quick-run] State file invalid, recreating cache metadata..."
        return @{}
    }
}

function Save-State {
    param(
        [string]$Path,
        [hashtable]$State
    )

    $State | ConvertTo-Json | Set-Content -Path $Path -Encoding UTF8
}

function Get-RemoteEtag {
    param([string]$Url)

    try {
        $headResponse = Invoke-WebRequest -Uri $Url -Method Head -UseBasicParsing
        return $headResponse.Headers.ETag
    }
    catch {
        Write-Host "[quick-run] Could not retrieve ETag, forcing source refresh..."
        return $null
    }
}

function Get-FileHashString {
    param([string]$Path)

    if (!(Test-Path $Path)) {
        return $null
    }

    return (Get-FileHash -Path $Path -Algorithm SHA256).Hash
}

Write-Host "[quick-run] Updating source from $branch..."
New-Item -ItemType Directory -Path $installRoot -Force | Out-Null

$state = Get-State -Path $stateFile
$remoteEtag = Get-RemoteEtag -Url $zipUrl
$mainPyCurrent = Join-Path $stageDir "main.py"
$sourceIsCurrent = (
    (Test-Path $mainPyCurrent) -and
    ($state.branch -eq $branch) -and
    ($remoteEtag) -and
    ($state.sourceEtag -eq $remoteEtag)
)

if ($sourceIsCurrent) {
    Write-Host "[quick-run] Source already up to date (ETag cache hit)."
}
else {
    Write-Host "[quick-run] Refreshing source archive..."
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing

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

    $state.branch = $branch
    $state.sourceEtag = $remoteEtag
}

$mainPy = Join-Path $stageDir "main.py"
if (!(Test-Path $mainPy)) {
    throw "main.py not found in $stageDir"
}

$requirementsFile = Join-Path $stageDir "requirements.txt"
$venvPath = Join-Path $installRoot (".venv-" + $safeBranch)
$venvPython = Join-Path $venvPath "Scripts\python.exe"

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (!($pythonLauncher -or $pythonCmd)) {
    throw "Python 3 not found. Install Python and try again."
}

if (!(Test-Path $venvPython)) {
    Write-Host "[quick-run] Creating virtual environment at $venvPath..."
    if ($pythonLauncher) {
        & py -3 -m venv $venvPath
    }
    else {
        & python -m venv $venvPath
    }
}

$requirementsHash = Get-FileHashString -Path $requirementsFile
$depsAreCurrent = (
    (Test-Path $venvPython) -and
    ($requirementsHash) -and
    ($state.requirementsBranch -eq $branch) -and
    ($state.requirementsHash -eq $requirementsHash)
)

if ($depsAreCurrent) {
    Write-Host "[quick-run] Dependencies unchanged (requirements cache hit)."
}
else {
    Write-Host "[quick-run] Installing dependencies..."
    if ($env:AIP_FORCE_PIP_UPGRADE -eq "1") {
        & $venvPython -m pip install --upgrade pip --disable-pip-version-check
    }
}

if (Test-Path $requirementsFile) {
    if (!$depsAreCurrent) {
        & $venvPython -m pip install -r $requirementsFile --disable-pip-version-check
        $state.requirementsBranch = $branch
        $state.requirementsHash = $requirementsHash
    }
}

Save-State -Path $stateFile -State $state

Write-Host "[quick-run] Launching app..."
& $venvPython $mainPy
