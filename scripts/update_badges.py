#!/usr/bin/env python3
"""
Script para atualizar os badges de versão nos arquivos README.md e roadmap.md.
Este script é executado automaticamente após a atualização da versão.

Uso:
    python scripts/update_badges.py
"""

import os
import re
from pathlib import Path
import sys

# Obter o diretório raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
README_FILE = ROOT_DIR / "README.md"
ROADMAP_FILE = ROOT_DIR / "roadmap.md"
VERSION_FILE = ROOT_DIR / "app" / "core" / "version.py"

def read_version_info():
    """Lê as informações de versão do arquivo version.py."""
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Extrair as informações
    version_match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
    phase_match = re.search(r'PHASE\s*=\s*"([^"]+)"', content)
    date_match = re.search(r'LAST_UPDATED\s*=\s*"([^"]+)"', content)

    if not all([version_match, phase_match, date_match]):
        print("Erro: Não foi possível encontrar todas as informações de versão.")
        sys.exit(1)

    return {
        "version": version_match.group(1),
        "phase": phase_match.group(1),
        "last_updated": date_match.group(1)
    }

def update_badges(file_path, version_info):
    """Atualiza os badges em um arquivo markdown."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Usar regex mais simples e seguro para substituir o badge de versão
    version_pattern = r'\[!\[Versão\]\(https://img\.shields\.io/badge/Versão-[^-]+-blue\)\]'
    new_version_badge = f"[![Versão](https://img.shields.io/badge/Versão-{version_info['phase'].replace(' ', '%20')}-blue)]"
    content = re.sub(version_pattern, new_version_badge, content)

    # Usar regex mais simples e seguro para substituir o badge de última atualização
    update_pattern = r'\[!\[Última atualização\]\(https://img\.shields\.io/badge/Última%20atualização-[^-]+-green\)\]'
    new_update_badge = f"[![Última atualização](https://img.shields.io/badge/Última%20atualização-{version_info['last_updated'].replace(' ', '%20')}-green)]"
    content = re.sub(update_pattern, new_update_badge, content)

    # Escrever o conteúdo atualizado
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Badges atualizados em {file_path.name}")

def main():
    """Função principal."""
    version_info = read_version_info()

    # Atualizar os badges no README.md
    if README_FILE.exists():
        update_badges(README_FILE, version_info)
    else:
        print(f"Aviso: Arquivo {README_FILE} não encontrado.")

    # Atualizar os badges no roadmap.md
    if ROADMAP_FILE.exists():
        update_badges(ROADMAP_FILE, version_info)
    else:
        print(f"Aviso: Arquivo {ROADMAP_FILE} não encontrado.")

    print("Badges atualizados com sucesso!")

if __name__ == "__main__":
    main()
