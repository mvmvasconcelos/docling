"""
Testes para o módulo app.core.version
"""
import re
from app.core.version import (
    VERSION,
    PHASE,
    LAST_UPDATED,
    get_version,
    get_phase,
    get_last_updated,
    get_version_info,
)


def test_version_format():
    """Testa se a versão está no formato correto (MAJOR.MINOR.PATCH)."""
    # Padrão de versão semântica: X.Y.Z onde X, Y e Z são números inteiros
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, VERSION), f"Versão '{VERSION}' não está no formato X.Y.Z"


def test_get_version():
    """Testa se a função get_version retorna o valor correto."""
    assert get_version() == VERSION


def test_get_phase():
    """Testa se a função get_phase retorna o valor correto."""
    assert get_phase() == PHASE


def test_get_last_updated():
    """Testa se a função get_last_updated retorna o valor correto."""
    assert get_last_updated() == LAST_UPDATED


def test_get_version_info():
    """Testa se a função get_version_info retorna o dicionário correto."""
    expected = {
        "version": VERSION,
        "phase": PHASE,
        "last_updated": LAST_UPDATED,
    }
    assert get_version_info() == expected


def test_last_updated_format():
    """Testa se a data da última atualização está no formato correto (Mês YYYY)."""
    # Padrão: Nome do mês seguido por espaço e ano de 4 dígitos
    pattern = r"^[A-Za-zçãõáéíóúâêîôûàèìòù]+ \d{4}$"
    assert re.match(pattern, LAST_UPDATED), f"Data '{LAST_UPDATED}' não está no formato 'Mês YYYY'"
