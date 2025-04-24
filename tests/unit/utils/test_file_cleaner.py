"""
Testes para o módulo app.utils.file_cleaner
"""
import os
import json
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

from app.utils.file_cleaner import FileCleaner
from app.core.retention_policy import RetentionPolicy


@pytest.fixture
def mock_retention_policy():
    """Fixture para simular a política de retenção."""
    policy = RetentionPolicy({
        "uploads": {
            "max_age_days": 1,
            "remove_after_processing": True,
        },
        "temp_files": {
            "max_age_hours": 24,
        },
        "results": {
            "max_age_days": 7,
            "consider_last_access": True,
        }
    })
    return policy


@pytest.fixture
def temp_dirs():
    """Fixture para criar diretórios temporários para testes."""
    # Criar diretórios temporários
    base_dir = tempfile.mkdtemp()
    upload_dir = os.path.join(base_dir, "uploads")
    results_dir = os.path.join(base_dir, "results")

    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    yield {
        "base_dir": base_dir,
        "upload_dir": upload_dir,
        "results_dir": results_dir,
    }

    # Limpar após o teste
    shutil.rmtree(base_dir)


@pytest.fixture
def create_test_files(temp_dirs):
    """Fixture para criar arquivos de teste."""
    def _create_files(file_type, count, age_days=0):
        """
        Cria arquivos de teste com idade específica.

        Args:
            file_type: Tipo de arquivo ("uploads" ou "results")
            count: Número de arquivos a serem criados
            age_days: Idade dos arquivos em dias

        Returns:
            Lista de caminhos para os arquivos criados
        """
        created_files = []

        if file_type == "uploads":
            target_dir = temp_dirs["upload_dir"]
            file_prefix = "upload_"
            file_ext = ".pdf"
        elif file_type == "results":
            target_dir = temp_dirs["results_dir"]
            file_prefix = "result_"
            file_ext = ""  # Diretórios para resultados
        else:
            raise ValueError(f"Tipo de arquivo inválido: {file_type}")

        # Calcular datas para os arquivos
        now = datetime.now()
        past_date = now - timedelta(days=age_days)
        timestamp = past_date.timestamp()

        for i in range(count):
            if file_type == "uploads":
                # Criar arquivo
                file_path = os.path.join(target_dir, f"{file_prefix}{i}{file_ext}")
                with open(file_path, "w") as f:
                    f.write(f"Conteúdo de teste para {file_path}")

                # Definir data de modificação
                os.utime(file_path, (timestamp, timestamp))

                created_files.append(file_path)
            else:  # results
                # Criar diretório de resultado
                result_dir = os.path.join(target_dir, f"{file_prefix}{i}")
                os.makedirs(result_dir, exist_ok=True)

                # Criar arquivo de metadados com data de processamento consistente com a idade
                metadata_file = os.path.join(result_dir, "metadata.json")
                metadata = {
                    "id": f"{file_prefix}{i}",
                    "original_filename": f"upload_{i}.pdf",  # Nome consistente com os uploads
                    "processed_at": past_date.isoformat(),  # Data consistente com a idade
                    "status": "success",
                }

                with open(metadata_file, "w") as f:
                    json.dump(metadata, f)

                # Criar arquivo de conteúdo
                content_file = os.path.join(result_dir, "content.md")
                with open(content_file, "w") as f:
                    f.write(f"# Conteúdo de teste para {result_dir}")

                # Criar uma cópia do arquivo original no diretório de resultados
                original_copy = os.path.join(result_dir, f"upload_{i}.pdf")
                with open(original_copy, "w") as f:
                    f.write(f"Conteúdo original para {original_copy}")

                # Definir data de modificação para todos os arquivos e o diretório
                os.utime(result_dir, (timestamp, timestamp))
                os.utime(metadata_file, (timestamp, timestamp))
                os.utime(content_file, (timestamp, timestamp))
                os.utime(original_copy, (timestamp, timestamp))

                created_files.append(result_dir)

        return created_files

    return _create_files


class TestFileCleaner:
    """Testes para a classe FileCleaner."""

    def test_init(self, mock_retention_policy):
        """Testa se o limpador é inicializado corretamente."""
        with patch("app.utils.file_cleaner.retention_policy", mock_retention_policy):
            cleaner = FileCleaner(dry_run=True)

            assert cleaner.dry_run is True
            assert cleaner.policy == mock_retention_policy
            assert isinstance(cleaner.stats, dict)

    def test_identify_old_uploads(self, temp_dirs, create_test_files, mock_retention_policy):
        """Testa a identificação de uploads obsoletos."""
        # Criar arquivos de teste
        recent_files = create_test_files("uploads", 3, age_days=0)  # Arquivos recentes
        old_files = create_test_files("uploads", 2, age_days=2)  # Arquivos antigos

        # Criar uma política de retenção específica para o teste
        test_policy = RetentionPolicy({
            "uploads": {
                "max_age_days": 1,  # Manter por 1 dia
                "remove_after_processing": False,  # Não remover após processamento
                "exempt_extensions": [],  # Sem extensões isentas
            }
        })

        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", test_policy), \
             patch("app.utils.file_cleaner.FileCleaner._get_processed_original_files", return_value=set()):

            cleaner = FileCleaner(dry_run=True)
            old_uploads = cleaner.identify_old_uploads()

            # Verificar se apenas os arquivos antigos foram identificados
            assert len(old_uploads) == 2, f"Esperava 2 arquivos antigos, encontrou {len(old_uploads)}: {old_uploads}"

            # Verificar se todos os arquivos antigos foram identificados
            old_paths = set(old_files)
            found_paths = set(old_uploads)
            assert old_paths.issubset(found_paths), f"Nem todos os arquivos antigos foram identificados. Esperava {old_paths}, encontrou {found_paths}"

            # Verificar se nenhum arquivo recente foi identificado como antigo
            recent_paths = set(recent_files)
            assert recent_paths.isdisjoint(found_paths), f"Arquivos recentes foram incorretamente identificados como antigos: {recent_paths.intersection(found_paths)}"

    def test_identify_old_results(self, temp_dirs, create_test_files, mock_retention_policy):
        """Testa a identificação de resultados obsoletos."""
        # Criar diretórios de resultados de teste
        recent_results = create_test_files("results", 3, age_days=1)  # Resultados recentes
        old_results = create_test_files("results", 2, age_days=10)  # Resultados antigos

        # Modificar a política de retenção para o teste
        test_policy = RetentionPolicy({
            "results": {
                "max_age_days": 7,  # Manter por 7 dias
                "consider_last_access": True,
            }
        })

        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", test_policy):

            cleaner = FileCleaner(dry_run=True)
            old_results_found = cleaner.identify_old_results()

            # Verificar se apenas os resultados antigos foram identificados
            assert len(old_results_found) == 2, f"Esperava 2 resultados antigos, encontrou {len(old_results_found)}"

            # Verificar se todos os resultados antigos foram identificados
            old_paths = set(old_results)
            found_paths = set(old_results_found)
            assert old_paths.issubset(found_paths), f"Nem todos os resultados antigos foram identificados. Esperava {old_paths}, encontrou {found_paths}"

            # Verificar se nenhum resultado recente foi identificado como antigo
            recent_paths = set(recent_results)
            assert recent_paths.isdisjoint(found_paths), f"Resultados recentes foram incorretamente identificados como antigos: {recent_paths.intersection(found_paths)}"

    def test_remove_files_dry_run(self, temp_dirs, create_test_files, mock_retention_policy):
        """Testa a remoção de arquivos em modo dry-run."""
        # Criar arquivos de teste
        files = create_test_files("uploads", 3, age_days=0)

        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", mock_retention_policy):

            cleaner = FileCleaner(dry_run=True)
            removed_count = cleaner.remove_files(files, "uploads")

            # Verificar se os arquivos não foram removidos (dry-run)
            assert removed_count == 3
            for file_path in files:
                assert os.path.exists(file_path)

    def test_remove_files_real(self, temp_dirs, create_test_files, mock_retention_policy):
        """Testa a remoção real de arquivos."""
        # Criar arquivos de teste
        files = create_test_files("uploads", 3, age_days=0)

        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", mock_retention_policy):

            cleaner = FileCleaner(dry_run=False)
            removed_count = cleaner.remove_files(files, "uploads")

            # Verificar se os arquivos foram removidos
            assert removed_count == 3
            for file_path in files:
                assert not os.path.exists(file_path)

    def test_clean_all(self, temp_dirs, create_test_files, mock_retention_policy):
        """Testa a limpeza completa."""
        # Criar arquivos de teste
        old_uploads = create_test_files("uploads", 2, age_days=2)
        recent_uploads = create_test_files("uploads", 1, age_days=0)
        old_results = create_test_files("results", 2, age_days=10)
        recent_results = create_test_files("results", 1, age_days=1)

        # Modificar a política de retenção para o teste
        test_policy = RetentionPolicy({
            "uploads": {
                "max_age_days": 1,
                "remove_after_processing": True,
            },
            "results": {
                "max_age_days": 7,  # Manter por 7 dias
                "consider_last_access": True,
            }
        })

        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", test_policy), \
             patch("app.utils.file_cleaner.FileCleaner.identify_temp_files", return_value=[]), \
             patch("app.utils.file_cleaner.FileCleaner._get_processed_original_files", return_value=set()):

            # Testar em modo dry-run
            cleaner = FileCleaner(dry_run=True)
            stats = cleaner.clean_all()

            # Verificar estatísticas
            assert stats["uploads_identified"] == 2, f"Esperava 2 uploads identificados, encontrou {stats['uploads_identified']}"
            assert stats["results_identified"] == 2, f"Esperava 2 resultados identificados, encontrou {stats['results_identified']}"
            assert stats["total_identified"] == 4, f"Esperava 4 arquivos identificados no total, encontrou {stats['total_identified']}"

            # Verificar que os arquivos ainda existem (dry-run)
            for file_path in old_uploads + old_results + recent_uploads + recent_results:
                assert os.path.exists(file_path), f"Arquivo deveria existir em modo dry-run: {file_path}"

            # Testar remoção real
            cleaner = FileCleaner(dry_run=False)
            stats = cleaner.clean_all()

            # Verificar que os arquivos antigos foram removidos
            for file_path in old_uploads:
                assert not os.path.exists(file_path), f"Arquivo antigo deveria ter sido removido: {file_path}"

            for file_path in old_results:
                assert not os.path.exists(file_path), f"Resultado antigo deveria ter sido removido: {file_path}"

            # Verificar que os arquivos recentes ainda existem
            for file_path in recent_uploads:
                assert os.path.exists(file_path), f"Arquivo recente não deveria ter sido removido: {file_path}"

            for file_path in recent_results:
                assert os.path.exists(file_path), f"Resultado recente não deveria ter sido removido: {file_path}"

    def test_format_size(self):
        """Testa a formatação de tamanho em bytes."""
        assert FileCleaner._format_size(0) == "0 B"
        assert FileCleaner._format_size(1023) == "1023.00 B"
        assert FileCleaner._format_size(1024) == "1.00 KB"
        assert FileCleaner._format_size(1024 * 1024) == "1.00 MB"
        assert FileCleaner._format_size(1024 * 1024 * 1024) == "1.00 GB"
