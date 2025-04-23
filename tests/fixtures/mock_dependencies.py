"""
Mocks para dependências externas usadas nos testes.
"""
import os
import io
import json
from unittest.mock import MagicMock, patch
import pytest


class MockDocument:
    """Mock para a classe Document do python-docx."""

    def __init__(self, paragraphs=None, tables=None):
        self.paragraphs = paragraphs or []
        self.tables = tables or []


class MockParagraph:
    """Mock para a classe Paragraph do python-docx."""

    def __init__(self, text="", style=None):
        self.text = text
        self.style = style or MockStyle()


class MockStyle:
    """Mock para a classe Style do python-docx."""

    def __init__(self, name="Normal"):
        self.name = name


class MockTable:
    """Mock para a classe Table do python-docx."""

    def __init__(self, rows=None, cols=None):
        self.rows = rows or []
        self._grid = [[MagicMock() for _ in range(cols or 0)] for _ in range(rows or 0)]


class MockPdfReader:
    """Mock para a classe PdfReader do PyPDF2."""

    def __init__(self, pages=None, metadata=None):
        self.pages = pages or []
        self.metadata = metadata or {}


class MockPdfPage:
    """Mock para a classe Page do PyPDF2."""

    def __init__(self, text=""):
        self._text = text

    def extract_text(self):
        """Simula a extração de texto de uma página PDF."""
        return self._text


class MockDataFrame:
    """Mock para a classe DataFrame do pandas."""

    def __init__(self, data=None):
        self.data = data or {}

    def to_string(self, index=True):
        """Simula a conversão do DataFrame para string."""
        return "MockDataFrame content"

    def to_dict(self, orient="records"):
        """Simula a conversão do DataFrame para dicionário."""
        return self.data


class MockWorkbook:
    """Mock para a classe Workbook do openpyxl."""

    def __init__(self, sheet_names=None):
        self.sheet_names = sheet_names or ["Sheet1"]
        self.active = MockWorksheet()
        self._sheets = {name: MockWorksheet(name) for name in self.sheet_names}

    def get_sheet_by_name(self, name):
        """Simula a obtenção de uma planilha pelo nome."""
        return self._sheets.get(name, MockWorksheet())


class MockWorksheet:
    """Mock para a classe Worksheet do openpyxl."""

    def __init__(self, name="Sheet1"):
        self.name = name
        self.title = name
        self._cells = {}

    def cell(self, row, column):
        """Simula a obtenção de uma célula."""
        key = (row, column)
        if key not in self._cells:
            self._cells[key] = MockCell(f"Cell {row},{column}")
        return self._cells[key]


class MockCell:
    """Mock para a classe Cell do openpyxl."""

    def __init__(self, value=None):
        self.value = value


@pytest.fixture
def mock_docx():
    """Fixture para simular a biblioteca python-docx."""
    with patch("docx.Document") as mock:
        # Configurar o mock para retornar um documento com parágrafos e tabelas
        doc = MockDocument(
            paragraphs=[
                MockParagraph("Título do Documento", MockStyle("Heading1")),
                MockParagraph("Este é um parágrafo de exemplo."),
                MockParagraph("Este é outro parágrafo."),
            ],
            tables=[MockTable(rows=2, cols=2)],
        )
        mock.return_value = doc
        yield mock


@pytest.fixture
def mock_pdf():
    """Fixture para simular a biblioteca PyPDF2."""
    with patch("PyPDF2.PdfReader") as mock:
        # Configurar o mock para retornar um leitor de PDF com páginas e metadados
        reader = MockPdfReader(
            pages=[
                MockPdfPage("Página 1 do PDF"),
                MockPdfPage("Página 2 do PDF"),
            ],
            metadata={
                "/Title": "Documento de Teste",
                "/Author": "Teste",
                "/CreationDate": "D:20250415120000",
            },
        )
        mock.return_value = reader
        yield mock


@pytest.fixture
def mock_pandas():
    """Fixture para simular a biblioteca pandas."""
    with patch("pandas.read_excel") as mock:
        # Configurar o mock para retornar um DataFrame
        df = MockDataFrame(
            data=[
                {"Coluna1": "Valor1", "Coluna2": "Valor2"},
                {"Coluna1": "Valor3", "Coluna2": "Valor4"},
            ]
        )
        mock.return_value = df
        yield mock


@pytest.fixture
def mock_openpyxl():
    """Fixture para simular a biblioteca openpyxl."""
    with patch("openpyxl.load_workbook") as mock:
        # Configurar o mock para retornar um workbook
        wb = MockWorkbook(sheet_names=["Planilha1", "Planilha2"])
        mock.return_value = wb
        yield mock


@pytest.fixture
def mock_markdown():
    """Fixture para simular a biblioteca markdown."""
    with patch("markdown.markdown") as mock:
        # Configurar o mock para retornar HTML
        mock.return_value = "<h1>Título</h1><p>Parágrafo</p>"
        yield mock


@pytest.fixture
def mock_file():
    """Fixture para criar um arquivo temporário para testes."""
    content = "Conteúdo de teste para o arquivo"
    file_obj = io.BytesIO(content.encode("utf-8"))
    file_obj.name = "test_file.txt"
    yield file_obj


@pytest.fixture
def mock_docx_file():
    """Fixture para simular um arquivo DOCX."""
    file_path = "/tmp/test_document.docx"
    yield file_path


@pytest.fixture
def mock_pdf_file():
    """Fixture para simular um arquivo PDF."""
    file_path = "/tmp/test_document.pdf"
    yield file_path


@pytest.fixture
def mock_excel_file():
    """Fixture para simular um arquivo Excel."""
    file_path = "/tmp/test_document.xlsx"
    yield file_path
