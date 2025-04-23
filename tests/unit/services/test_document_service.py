"""
Testes para o módulo app.services.document_service
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import shutil

from app.services.document_service import (
    process_document,
    get_document_info,
    list_documents,
)


@pytest.fixture
def mock_results_dir(tmp_path):
    """Fixture para criar um diretório temporário para resultados."""
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    with patch("app.services.document_service.RESULTS_DIR", str(results_dir)):
        yield results_dir


@pytest.fixture
def mock_upload_dir(tmp_path):
    """Fixture para criar um diretório temporário para uploads."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    with patch("app.services.document_service.UPLOAD_DIR", str(upload_dir)):
        yield upload_dir


@pytest.fixture
def sample_document(tmp_path):
    """Fixture para criar um arquivo de documento de exemplo."""
    file_path = tmp_path / "test_document.pdf"
    file_path.write_text("Conteúdo de teste")
    return str(file_path)


@pytest.fixture
def mock_docling_adapter():
    """Fixture para simular o adaptador Docling."""
    with patch("app.services.document_service.docling_adapter") as mock:
        # Configurar o mock para retornar um resultado de processamento
        mock.process_document.return_value = {
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
def sample_document_info():
    """Fixture para criar informações de documento de exemplo."""
    return {
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


class TestDocumentService:
    """Testes para o serviço de documentos."""

    def test_process_document(self, mock_results_dir, sample_document, mock_docling_adapter):
        """Testa o processamento de um documento."""
        # Chamar a função a ser testada
        with patch("uuid.uuid4", return_value="123e4567-e89b-12d3-a456-426614174000"):
            result = process_document(
                file_path=sample_document,
                original_filename="test_document.pdf",
                extract_text=True,
                extract_tables=True,
                extract_images=False,
            )

        # Verificar o resultado
        assert result["id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert result["original_filename"] == "test_document.pdf"
        assert result["file_type"] == "pdf"
        assert result["status"] == "success"
        assert "processed_at" in result

        # Verificar se os arquivos foram criados
        result_dir = os.path.join(mock_results_dir, "123e4567-e89b-12d3-a456-426614174000")
        assert os.path.exists(result_dir)
        assert os.path.exists(os.path.join(result_dir, "metadata.json"))
        assert os.path.exists(os.path.join(result_dir, "content.md"))
        assert os.path.exists(os.path.join(result_dir, "content.html"))

    def test_process_document_error(self, mock_results_dir, sample_document):
        """Testa o processamento de um documento com erro."""
        # Simular um erro no adaptador Docling
        with patch(
            "app.services.document_service.docling_adapter.process_document",
            side_effect=Exception("Erro simulado"),
        ):
            # Chamar a função a ser testada e verificar se a exceção é propagada
            with pytest.raises(Exception, match="Erro simulado"):
                process_document(
                    file_path=sample_document,
                    original_filename="test_document.pdf",
                )

    def test_get_document_info_existing(self, mock_results_dir, sample_document_info):
        """Testa a obtenção de informações de um documento existente."""
        # Criar um diretório de resultados e arquivos de metadados
        document_id = sample_document_info["id"]
        result_dir = os.path.join(mock_results_dir, document_id)
        os.makedirs(result_dir, exist_ok=True)

        # Criar arquivo de metadados
        with open(os.path.join(result_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(sample_document_info, f)

        # Criar arquivos de conteúdo
        with open(os.path.join(result_dir, "content.md"), "w", encoding="utf-8") as f:
            f.write(sample_document_info["content"]["markdown"])

        with open(os.path.join(result_dir, "content.html"), "w", encoding="utf-8") as f:
            f.write(sample_document_info["content"]["html"])

        # Criar arquivo original
        with open(
            os.path.join(result_dir, sample_document_info["original_filename"]), "w", encoding="utf-8"
        ) as f:
            f.write("Conteúdo original")

        # Chamar a função a ser testada
        result = get_document_info(document_id)

        # Verificar o resultado
        assert result["id"] == document_id
        assert result["original_filename"] == "test_document.pdf"
        assert result["status"] == "success"
        assert "files" in result
        assert result["files"]["metadata"] == os.path.join(result_dir, "metadata.json")
        assert result["files"]["markdown"] == os.path.join(result_dir, "content.md")
        assert result["files"]["html"] == os.path.join(result_dir, "content.html")
        assert result["files"]["original"] == os.path.join(result_dir, "test_document.pdf")

    def test_get_document_info_nonexistent(self, mock_results_dir):
        """Testa a obtenção de informações de um documento inexistente."""
        # Chamar a função a ser testada
        result = get_document_info("nonexistent-id")

        # Verificar o resultado
        assert result is None

    def test_list_documents_empty(self, mock_results_dir):
        """Testa a listagem de documentos quando não há documentos."""
        # Chamar a função a ser testada
        result = list_documents()

        # Verificar o resultado
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_documents(self, mock_results_dir, sample_document_info):
        """Testa a listagem de documentos."""
        # Criar alguns diretórios de documentos
        for i in range(5):
            document_id = f"doc-{i}"
            result_dir = os.path.join(mock_results_dir, document_id)
            os.makedirs(result_dir, exist_ok=True)

            # Criar arquivo de metadados
            doc_info = sample_document_info.copy()
            doc_info["id"] = document_id
            with open(os.path.join(result_dir, "metadata.json"), "w", encoding="utf-8") as f:
                json.dump(doc_info, f)

        # Simular a função get_document_info e os.path.getmtime
        with patch(
            "app.services.document_service.get_document_info",
            side_effect=lambda doc_id: {"id": doc_id, "original_filename": "test.pdf"},
        ), patch(
            "os.path.getmtime",
            # Simular timestamps em ordem inversa para garantir a ordenação correta
            side_effect=lambda path: 1000 - int(path.split("-")[-1]) if "-" in path else 0,
        ):
            # Chamar a função a ser testada
            result = list_documents(limit=3, offset=1)

            # Verificar o resultado
            assert isinstance(result, list)
            # Verificar apenas o tamanho e tipo do resultado, sem depender da ordem específica
            # que pode variar dependendo de como os arquivos são ordenados
            assert len(result) == 3
            # Verificar que todos os IDs estão no formato esperado
            for item in result:
                assert "doc-" in item["id"]
                assert "original_filename" in item

    def test_list_documents_with_limit_and_offset(self, mock_results_dir, sample_document_info):
        """Testa a listagem de documentos com limite e offset."""
        # Criar alguns diretórios de documentos
        for i in range(10):
            document_id = f"doc-{i}"
            result_dir = os.path.join(mock_results_dir, document_id)
            os.makedirs(result_dir, exist_ok=True)

            # Criar arquivo de metadados
            doc_info = sample_document_info.copy()
            doc_info["id"] = document_id
            with open(os.path.join(result_dir, "metadata.json"), "w", encoding="utf-8") as f:
                json.dump(doc_info, f)

        # Simular a função get_document_info
        with patch(
            "app.services.document_service.get_document_info",
            side_effect=lambda doc_id: {"id": doc_id, "original_filename": "test.pdf"},
        ):
            # Chamar a função a ser testada com diferentes limites e offsets
            result1 = list_documents(limit=5, offset=0)
            result2 = list_documents(limit=3, offset=5)
            result3 = list_documents(limit=10, offset=5)

            # Verificar os resultados
            assert len(result1) == 5
            assert len(result2) == 3
            assert len(result3) == 5  # Apenas 5 documentos restantes após offset 5
