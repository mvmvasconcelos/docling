#!/usr/bin/env python3
"""
Script para atualizar a versão do projeto Docling.
Este script atualiza o arquivo app/core/version.py com a nova versão.

Uso:
    python scripts/update_version.py [major|minor|patch] [--phase "Nova Fase"] [--date "Mês YYYY"]

Exemplos:
    python scripts/update_version.py patch
    python scripts/update_version.py minor --phase "MVP Fase 2"
    python scripts/update_version.py major --phase "Release" --date "Maio 2025"
"""

import os
import sys
import re
from pathlib import Path
import argparse
import subprocess
from datetime import datetime

# Obter o diretório raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT_DIR / "app" / "core" / "version.py"

def read_current_version():
    """Lê a versão atual do arquivo version.py."""
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Extrair a versão atual
    version_match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
    phase_match = re.search(r'PHASE\s*=\s*"([^"]+)"', content)
    date_match = re.search(r'LAST_UPDATED\s*=\s*"([^"]+)"', content)

    if not version_match:
        print("Erro: Não foi possível encontrar a versão atual no arquivo.")
        sys.exit(1)

    version = version_match.group(1)
    phase = phase_match.group(1) if phase_match else "MVP Fase 1"
    last_updated = date_match.group(1) if date_match else "Abril 2025"

    return version, phase, last_updated

def update_version(version_type, new_phase=None, new_date=None):
    """Atualiza a versão no arquivo version.py."""
    current_version, current_phase, current_date = read_current_version()

    # Dividir a versão em partes
    major, minor, patch = map(int, current_version.split('.'))

    # Atualizar a versão conforme o tipo
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        print(f"Erro: Tipo de versão inválido: {version_type}")
        sys.exit(1)

    # Montar a nova versão
    new_version = f"{major}.{minor}.{patch}"

    # Usar os valores fornecidos ou atualizar automaticamente
    if new_phase:
        # Se uma fase foi explicitamente fornecida, use-a
        phase = new_phase
    elif current_phase.replace('.', '').isdigit():
        # Se a fase atual é um número de versão (como "0.9.0"), atualize-a para a nova versão
        phase = new_version
    else:
        # Caso contrário, mantenha a fase atual
        phase = current_phase

    date = new_date if new_date else current_date

    # Ler o conteúdo atual do arquivo
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Substituir os valores
    content = re.sub(r'VERSION\s*=\s*"[^"]+"', f'VERSION = "{new_version}"', content)
    content = re.sub(r'PHASE\s*=\s*"[^"]+"', f'PHASE = "{phase}"', content)
    content = re.sub(r'LAST_UPDATED\s*=\s*"[^"]+"', f'LAST_UPDATED = "{date}"', content)

    # Escrever o conteúdo atualizado
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Versão atualizada com sucesso:")
    print(f"  Versão anterior: {current_version} ({current_phase})")
    print(f"  Nova versão: {new_version} ({phase})")
    print(f"  Última atualização: {date}")

    # Atualizar os badges nos arquivos markdown
    try:
        badges_script = Path(__file__).resolve().parent / "update_badges.py"
        if badges_script.exists():
            print("\nAtualizando badges nos arquivos markdown...")
            subprocess.run([sys.executable, str(badges_script)], check=True)
        else:
            print("\nAviso: Script update_badges.py não encontrado.")
    except subprocess.CalledProcessError as e:
        print(f"\nErro ao atualizar badges: {e}")
    except Exception as e:
        print(f"\nErro inesperado ao atualizar badges: {e}")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Atualiza a versão do projeto Docling.")
    parser.add_argument("version_type", choices=["major", "minor", "patch"],
                        help="Tipo de atualização de versão")
    parser.add_argument("--phase", help="Nova fase do projeto (ex: 'MVP Fase 2')")
    parser.add_argument("--date", help="Data da atualização (ex: 'Maio 2025')")

    args = parser.parse_args()

    # Se a data não for fornecida, usar o mês e ano atuais
    if not args.date:
        current_date = datetime.now()
        month_names = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        month_name = month_names[current_date.month - 1]
        args.date = f"{month_name} {current_date.year}"

    update_version(args.version_type, args.phase, args.date)

if __name__ == "__main__":
    main()
