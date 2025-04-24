"""
Testes para o módulo app.api.routes
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.api.routes import router


# Cliente de teste para simular requisições HTTP
client = TestClient(app)


@pytest.fixture
def mock_process_document():
    """Fixture para simular a função process_document."""
    with patch("app.api.routes.process_document") as mock:
        # Configurar o mock para retornar um resultado de processamento
        mock.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "original_filename": "test_document.pdf",
            "processed_at": datetime.now().isoformat(),
            "file_type": "pdf",
            "file_size": 1024,
            "status": "success",
            "message": "Documento processado com sucesso",
            "content": {
                "text": "Conteúdo de teste",
                "markdown": "# Título\n\nConteúdo de teste",
                "html": "<h1>Título</h1><p>Conteúdo de teste</p>",
            },
        }
        yield mock


@pytest.fixture
def mock_get_document_info():
    """Fixture para simular a função get_document_info."""
    with patch("app.api.routes.get_document_info") as mock:
        # Configurar o mock para retornar informações de documento
        mock.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "original_filename": "test_document.pdf",
            "processed_at": datetime.now().isoformat(),
            "file_type": "pdf",
            "file_size": 1024,
            "status": "success",
            "message": "Documento processado com sucesso",
            "content": {
                "text": "Conteúdo de teste",
                "markdown": "# Título\n\nConteúdo de teste",
                "html": "<h1>Título</h1><p>Conteúdo de teste</p>",
            },
            "files": {
                "metadata": "/app/results/123e4567-e89b-12d3-a456-426614174000/metadata.json",
                "markdown": "/app/results/123e4567-e89b-12d3-a456-426614174000/content.md",
                "html": "/app/results/123e4567-e89b-12d3-a456-426614174000/content.html",
                "original": "/app/results/123e4567-e89b-12d3-a456-426614174000/test_document.pdf",
            },
        }
        yield mock


@pytest.fixture
def mock_file_response():
    """Fixture para simular a resposta de arquivo."""
    with patch("app.api.routes.FileResponse") as mock:
        # Configurar o mock para retornar uma resposta de arquivo
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_open_file():
    """Fixture para simular a abertura de arquivos."""
    with patch("builtins.open", mock_open(read_data="Conteúdo de teste")) as mock:
        yield mock


class TestAPIRoutes:
    """Testes para as rotas da API."""

    def test_health_check(self):
        """Testa o endpoint de verificação de saúde."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()

    def test_get_version(self):
        """Testa o endpoint de versão."""
        response = client.get("/api/version")
        assert response.status_code == 200
        assert "version" in response.json()
        assert "phase" in response.json()
        assert "last_updated" in response.json()

    def test_upload_and_process_document_success(self, mock_process_document):
        """Testa o upload e processamento de documento com sucesso."""
        # Criar um arquivo de teste
        files = {"file": ("test_document.pdf", b"PDF content", "application/pdf")}
        data = {"extract_text": "true", "extract_tables": "true", "extract_images": "false"}

        # Simular a requisição
        with patch("builtins.open", mock_open()):
            with patch("os.path.exists", return_value=True):
                with patch("uuid.uuid4", return_value="123e4567-e89b-12d3-a456-426614174000"):
                    response = client.post("/api/process", files=files, data=data)

        # Verificar o resultado
        assert response.status_code == 200
        assert response.json()["id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert response.json()["original_filename"] == "test_document.pdf"
        assert response.json()["status"] == "success"

    def test_upload_and_process_document_invalid_extension(self):
        """Testa o upload de documento com extensão inválida."""
        # Criar um arquivo de teste com extensão inválida
        files = {"file": ("test_document.txt", b"Text content", "text/plain")}
        data = {"extract_text": "true", "extract_tables": "true", "extract_images": "false"}

        # Simular a requisição
        response = client.post("/api/process", files=files, data=data)

        # Verificar o resultado
        assert response.status_code == 400
        assert "Tipo de arquivo não suportado" in response.json().get("message", "")

    def test_upload_and_process_document_error(self, mock_process_document):
        """Testa o upload e processamento de documento com erro."""
        # Configurar o mock para lançar uma exceção
        mock_process_document.side_effect = Exception("Erro simulado")

        # Criar um arquivo de teste
        files = {"file": ("test_document.pdf", b"PDF content", "application/pdf")}
        data = {"extract_text": "true", "extract_tables": "true", "extract_images": "false"}

        # Simular a requisição
        with patch("builtins.open", mock_open()):
            with patch("os.path.exists", return_value=True):
                with patch("os.remove"):  # Mock para remover o arquivo em caso de erro
                    with patch("uuid.uuid4", return_value="123e4567-e89b-12d3-a456-426614174000"):
                        response = client.post("/api/process", files=files, data=data)

        # Verificar o resultado - a API retorna 200 mesmo em caso de erro, com status "error"
        assert response.status_code == 200
        assert response.json().get("status") == "error"
        assert "Erro ao processar o documento" in response.json().get("error", "")

    def test_get_document_success(self, mock_get_document_info):
        """Testa a obtenção de informações de documento com sucesso."""
        # Simular a requisição
        response = client.get("/api/documents/123e4567-e89b-12d3-a456-426614174000")

        # Verificar o resultado
        assert response.status_code == 200
        assert response.json()["id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert response.json()["original_filename"] == "test_document.pdf"
        assert response.json()["status"] == "success"

    def test_get_document_not_found(self, mock_get_document_info):
        """Testa a obtenção de informações de documento não encontrado."""
        # Configurar o mock para retornar None (documento não encontrado)
        mock_get_document_info.return_value = None

        # Simular a requisição
        response = client.get("/api/documents/nonexistent-id")

        # Verificar o resultado
        assert response.status_code == 404
        assert "Documento não encontrado" in response.json().get("message", "")

    def test_get_document_error(self, mock_get_document_info):
        """Testa a obtenção de informações de documento com erro."""
        # Configurar o mock para lançar uma exceção
        mock_get_document_info.side_effect = Exception("Erro simulado")

        # Simular a requisição
        response = client.get("/api/documents/123e4567-e89b-12d3-a456-426614174000")

        # Verificar o resultado
        assert response.status_code == 500
        assert "Erro ao obter informações do documento" in response.json().get("message", "")

    def test_download_document_success(self, mock_get_document_info, mock_file_response):
        """Testa o download de documento com sucesso."""
        # Simular a requisição para diferentes formatos
        for format in ["original", "markdown", "html"]:
            with patch("os.path.exists", return_value=True):
                response = client.get(f"/api/documents/123e4567-e89b-12d3-a456-426614174000/download/{format}")

            # Verificar o resultado
            assert response.status_code == 200

    def test_download_document_not_found(self, mock_get_document_info):
        """Testa o download de documento não encontrado."""
        # Configurar o mock para retornar None (documento não encontrado)
        mock_get_document_info.return_value = None

        # Simular a requisição
        response = client.get("/api/documents/nonexistent-id/download/original")

        # Verificar o resultado
        assert response.status_code == 404
        assert "Documento não encontrado" in response.json().get("message", "")

    def test_download_document_invalid_format(self, mock_get_document_info):
        """Testa o download de documento com formato inválido."""
        # Simular a requisição com formato inválido
        response = client.get("/api/documents/123e4567-e89b-12d3-a456-426614174000/download/invalid")

        # Verificar o resultado
        assert response.status_code == 400
        assert "Formato não suportado" in response.json().get("message", "")

    def test_download_document_format_not_available(self, mock_get_document_info):
        """Testa o download de documento com formato não disponível."""
        # Configurar o mock para retornar informações sem o formato solicitado
        mock_get_document_info.return_value["files"]["markdown"] = None

        # Simular a requisição
        with patch("os.path.exists", return_value=False):
            response = client.get("/api/documents/123e4567-e89b-12d3-a456-426614174000/download/markdown")

        # Verificar o resultado
        assert response.status_code == 404
        assert "Arquivo no formato markdown não disponível" in response.json().get("message", "")

    def test_preview_document_success(self, mock_get_document_info):
        """Testa a visualização de documento com sucesso."""
        # Simular a requisição para diferentes formatos
        for format in ["markdown", "html", "text"]:
            with patch("os.path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data="Conteúdo de teste")):
                    response = client.get(f"/api/documents/123e4567-e89b-12d3-a456-426614174000/preview/{format}")

            # Verificar o resultado
            assert response.status_code == 200
            if format == "html":
                assert response.headers["content-type"] == "text/html; charset=utf-8"
            else:
                assert response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_preview_document_not_found(self, mock_get_document_info):
        """Testa a visualização de documento não encontrado."""
        # Configurar o mock para retornar None (documento não encontrado)
        mock_get_document_info.return_value = None

        # Simular a requisição
        response = client.get("/api/documents/nonexistent-id/preview/markdown")

        # Verificar o resultado
        assert response.status_code == 404
        assert "Documento não encontrado" in response.json().get("message", "")

    def test_preview_document_invalid_format(self, mock_get_document_info):
        """Testa a visualização de documento com formato inválido."""
        # Simular a requisição com formato inválido
        response = client.get("/api/documents/123e4567-e89b-12d3-a456-426614174000/preview/invalid")

        # Verificar o resultado
        assert response.status_code == 400
        assert "Formato não suportado" in response.json().get("message", "")

    def test_preview_document_format_not_available(self, mock_get_document_info):
        """Testa a visualização de documento com formato não disponível."""
        # Configurar o mock para retornar informações sem o formato solicitado
        mock_get_document_info.return_value["files"]["markdown"] = None

        # Simular a requisição
        with patch("os.path.exists", return_value=False):
            response = client.get("/api/documents/123e4567-e89b-12d3-a456-426614174000/preview/markdown")

        # Verificar o resultado
        assert response.status_code == 404
        assert "Conteúdo no formato markdown não disponível" in response.json().get("message", "")
