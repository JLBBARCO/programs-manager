$owner = "JLBBARCO"
$repo = "auto-programs"
$installRoot = Join-Path $HOME ".auto-install-programs"
$exePath = Join-Path $installRoot "Auto-Install-Programs\Auto Install Programs.exe"

# 1. Verifica se já existe, se não, busca na API do GitHub
if (!(Test-Path $exePath)) {
    Write-Host "[auto-programs] Baixando versão compilada para Windows..."
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest"
    $asset = $release.assets | Where-Object { $_.name -like "*windows.zip" } | Select-Object -First 1
    
    $zipTemp = Join-Path $env:TEMP "aip_win.zip"
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipTemp
    
    Expand-Archive -Path $zipTemp -DestinationPath $installRoot -Force
    Remove-Item $zipTemp
}

# 2. Executa o binário diretamente (Sem Python, sem VENV)
Write-Host "[auto-programs] Iniciando..."
Start-Process -FilePath $exePath -WorkingDirectory (Split-Path $exePath)