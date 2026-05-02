"""
Configuração do pytest para o sistema de testes do Programs Manager
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Configuração inicial do pytest"""
    config.addinivalue_line(
        "markers", "unit: marca teste como unitário"
    )
    config.addinivalue_line(
        "markers", "integration: marca teste como integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca teste como lento"
    )
    print("\n✓ Pytest configurado para Programs Manager\n")


def pytest_collection_modifyitems(config, items):
    """Modifica items coletados antes da execução"""
    for item in items:
        # Adiciona markers padrão se não houver
        if not item.iter_markers():
            item.add_marker("unit")
