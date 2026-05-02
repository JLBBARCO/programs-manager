# Script para executar os testes do Programs Manager no Windows
# Uso: .\run_tests.ps1 ou PowerShell -File run_tests.ps1

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Programs Manager - Sistema Automático de Testes           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Obtém o diretório do script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Função para encontrar Python
function Find-Python {
    # Tenta Python 3 primeiro
    $pythonVersions = @("python", "python3")
    
    foreach ($py in $pythonVersions) {
        try {
            $version = & $py --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                return $py
            }
        }
        catch {
            # Continua para a próxima versão
        }
    }
    
    return $null
}

# Detectar Python
Write-Host "[*] Testando disponibilidade do Python..." -ForegroundColor Blue
$pythonCmd = Find-Python

if ($null -eq $pythonCmd) {
    Write-Host "[!] Python não encontrado. Instale Python 3.7+ e tente novamente." -ForegroundColor Red
    exit 1
}

$pythonVersion = & $pythonCmd --version 2>&1
Write-Host "[OK] $pythonVersion encontrado" -ForegroundColor Green
Write-Host ""

# Opção 1: Usar o sistema de testes personalizado (padrão)
if ($args.Count -eq 0 -or $args[0] -eq "auto") {
    Write-Host "[*] Executando testes automáticos..." -ForegroundColor Blue
    Write-Host ""
    & $pythonCmd "$projectRoot\test\run_tests.py"
    
# Opção 2: Usar pytest se disponível
} elseif ($args[0] -eq "pytest") {
    Write-Host "[*] Verificando disponibilidade do pytest..." -ForegroundColor Blue
    
    $testResult = & $pythonCmd -m pytest --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] pytest não encontrado. Instalando..." -ForegroundColor Yellow
        & $pythonCmd -m pip install pytest
    }
    
    Write-Host ""
    Write-Host "[*] Executando testes com pytest..." -ForegroundColor Blue
    & $pythonCmd -m pytest "$projectRoot\test\test_modules.py" -v --tb=short
    
# Opção 3: Exibir relatório anterior
} elseif ($args[0] -eq "report") {
    Write-Host "[*] Abrindo relatório HTML..." -ForegroundColor Blue
    
    $reportPath = "$projectRoot\test\test_report.html"
    if (Test-Path $reportPath) {
        Invoke-Item $reportPath
    } else {
        Write-Host "[!] Relatório não encontrado. Execute os testes primeiro." -ForegroundColor Red
    }

# Opção 4: Exibir ajuda
} elseif ($args[0] -eq "help" -or $args[0] -eq "-h" -or $args[0] -eq "--help") {
    Write-Host "Uso: .\run_tests.ps1 [opção]"
    Write-Host ""
    Write-Host "Opções:"
    Write-Host "  auto    - Executar testes automáticos (padrão)"
    Write-Host "  pytest  - Executar com pytest"
    Write-Host "  report  - Abrir relatório HTML anterior"
    Write-Host "  help    - Exibir esta mensagem"
    Write-Host ""
    Write-Host "Exemplos:"
    Write-Host "  .\run_tests.ps1"
    Write-Host "  .\run_tests.ps1 pytest"
    Write-Host "  .\run_tests.ps1 report"

} else {
    Write-Host "[!] Opção desconhecida: $($args[0])" -ForegroundColor Red
    Write-Host "Use '.\run_tests.ps1 help' para ver as opções disponíveis"
    exit 1
}

Write-Host ""
Write-Host "[OK] Testes concluídos!" -ForegroundColor Green
Write-Host ""
