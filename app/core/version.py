"""
Arquivo central para definição da versão do projeto Docling.
Este arquivo serve como fonte única de verdade para a versão do projeto.
"""

# Versão do projeto no formato Semântico (SemVer): MAJOR.MINOR.PATCH
# - MAJOR: Mudanças incompatíveis com versões anteriores
# - MINOR: Adição de funcionalidades mantendo compatibilidade
# - PATCH: Correções de bugs mantendo compatibilidade
VERSION = "1.2.0"

# Fase de desenvolvimento (usado em badges e documentação)
PHASE = "1.2.0"

# Data da última atualização (formato: Mês YYYY)
LAST_UPDATED = "Abril 2025"


def get_version():
    """Retorna a versão atual do projeto."""
    return VERSION


def get_phase():
    """Retorna a fase atual de desenvolvimento."""
    return PHASE


def get_last_updated():
    """Retorna a data da última atualização."""
    return LAST_UPDATED


def get_version_info():
    """Retorna um dicionário com todas as informações de versão."""
    return {"version": VERSION, "phase": PHASE, "last_updated": LAST_UPDATED}
