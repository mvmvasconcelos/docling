"""
Módulo para identificação e limpeza de arquivos temporários.

Este módulo fornece funcionalidades para identificar arquivos temporários obsoletos
e removê-los de forma segura, otimizando o uso de espaço em disco.
"""

import os
import json
import shutil
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import UPLOAD_DIR, RESULTS_DIR
from app.core.retention_policy import retention_policy
from app.utils.log_config import configure_file_cleaner_logging

# Configurar logger
configure_file_cleaner_logging(console=False)
logger = logging.getLogger(__name__)


class FileCleaner:
    """
    Classe para identificar e limpar arquivos temporários obsoletos.
    """

    def __init__(self, dry_run: bool = False):
        """
        Inicializa o limpador de arquivos.

        Args:
            dry_run: Se True, não remove arquivos, apenas simula a remoção
        """
        self.dry_run = dry_run
        self.upload_dir = UPLOAD_DIR
        self.results_dir = RESULTS_DIR
        self.policy = retention_policy

        # Estatísticas de limpeza
        self.stats = {
            "uploads_identified": 0,
            "uploads_removed": 0,
            "uploads_bytes_freed": 0,
            "results_identified": 0,
            "results_removed": 0,
            "results_bytes_freed": 0,
            "temp_files_identified": 0,
            "temp_files_removed": 0,
            "temp_files_bytes_freed": 0,
        }

    def identify_old_uploads(self) -> List[str]:
        """
        Identifica arquivos de upload obsoletos com base na política de retenção.

        Returns:
            Lista de caminhos para arquivos de upload obsoletos
        """
        old_uploads = []
        max_age = self.policy.get_upload_max_age()
        now = datetime.now()

        # Obter IDs de resultados existentes para verificar se o upload foi processado
        processed_files = self._get_processed_original_files()

        try:
            # Verificar cada arquivo no diretório de uploads
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)

                # Ignorar diretórios
                if not os.path.isfile(file_path):
                    continue

                # Verificar se o arquivo está isento com base na extensão
                file_ext = os.path.splitext(filename)[1]
                if self.policy.is_extension_exempt(file_ext):
                    logger.debug(f"Arquivo isento por extensão: {file_path}")
                    continue

                # Verificar idade do arquivo
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                file_age = now - file_time

                # Verificar se o arquivo foi processado
                file_processed = file_path in processed_files

                # Adicionar à lista se for antigo ou já foi processado
                if file_age > max_age or (file_processed and self.policy.should_remove_after_processing()):
                    old_uploads.append(file_path)
                    self.stats["uploads_identified"] += 1
                    logger.debug(f"Arquivo de upload obsoleto identificado: {file_path}")

        except Exception as e:
            logger.error(f"Erro ao identificar uploads obsoletos: {str(e)}")

        return old_uploads

    def identify_old_results(self) -> List[str]:
        """
        Identifica diretórios de resultados obsoletos com base na política de retenção.

        Returns:
            Lista de caminhos para diretórios de resultados obsoletos
        """
        old_results = []
        max_age = self.policy.get_results_max_age()
        now = datetime.now()

        try:
            # Verificar cada diretório no diretório de resultados
            for result_id in os.listdir(self.results_dir):
                result_dir = os.path.join(self.results_dir, result_id)

                # Ignorar arquivos (esperamos apenas diretórios)
                if not os.path.isdir(result_dir):
                    continue

                # Verificar se o resultado está isento com base em tags
                metadata_file = os.path.join(result_dir, "metadata.json")
                tags = []

                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)
                            tags = metadata.get("tags", [])
                    except Exception as e:
                        logger.warning(f"Erro ao ler metadados de {result_dir}: {str(e)}")

                if self.policy.is_result_exempt(tags):
                    logger.debug(f"Resultado isento por tags: {result_dir}")
                    continue

                # Determinar a data de referência (criação ou último acesso)
                if self.policy.should_consider_last_access():
                    # Encontrar o arquivo mais recentemente acessado no diretório
                    latest_access_time = None

                    for root, _, files in os.walk(result_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                # Usar mtime como aproximação para último acesso
                                # (atime nem sempre é confiável em sistemas de arquivos modernos)
                                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                                if latest_access_time is None or file_time > latest_access_time:
                                    latest_access_time = file_time
                            except Exception:
                                pass

                    reference_time = latest_access_time or datetime.fromtimestamp(os.path.getmtime(result_dir))
                else:
                    # Usar apenas a data de criação do diretório
                    reference_time = datetime.fromtimestamp(os.path.getmtime(result_dir))

                # Verificar idade do resultado
                result_age = now - reference_time

                if result_age > max_age:
                    old_results.append(result_dir)
                    self.stats["results_identified"] += 1
                    logger.debug(f"Resultado obsoleto identificado: {result_dir}")

        except Exception as e:
            logger.error(f"Erro ao identificar resultados obsoletos: {str(e)}")

        return old_results

    def identify_temp_files(self) -> List[str]:
        """
        Identifica arquivos temporários obsoletos no diretório temporário do sistema.

        Returns:
            Lista de caminhos para arquivos temporários obsoletos
        """
        old_temp_files = []
        max_age = self.policy.get_temp_files_max_age()
        now = datetime.now()

        try:
            # Verificar diretório temporário do sistema
            temp_dir = tempfile.gettempdir()

            # Padrão para identificar arquivos temporários criados pelo Docling
            # (pode ser ajustado conforme necessário)
            docling_temp_patterns = ["docling_", "doc_processing_"]

            for filename in os.listdir(temp_dir):
                # Verificar se o arquivo parece ser do Docling
                if not any(pattern in filename for pattern in docling_temp_patterns):
                    continue

                file_path = os.path.join(temp_dir, filename)

                # Ignorar diretórios
                if not os.path.isfile(file_path):
                    continue

                # Verificar idade do arquivo
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    file_age = now - file_time

                    if file_age > max_age:
                        old_temp_files.append(file_path)
                        self.stats["temp_files_identified"] += 1
                        logger.debug(f"Arquivo temporário obsoleto identificado: {file_path}")
                except Exception as e:
                    logger.warning(f"Erro ao verificar arquivo temporário {file_path}: {str(e)}")

        except Exception as e:
            logger.error(f"Erro ao identificar arquivos temporários obsoletos: {str(e)}")

        return old_temp_files

    def remove_files(self, file_paths: List[str], file_type: str) -> int:
        """
        Remove arquivos de forma segura.

        Args:
            file_paths: Lista de caminhos para arquivos a serem removidos
            file_type: Tipo de arquivo ("uploads", "results" ou "temp_files")

        Returns:
            Número de arquivos removidos com sucesso
        """
        removed_count = 0

        for file_path in file_paths:
            try:
                # Verificar se o arquivo/diretório existe
                if not os.path.exists(file_path):
                    logger.warning(f"Arquivo não encontrado: {file_path}")
                    continue

                # Calcular tamanho para estatísticas
                size = 0
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                elif os.path.isdir(file_path):
                    for dirpath, _, filenames in os.walk(file_path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if os.path.exists(fp):
                                size += os.path.getsize(fp)

                # Remover arquivo ou diretório (apenas se não estiver em modo dry-run)
                if not self.dry_run:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)

                # Atualizar estatísticas
                removed_count += 1
                self.stats[f"{file_type}_removed"] += 1
                self.stats[f"{file_type}_bytes_freed"] += size

                logger.info(f"{'[DRY RUN] Simulação de remoção' if self.dry_run else 'Removido'}: {file_path}")

            except Exception as e:
                logger.error(f"Erro ao remover {file_path}: {str(e)}")

        return removed_count

    def clean_all(self) -> Dict[str, Any]:
        """
        Identifica e remove todos os arquivos temporários obsoletos.

        Returns:
            Estatísticas da operação de limpeza
        """
        logger.info(f"Iniciando limpeza de arquivos temporários (modo {'simulação' if self.dry_run else 'real'})")

        # Identificar arquivos obsoletos
        old_uploads = self.identify_old_uploads()
        old_results = self.identify_old_results()
        old_temp_files = self.identify_temp_files()

        # Remover arquivos obsoletos
        self.remove_files(old_uploads, "uploads")
        self.remove_files(old_results, "results")
        self.remove_files(old_temp_files, "temp_files")

        # Calcular estatísticas totais
        total_identified = (
            self.stats["uploads_identified"] +
            self.stats["results_identified"] +
            self.stats["temp_files_identified"]
        )

        total_removed = (
            self.stats["uploads_removed"] +
            self.stats["results_removed"] +
            self.stats["temp_files_removed"]
        )

        total_bytes_freed = (
            self.stats["uploads_bytes_freed"] +
            self.stats["results_bytes_freed"] +
            self.stats["temp_files_bytes_freed"]
        )

        # Adicionar estatísticas totais
        self.stats["total_identified"] = total_identified
        self.stats["total_removed"] = total_removed
        self.stats["total_bytes_freed"] = total_bytes_freed
        self.stats["human_readable_freed"] = self._format_size(total_bytes_freed)
        self.stats["dry_run"] = self.dry_run
        self.stats["timestamp"] = datetime.now().isoformat()

        logger.info(f"Limpeza concluída: {total_removed}/{total_identified} arquivos removidos, {self._format_size(total_bytes_freed)} liberados")

        return self.stats

    def _get_processed_original_files(self) -> Set[str]:
        """
        Obtém o conjunto de arquivos originais que já foram processados.

        Returns:
            Conjunto de caminhos para arquivos originais processados
        """
        processed_files = set()

        try:
            # Verificar cada diretório no diretório de resultados
            for result_id in os.listdir(self.results_dir):
                result_dir = os.path.join(self.results_dir, result_id)

                # Ignorar arquivos (esperamos apenas diretórios)
                if not os.path.isdir(result_dir):
                    continue

                # Verificar arquivo de metadados
                metadata_file = os.path.join(result_dir, "metadata.json")

                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)

                            # Verificar se o processamento foi bem-sucedido
                            if metadata.get("status") == "success":
                                # Obter nome do arquivo original
                                original_filename = metadata.get("original_filename")

                                if original_filename:
                                    # Construir caminho para o arquivo original no diretório de uploads
                                    # Nota: Isso é uma aproximação, pois o nome real do arquivo no diretório
                                    # de uploads pode ser diferente (UUID)
                                    for filename in os.listdir(self.upload_dir):
                                        file_path = os.path.join(self.upload_dir, filename)
                                        processed_files.add(file_path)

                    except Exception as e:
                        logger.warning(f"Erro ao ler metadados de {result_dir}: {str(e)}")

        except Exception as e:
            logger.error(f"Erro ao obter arquivos processados: {str(e)}")

        return processed_files

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        Formata um tamanho em bytes para uma representação legível.

        Args:
            size_bytes: Tamanho em bytes

        Returns:
            Tamanho formatado (ex: "1.23 MB")
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1

        return f"{size_bytes:.2f} {size_names[i]}"


def clean_temp_files(dry_run: bool = False) -> Dict[str, Any]:
    """
    Função de conveniência para limpar arquivos temporários.

    Args:
        dry_run: Se True, não remove arquivos, apenas simula a remoção

    Returns:
        Estatísticas da operação de limpeza
    """
    cleaner = FileCleaner(dry_run=dry_run)
    return cleaner.clean_all()
