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
        
        # Calcular timestamp para a data modificada
        now = datetime.now()
        timestamp = (now - timedelta(days=age_days)).timestamp()
        
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
                
                # Criar arquivo de metadados
                metadata_file = os.path.join(result_dir, "metadata.json")
                metadata = {
                    "id": f"{file_prefix}{i}",
                    "original_filename": f"original_{i}.pdf",
                    "processed_at": now.isoformat(),
                    "status": "success",
                }
                
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f)
                
                # Criar arquivo de conteúdo
                content_file = os.path.join(result_dir, "content.md")
                with open(content_file, "w") as f:
                    f.write(f"# Conteúdo de teste para {result_dir}")
                
                # Definir data de modificação
                os.utime(result_dir, (timestamp, timestamp))
                os.utime(metadata_file, (timestamp, timestamp))
                os.utime(content_file, (timestamp, timestamp))
                
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
        
        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", mock_retention_policy):
            
            cleaner = FileCleaner(dry_run=True)
            old_uploads = cleaner.identify_old_uploads()
            
            # Verificar se apenas os arquivos antigos foram identificados
            assert len(old_uploads) == 2
            for file_path in old_files:
                assert file_path in old_uploads
            for file_path in recent_files:
                assert file_path not in old_uploads
    
    def test_identify_old_results(self, temp_dirs, create_test_files, mock_retention_policy):
        """Testa a identificação de resultados obsoletos."""
        # Criar diretórios de resultados de teste
        recent_results = create_test_files("results", 3, age_days=1)  # Resultados recentes
        old_results = create_test_files("results", 2, age_days=10)  # Resultados antigos
        
        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", mock_retention_policy):
            
            cleaner = FileCleaner(dry_run=True)
            old_results_found = cleaner.identify_old_results()
            
            # Verificar se apenas os resultados antigos foram identificados
            assert len(old_results_found) == 2
            for result_dir in old_results:
                assert result_dir in old_results_found
            for result_dir in recent_results:
                assert result_dir not in old_results_found
    
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
        
        with patch("app.utils.file_cleaner.UPLOAD_DIR", temp_dirs["upload_dir"]), \
             patch("app.utils.file_cleaner.RESULTS_DIR", temp_dirs["results_dir"]), \
             patch("app.utils.file_cleaner.retention_policy", mock_retention_policy), \
             patch("app.utils.file_cleaner.FileCleaner.identify_temp_files", return_value=[]):
            
            cleaner = FileCleaner(dry_run=True)
            stats = cleaner.clean_all()
            
            # Verificar estatísticas
            assert stats["uploads_identified"] == 2
            assert stats["results_identified"] == 2
            assert stats["total_identified"] == 4
            
            # Verificar que os arquivos ainda existem (dry-run)
            for file_path in old_uploads + old_results + recent_uploads + recent_results:
                assert os.path.exists(file_path)
            
            # Testar remoção real
            cleaner = FileCleaner(dry_run=False)
            stats = cleaner.clean_all()
            
            # Verificar que os arquivos antigos foram removidos
            for file_path in old_uploads + old_results:
                assert not os.path.exists(file_path)
            
            # Verificar que os arquivos recentes ainda existem
            for file_path in recent_uploads + recent_results:
                assert os.path.exists(file_path)
    
    def test_format_size(self):
        """Testa a formatação de tamanho em bytes."""
        assert FileCleaner._format_size(0) == "0 B"
        assert FileCleaner._format_size(1023) == "1023.00 B"
        assert FileCleaner._format_size(1024) == "1.00 KB"
        assert FileCleaner._format_size(1024 * 1024) == "1.00 MB"
        assert FileCleaner._format_size(1024 * 1024 * 1024) == "1.00 GB"
