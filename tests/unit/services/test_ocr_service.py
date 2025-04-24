"""
Testes para o serviço de OCR.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
import io

from app.services.ocr_service import OCRService


@pytest.fixture
def ocr_service():
    """Fixture para criar uma instância do serviço de OCR."""
    with patch('app.services.ocr_service.pytesseract') as mock_pytesseract:
        # Configurar o mock para retornar idiomas suportados
        mock_pytesseract.get_languages.return_value = ["por", "eng", "spa", "fra"]
        
        # Criar o serviço
        service = OCRService()
        
        # Configurar o mock para retornar texto de exemplo
        mock_pytesseract.image_to_string.return_value = "Texto de exemplo para OCR"
        mock_pytesseract.image_to_data.return_value = {"text": ["Texto", "de", "exemplo"]}
        mock_pytesseract.image_to_pdf_or_hocr.return_value = b"<html><body>Texto de exemplo</body></html>"
        mock_pytesseract.image_to_osd.return_value = "Script: Latin\nScript confidence: 1.0"
        
        yield service


@pytest.fixture
def sample_image():
    """Fixture para criar uma imagem de teste."""
    # Criar uma imagem em memória para testes
    img = Image.new('RGB', (100, 30), color=(255, 255, 255))
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Salvar a imagem em um arquivo temporário
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    img_path = os.path.join(temp_dir, "test_image.png")
    
    with open(img_path, 'wb') as f:
        f.write(img_io.getvalue())
    
    yield img_path
    
    # Limpar após o teste
    if os.path.exists(img_path):
        os.remove(img_path)
    
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


def test_ocr_service_initialization(ocr_service):
    """Testa a inicialização do serviço de OCR."""
    assert ocr_service is not None
    assert len(ocr_service.supported_languages) > 0
    assert "por" in ocr_service.supported_languages
    assert "eng" in ocr_service.supported_languages


def test_process_image_text(ocr_service, sample_image):
    """Testa o processamento de OCR em uma imagem para extrair texto."""
    result = ocr_service.process_image(sample_image, lang="por", output_type="text")
    
    assert result["success"] is True
    assert "text" in result
    assert result["text"] == "Texto de exemplo para OCR"
    assert result["lang"] == "por"


def test_process_image_data(ocr_service, sample_image):
    """Testa o processamento de OCR em uma imagem para extrair dados estruturados."""
    result = ocr_service.process_image(sample_image, lang="por", output_type="data")
    
    assert result["success"] is True
    assert "data" in result
    assert "text" in result["data"]
    assert result["lang"] == "por"


def test_process_image_hocr(ocr_service, sample_image):
    """Testa o processamento de OCR em uma imagem para extrair HOCR."""
    result = ocr_service.process_image(sample_image, lang="por", output_type="hocr")
    
    assert result["success"] is True
    assert "hocr" in result
    assert isinstance(result["hocr"], bytes)
    assert result["lang"] == "por"


def test_process_image_invalid_path(ocr_service):
    """Testa o processamento de OCR com um caminho de arquivo inválido."""
    result = ocr_service.process_image("/caminho/inexistente.png")
    
    assert result["success"] is False
    assert "error" in result
    assert "Arquivo não encontrado" in result["error"]


def test_process_image_invalid_language(ocr_service, sample_image):
    """Testa o processamento de OCR com um idioma inválido."""
    # Configurar o mock para retornar apenas alguns idiomas
    ocr_service.supported_languages = ["por", "eng"]
    
    # Tentar processar com um idioma não suportado
    result = ocr_service.process_image(sample_image, lang="xyz")
    
    # Deve usar o idioma padrão (por) como fallback
    assert result["success"] is True
    assert result["lang"] == "por"


def test_detect_language(ocr_service, sample_image):
    """Testa a detecção automática de idioma."""
    lang = ocr_service.detect_language(sample_image)
    
    # Como estamos usando um mock que retorna "Latin", deve mapear para "por"
    assert lang == "por"


def test_process_pdf_images(ocr_service, sample_image):
    """Testa o processamento de OCR em um diretório de imagens."""
    # Criar um diretório temporário com uma imagem
    temp_dir = os.path.dirname(sample_image)
    
    # Processar o diretório
    result = ocr_service.process_pdf_images(temp_dir)
    
    assert result["success"] is True
    assert "pages" in result
    assert len(result["pages"]) == 1
    assert result["pages"][0]["success"] is True
    assert "text" in result["pages"][0]
    assert "full_text" in result
    assert result["full_text"] != ""


def test_process_pdf_images_invalid_dir(ocr_service):
    """Testa o processamento de OCR com um diretório inválido."""
    result = ocr_service.process_pdf_images("/diretorio/inexistente")
    
    assert result["success"] is False
    assert "error" in result
    assert "Diretório não encontrado" in result["error"]


def test_preprocess_image(ocr_service):
    """Testa o pré-processamento de imagem."""
    # Criar uma imagem colorida
    img = Image.new('RGB', (100, 30), color=(255, 0, 0))
    
    # Pré-processar a imagem
    processed_img = ocr_service._preprocess_image(img)
    
    # Verificar se a imagem foi convertida para escala de cinza
    assert processed_img.mode == 'L'
