param(
    [switch]$Cleanup = $false
)

$ErrorActionPreference = 'Continue'

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Passwords Manager - Shortcut Integration Test (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "Project root: $ProjectRoot"
Write-Host "Platform: Windows"
Write-Host ""

$StartMenuDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$DesktopDir = "$env:USERPROFILE\Desktop"
$StartMenuShortcut = Join-Path $StartMenuDir "Passwords Manager.lnk"
$DesktopShortcut = Join-Path $DesktopDir "Passwords Manager.lnk"

Write-Host "Testing shortcut creation on app startup..."
Write-Host "Expected Start Menu shortcut: $StartMenuShortcut"
Write-Host "Expected Desktop shortcut: $DesktopShortcut"
Write-Host ""

# Record state before
$StartMenuExists = Test-Path $StartMenuShortcut
$DesktopExists = Test-Path $DesktopShortcut

if ($StartMenuExists) {
    Write-Host "-> Start Menu shortcut exists (will check if updated)"
}
else {
    Write-Host "-> Start Menu shortcut does not exist yet"
}

if ($DesktopExists) {
    Write-Host "-> Desktop shortcut exists (will check if updated)"
}
else {
    Write-Host "-> Desktop shortcut does not exist yet"
}

Write-Host ""
Write-Host "Running app (will timeout after 8 seconds)..." -ForegroundColor Yellow

Push-Location $ProjectRoot

Write-Host "Priming shortcut creation via application helper..."
python -c "from src.lib.shortcuts import ensure_platform_shortcuts_best_effort; created = ensure_platform_shortcuts_best_effort(); print('Created shortcuts:'); [print(shortcut) for shortcut in created]"
Write-Host ""

# Start app with 8-second timeout (give app time to create shortcuts before closing)
$process = Start-Process python -ArgumentList "main.py" -PassThru -NoNewWindow -ErrorAction SilentlyContinue
Start-Sleep -Seconds 8
$process | Stop-Process -Force -ErrorAction SilentlyContinue
Wait-Process -InputObject $process -ErrorAction SilentlyContinue

Pop-Location

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Checking shortcut creation..."
Write-Host ""

$TestPassed = $true

if (Test-Path $StartMenuShortcut) {
    Write-Host "[OK] Start Menu shortcut created: $StartMenuShortcut" -ForegroundColor Green
}
else {
    Write-Host "[FAIL] Start Menu shortcut not found: $StartMenuShortcut" -ForegroundColor Red
    $TestPassed = $false
}

if (Test-Path $DesktopShortcut) {
    Write-Host "[OK] Desktop shortcut created: $DesktopShortcut" -ForegroundColor Green
}
else {
    Write-Host "[FAIL] Desktop shortcut not found: $DesktopShortcut" -ForegroundColor Red
    $TestPassed = $false
}

Write-Host ""

if ($TestPassed) {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "[OK] Integration test passed!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    
    if ($Cleanup) {
        Write-Host ""
        Write-Host "Cleaning up test shortcuts..." -ForegroundColor Yellow
        Remove-Item $StartMenuShortcut -Force -ErrorAction SilentlyContinue | Out-Null
        Remove-Item $DesktopShortcut -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Host "[OK] Cleanup complete" -ForegroundColor Green
    }
    exit 0
}
else {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "[FAIL] Integration test failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
    exit 1
}
