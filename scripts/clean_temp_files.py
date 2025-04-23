#!/usr/bin/env python3
"""
Script para limpeza manual de arquivos temporários.

Este script permite executar a limpeza de arquivos temporários manualmente,
com opções para simular a limpeza (dry-run) e personalizar as políticas de retenção.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.file_cleaner import clean_temp_files, FileCleaner
from app.core.retention_policy import RetentionPolicy
from app.utils.log_config import configure_file_cleaner_logging


def setup_logging(verbose: bool = False) -> None:
    """
    Configura o sistema de logging.

    Args:
        verbose: Se True, configura o nível de log para DEBUG
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Usar a configuração de logging do módulo log_config
    configure_file_cleaner_logging(console=True)

    # Ajustar nível de log se for modo verbose
    if verbose:
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        file_cleaner_logger = logging.getLogger("app.utils.file_cleaner")
        file_cleaner_logger.setLevel(log_level)


def parse_args() -> argparse.Namespace:
    """
    Analisa os argumentos da linha de comando.

    Returns:
        Argumentos analisados
    """
    parser = argparse.ArgumentParser(
        description="Limpa arquivos temporários do sistema Docling",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a limpeza sem remover arquivos",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Exibe informações detalhadas durante a execução",
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Salva as estatísticas em um arquivo JSON",
    )

    # Opções para personalizar políticas de retenção
    retention_group = parser.add_argument_group("Políticas de retenção")

    retention_group.add_argument(
        "--uploads-max-age",
        type=int,
        help="Idade máxima (em dias) para arquivos de upload",
    )

    retention_group.add_argument(
        "--results-max-age",
        type=int,
        help="Idade máxima (em dias) para resultados de processamento",
    )

    retention_group.add_argument(
        "--temp-files-max-age",
        type=int,
        help="Idade máxima (em horas) para arquivos temporários",
    )

    # Opções para tipos específicos de arquivos
    types_group = parser.add_argument_group("Tipos de arquivos")

    types_group.add_argument(
        "--uploads-only",
        action="store_true",
        help="Limpa apenas arquivos de upload",
    )

    types_group.add_argument(
        "--results-only",
        action="store_true",
        help="Limpa apenas resultados de processamento",
    )

    types_group.add_argument(
        "--temp-files-only",
        action="store_true",
        help="Limpa apenas arquivos temporários",
    )

    return parser.parse_args()


def main() -> None:
    """
    Função principal do script.
    """
    # Analisar argumentos
    args = parse_args()

    # Configurar logging
    setup_logging(args.verbose)

    # Configurar políticas de retenção personalizadas
    custom_policies = {}

    if args.uploads_max_age is not None:
        if "uploads" not in custom_policies:
            custom_policies["uploads"] = {}
        custom_policies["uploads"]["max_age_days"] = args.uploads_max_age

    if args.results_max_age is not None:
        if "results" not in custom_policies:
            custom_policies["results"] = {}
        custom_policies["results"]["max_age_days"] = args.results_max_age

    if args.temp_files_max_age is not None:
        if "temp_files" not in custom_policies:
            custom_policies["temp_files"] = {}
        custom_policies["temp_files"]["max_age_hours"] = args.temp_files_max_age

    # Aplicar políticas personalizadas
    if custom_policies:
        os.environ["RETENTION_UPLOADS_MAX_AGE_DAYS"] = str(
            custom_policies.get("uploads", {}).get("max_age_days", "")
        )
        os.environ["RETENTION_RESULTS_MAX_AGE_DAYS"] = str(
            custom_policies.get("results", {}).get("max_age_days", "")
        )
        os.environ["RETENTION_TEMP_FILES_MAX_AGE_HOURS"] = str(
            custom_policies.get("temp_files", {}).get("max_age_hours", "")
        )

    # Criar limpador de arquivos
    cleaner = FileCleaner(dry_run=args.dry_run)

    # Executar limpeza específica ou completa
    if args.uploads_only:
        old_uploads = cleaner.identify_old_uploads()
        cleaner.remove_files(old_uploads, "uploads")
    elif args.results_only:
        old_results = cleaner.identify_old_results()
        cleaner.remove_files(old_results, "results")
    elif args.temp_files_only:
        old_temp_files = cleaner.identify_temp_files()
        cleaner.remove_files(old_temp_files, "temp_files")
    else:
        # Limpeza completa
        cleaner.clean_all()

    # Exibir estatísticas
    stats = cleaner.stats

    print("\n=== Estatísticas de Limpeza ===")
    print(f"Modo: {'Simulação (dry-run)' if args.dry_run else 'Remoção real'}")
    print(f"Uploads: {stats['uploads_removed']}/{stats['uploads_identified']} removidos")
    print(f"Resultados: {stats['results_removed']}/{stats['results_identified']} removidos")
    print(f"Arquivos temporários: {stats['temp_files_removed']}/{stats['temp_files_identified']} removidos")

    total_identified = stats.get("total_identified", 0)
    total_removed = stats.get("total_removed", 0)
    total_freed = stats.get("human_readable_freed", "0 B")

    print(f"Total: {total_removed}/{total_identified} arquivos removidos")
    print(f"Espaço liberado: {total_freed}")

    # Salvar estatísticas em arquivo, se solicitado
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            print(f"\nEstatísticas salvas em: {args.output}")
        except Exception as e:
            logging.error(f"Erro ao salvar estatísticas: {str(e)}")


if __name__ == "__main__":
    main()
