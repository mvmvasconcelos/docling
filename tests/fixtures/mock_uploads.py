"""
Fixtures para simular uploads de arquivos.
"""
import os
import io
import tempfile
import shutil
from pathlib import Path
import pytest
from fastapi import UploadFile
from unittest.mock import MagicMock


@pytest.fixture
def temp_upload_dir():
    """Cria um diretório temporário para uploads de teste."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Limpar após o teste
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_results_dir():
    """Cria um diretório temporário para resultados de teste."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Limpar após o teste
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_text_file():
    """Cria um arquivo de texto temporário para testes."""
    content = "Este é um arquivo de texto para teste.\nSegunda linha do arquivo."
    file_obj = io.BytesIO(content.encode("utf-8"))
    file_obj.name = "test_file.txt"
    
    # Criar um UploadFile simulado
    upload_file = UploadFile(
        filename="test_file.txt",
        file=file_obj,
        content_type="text/plain",
    )
    
    yield upload_file
    
    # Fechar o arquivo
    file_obj.close()


@pytest.fixture
def mock_docx_upload():
    """Simula um upload de arquivo DOCX."""
    content = b"Conteúdo binário simulado para DOCX"
    file_obj = io.BytesIO(content)
    file_obj.name = "test_document.docx"
    
    # Criar um UploadFile simulado
    upload_file = UploadFile(
        filename="test_document.docx",
        file=file_obj,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    
    yield upload_file
    
    # Fechar o arquivo
    file_obj.close()


@pytest.fixture
def mock_pdf_upload():
    """Simula um upload de arquivo PDF."""
    content = b"Conteúdo binário simulado para PDF"
    file_obj = io.BytesIO(content)
    file_obj.name = "test_document.pdf"
    
    # Criar um UploadFile simulado
    upload_file = UploadFile(
        filename="test_document.pdf",
        file=file_obj,
        content_type="application/pdf",
    )
    
    yield upload_file
    
    # Fechar o arquivo
    file_obj.close()


@pytest.fixture
def mock_excel_upload():
    """Simula um upload de arquivo Excel."""
    content = b"Conteúdo binário simulado para Excel"
    file_obj = io.BytesIO(content)
    file_obj.name = "test_document.xlsx"
    
    # Criar um UploadFile simulado
    upload_file = UploadFile(
        filename="test_document.xlsx",
        file=file_obj,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    
    yield upload_file
    
    # Fechar o arquivo
    file_obj.close()


@pytest.fixture
def save_upload_file():
    """
    Função auxiliar para salvar um arquivo de upload em um diretório temporário.
    
    Returns:
        Uma função que salva um arquivo de upload e retorna o caminho do arquivo salvo.
    """
    
    async def _save_upload_file(upload_file, upload_dir):
        """
        Salva um arquivo de upload em um diretório.
        
        Args:
            upload_file: O arquivo de upload (UploadFile)
            upload_dir: O diretório onde salvar o arquivo
            
        Returns:
            O caminho do arquivo salvo
        """
        # Garantir que o diretório exista
        os.makedirs(upload_dir, exist_ok=True)
        
        # Criar o caminho completo do arquivo
        file_path = os.path.join(upload_dir, upload_file.filename)
        
        # Salvar o arquivo
        with open(file_path, "wb") as f:
            content = await upload_file.read()
            f.write(content)
            
        # Voltar o cursor do arquivo para o início para permitir leituras futuras
        await upload_file.seek(0)
        
        return file_path
    
    return _save_upload_file
