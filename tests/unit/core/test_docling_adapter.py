"""
Testes para o módulo app.core.docling_adapter
"""
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from app.core.docling_adapter import DoclingAdapter
from tests.fixtures.mock_dependencies import (
    mock_docx,
    mock_pdf,
    mock_pandas,
    mock_openpyxl,
    mock_markdown,
    mock_docx_file,
    mock_pdf_file,
    mock_excel_file,
)


class TestDoclingAdapter:
    """Testes para a classe DoclingAdapter."""

    def setup_method(self):
        """Configuração executada antes de cada teste."""
        self.adapter = DoclingAdapter()

    def test_init(self):
        """Testa se o adaptador é inicializado corretamente."""
        assert isinstance(self.adapter, DoclingAdapter)

    @pytest.mark.parametrize(
        "file_extension,expected_status",
        [
            (".pdf", "success"),
            (".docx", "success"),
            (".xlsx", "success"),
            (".xls", "success"),
            (".txt", "error"),  # Formato não suportado
            (".jpg", "error"),  # Formato não suportado
        ],
    )
    def test_process_document_file_types(self, file_extension, expected_status, tmp_path):
        """Testa se o adaptador processa diferentes tipos de arquivo corretamente."""
        # Criar um arquivo temporário com a extensão especificada
        file_path = tmp_path / f"test_document{file_extension}"
        file_path.write_text("Conteúdo de teste")

        # Aplicar mocks para evitar acesso real às bibliotecas
        with patch("docx.Document"), patch("PyPDF2.PdfReader"), patch("pandas.read_excel"), patch(
            "pandas.ExcelFile"
        ), patch("markdown.markdown"):
            # Chamar o método a ser testado
            result = self.adapter.process_document(file_path)

            # Verificar o resultado
            assert result["status"] == expected_status
            if expected_status == "success":
                assert "content" in result
            else:
                assert "Formato de arquivo não suportado" in result["message"]

    def test_process_document_exception(self, tmp_path):
        """Testa se o adaptador lida corretamente com exceções durante o processamento."""
        # Criar um arquivo temporário
        file_path = tmp_path / "test_document.pdf"
        file_path.write_text("Conteúdo de teste")

        # Simular uma exceção durante o processamento
        with patch("PyPDF2.PdfReader", side_effect=Exception("Erro simulado")):
            # Chamar o método a ser testado
            result = self.adapter.process_document(file_path)

            # Verificar o resultado
            assert result["status"] == "error"
            assert "Erro ao processar documento" in result["message"]
            assert result["content"] is None

    def test_process_pdf(self, mock_pdf):
        """Testa o processamento de arquivos PDF."""
        # Configurar o mock para simular um PDF com conteúdo
        result = {"status": "success", "content": {}}

        # Criar um arquivo temporário em memória
        with patch("builtins.open", mock_open(read_data=b"PDF content")):
            # Chamar o método a ser testado com um caminho fictício
            with patch("PyPDF2.PdfReader") as mock_reader:
                # Configurar o mock para retornar páginas e metadados
                mock_instance = MagicMock()
                mock_instance.pages = [MagicMock(), MagicMock()]
                mock_instance.pages[0].extract_text.return_value = "Página 1"
                mock_instance.pages[1].extract_text.return_value = "Página 2"
                mock_instance.metadata = MagicMock(title="Título do PDF")
                mock_reader.return_value = mock_instance

                self.adapter._process_pdf("test.pdf", result, True, True, False)

        # Verificar o resultado
        assert "text" in result["content"]
        assert "markdown" in result["content"]
        assert "html" in result["content"]
        assert "metadata" in result
        assert "pages" in result["metadata"]
        assert "title" in result["metadata"]

    def test_process_docx(self):
        """Testa o processamento de arquivos DOCX."""
        # Configurar o resultado inicial
        result = {"status": "success", "content": {}}

        # Chamar o método a ser testado com mocks
        with patch("docx.Document") as mock_document:
            # Configurar o mock para retornar um documento com parágrafos e tabelas
            mock_doc = MagicMock()

            # Simular parágrafos
            mock_paragraph1 = MagicMock()
            mock_paragraph1.text = "Título do Documento"
            mock_paragraph1.style.name = "Heading1"

            mock_paragraph2 = MagicMock()
            mock_paragraph2.text = "Este é um parágrafo de exemplo."
            mock_paragraph2.style.name = "Normal"

            mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]

            # Simular tabelas
            mock_table = MagicMock()
            mock_row = MagicMock()
            mock_cell = MagicMock()
            mock_cell.text = "Conteúdo da célula"
            mock_row.cells = [mock_cell]
            mock_table.rows = [mock_row]
            mock_doc.tables = [mock_table]

            # Simular propriedades do documento
            mock_doc.core_properties = MagicMock()
            mock_doc.core_properties.title = "Título do Documento"

            mock_document.return_value = mock_doc

            # Patch para markdown
            with patch("markdown.markdown", return_value="<h1>Título do Documento</h1>"):
                self.adapter._process_docx("test.docx", result, True, True, False)

        # Verificar o resultado
        assert "text" in result["content"]
        assert "markdown" in result["content"]
        assert "html" in result["content"]
        assert "metadata" in result
        assert "title" in result["metadata"]
        assert "pages" in result["metadata"]

    def test_process_excel(self):
        """Testa o processamento de arquivos Excel."""
        # Configurar o resultado inicial
        result = {"status": "success", "content": {}}

        # Chamar o método a ser testado
        with patch("pandas.ExcelFile") as mock_excel_file_class:
            # Configurar o mock para retornar nomes de planilhas
            mock_excel_file_instance = MagicMock()
            mock_excel_file_instance.sheet_names = ["Sheet1", "Sheet2"]
            mock_excel_file_class.return_value = mock_excel_file_instance

            # Mock para pandas.read_excel
            with patch("pandas.read_excel") as mock_read_excel:
                # Criar um DataFrame simulado
                mock_df = MagicMock()
                mock_df.values = MagicMock()
                mock_df.values.tolist.return_value = [["Valor1", "Valor2"], ["Valor3", "Valor4"]]
                mock_df.columns = MagicMock()
                mock_df.columns.tolist.return_value = ["Coluna1", "Coluna2"]
                mock_df.to_string.return_value = "Coluna1 Coluna2\nValor1  Valor2\nValor3  Valor4"

                mock_read_excel.return_value = mock_df

                self.adapter._process_excel("test.xlsx", result, True, True)

        # Verificar o resultado
        assert "text" in result["content"]
        assert "markdown" in result["content"]
        assert "html" in result["content"]
        assert "tables" in result["content"]
        assert "metadata" in result
        assert "title" in result["metadata"]
        assert "sheets" in result["metadata"]

    def test_get_document_metadata_pdf(self):
        """Testa a extração de metadados de arquivos PDF."""
        # Chamar o método a ser testado com mocks
        with patch("builtins.open", mock_open(read_data=b"PDF content")):
            with patch("PyPDF2.PdfReader") as mock_reader:
                # Configurar o mock para retornar páginas e metadados
                mock_instance = MagicMock()
                mock_instance.pages = [MagicMock(), MagicMock()]
                mock_instance.metadata = MagicMock(title="Título do PDF")
                mock_reader.return_value = mock_instance

                metadata = self.adapter.get_document_metadata("test.pdf")

        # Verificar o resultado
        assert "title" in metadata
        assert "format" in metadata
        assert metadata["format"] == "pdf"
        assert "pages" in metadata

    def test_get_document_metadata_docx(self):
        """Testa a extração de metadados de arquivos DOCX."""
        # Chamar o método a ser testado com mocks
        with patch("docx.Document") as mock_document:
            # Configurar o mock para retornar um documento com propriedades
            mock_doc = MagicMock()
            mock_doc.core_properties = MagicMock()
            mock_doc.core_properties.title = "Título do Documento DOCX"
            mock_document.return_value = mock_doc

            metadata = self.adapter.get_document_metadata("test.docx")

        # Verificar o resultado
        assert "title" in metadata
        assert "format" in metadata
        assert metadata["format"] == "docx"

    def test_get_document_metadata_excel(self):
        """Testa a extração de metadados de arquivos Excel."""
        # Chamar o método a ser testado
        with patch("pandas.ExcelFile") as mock_excel_file_class:
            # Configurar o mock para retornar nomes de planilhas
            mock_excel_file_instance = MagicMock()
            mock_excel_file_instance.sheet_names = ["Sheet1", "Sheet2"]
            mock_excel_file_class.return_value = mock_excel_file_instance

            metadata = self.adapter.get_document_metadata("test.xlsx")

        # Verificar o resultado
        assert "title" in metadata
        assert "format" in metadata
        assert metadata["format"] == "xlsx"
        assert "sheets" in metadata
        assert len(metadata["sheets"]) == 2

    def test_get_document_metadata_exception(self, tmp_path):
        """Testa se o adaptador lida corretamente com exceções durante a extração de metadados."""
        # Criar um arquivo temporário
        file_path = tmp_path / "test_document.pdf"
        file_path.write_text("Conteúdo de teste")

        # Simular uma exceção durante o processamento
        with patch("PyPDF2.PdfReader", side_effect=Exception("Erro simulado")):
            # Chamar o método a ser testado
            result = self.adapter.get_document_metadata(file_path)

            # Verificar o resultado
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro ao extrair metadados" in result["message"]

    def test_convert_to_format_markdown(self, tmp_path):
        """Testa a conversão para markdown."""
        # Criar um arquivo temporário
        file_path = tmp_path / "test_document.pdf"
        file_path.write_text("Conteúdo de teste")

        # Simular o processamento do documento
        with patch.object(
            self.adapter,
            "process_document",
            return_value={
                "status": "success",
                "content": {"markdown": "# Título\n\nConteúdo de teste"},
            },
        ):
            # Chamar o método a ser testado
            result = self.adapter.convert_to_format(file_path, "markdown")

            # Verificar o resultado
            assert result == "# Título\n\nConteúdo de teste"

    def test_convert_to_format_html(self, tmp_path):
        """Testa a conversão para HTML."""
        # Criar um arquivo temporário
        file_path = tmp_path / "test_document.pdf"
        file_path.write_text("Conteúdo de teste")

        # Simular o processamento do documento
        with patch.object(
            self.adapter,
            "process_document",
            return_value={
                "status": "success",
                "content": {"html": "<h1>Título</h1><p>Conteúdo de teste</p>"},
            },
        ):
            # Chamar o método a ser testado
            result = self.adapter.convert_to_format(file_path, "html")

            # Verificar o resultado
            assert result == "<h1>Título</h1><p>Conteúdo de teste</p>"

    def test_convert_to_format_text(self, tmp_path):
        """Testa a conversão para texto."""
        # Criar um arquivo temporário
        file_path = tmp_path / "test_document.pdf"
        file_path.write_text("Conteúdo de teste")

        # Simular o processamento do documento
        with patch.object(
            self.adapter,
            "process_document",
            return_value={"status": "success", "content": {"text": "Conteúdo de teste"}},
        ):
            # Chamar o método a ser testado
            result = self.adapter.convert_to_format(file_path, "text")

            # Verificar o resultado
            assert result == "Conteúdo de teste"

    def test_convert_to_format_unsupported(self, tmp_path):
        """Testa a conversão para um formato não suportado."""
        # Criar um arquivo temporário
        file_path = tmp_path / "test_document.pdf"
        file_path.write_text("Conteúdo de teste")

        # Simular o processamento do documento
        with patch.object(
            self.adapter,
            "process_document",
            return_value={"status": "success", "content": {"text": "Conteúdo de teste"}},
        ):
            # Chamar o método a ser testado
            result = self.adapter.convert_to_format(file_path, "json")

            # Verificar o resultado
            assert result is None

    def test_convert_to_format_error(self, tmp_path):
        """Testa a conversão quando o processamento do documento falha."""
        # Criar um arquivo temporário
        file_path = tmp_path / "test_document.pdf"
        file_path.write_text("Conteúdo de teste")

        # Simular o processamento do documento com erro
        with patch.object(
            self.adapter,
            "process_document",
            return_value={"status": "error", "message": "Erro simulado"},
        ):
            # Chamar o método a ser testado
            result = self.adapter.convert_to_format(file_path, "markdown")

            # Verificar o resultado
            assert result is None
