#!/bin/bash
# Script para executar os testes do Programs Manager

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Programs Manager - Sistema Automático de Testes           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detectar Python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${BLUE}[*]${NC} Testando disponibilidade do Python..."
if ! $PYTHON_CMD --version &> /dev/null; then
    echo -e "${RED}[!]${NC} Python não encontrado. Instale Python 3.7+ e tente novamente."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[OK]${NC} Python $PYTHON_VERSION encontrado"
echo ""

# Navegar para a raiz do projeto
cd "$(dirname "$0")/.."

# Opção 1: Usar o sistema de testes personalizado
if [[ "$1" == "auto" || "$1" == "" ]]; then
    echo -e "${BLUE}[*]${NC} Executando testes automáticos..."
    echo ""
    $PYTHON_CMD test/run_tests.py
    
# Opção 2: Usar pytest se disponível
elif [[ "$1" == "pytest" ]]; then
    echo -e "${BLUE}[*]${NC} Verificando disponibilidade do pytest..."
    if ! $PYTHON_CMD -m pytest --version &> /dev/null; then
        echo -e "${YELLOW}[!]${NC} pytest não encontrado. Instalando..."
        $PYTHON_CMD -m pip install pytest
    fi
    echo ""
    echo -e "${BLUE}[*]${NC} Executando testes com pytest..."
    $PYTHON_CMD -m pytest test/test_modules.py -v --tb=short
    
# Opção 3: Exibir ajuda
elif [[ "$1" == "help" || "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Uso: $0 [opção]"
    echo ""
    echo "Opções:"
    echo "  auto    - Executar testes automáticos (padrão)"
    echo "  pytest  - Executar com pytest"
    echo "  help    - Exibir esta mensagem"
    echo ""
    echo "Exemplos:"
    echo "  ./run_tests.sh"
    echo "  ./run_tests.sh pytest"
    echo "  bash run_tests.sh auto"
else
    echo -e "${RED}[!]${NC} Opção desconhecida: $1"
    echo "Use './run_tests.sh help' para ver as opções disponíveis"
    exit 1
fi

echo ""
echo -e "${GREEN}[OK]${NC} Testes concluídos!"
echo ""
