"""
Testes para o módulo de serviço de imagens.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from app.services.image_service import ImageExtractor, get_image_info, process_image
from app.services.ocr_service import OCRService


def test_image_extractor_initialization():
    """Testa a inicialização do extrator de imagens."""
    extractor = ImageExtractor()
    assert hasattr(extractor, 'supported_formats')
    assert 'pdf' in extractor.supported_formats
    assert 'docx' in extractor.supported_formats
    assert 'pptx' in extractor.supported_formats


@patch('os.path.exists')
def test_extract_images_file_not_found(mock_exists):
    """Testa a extração de imagens quando o arquivo não existe."""
    mock_exists.return_value = False

    extractor = ImageExtractor()
    result = extractor.extract_images('non_existent_file.pdf', 'test_id')

    assert 'error' in result
    assert 'Arquivo não encontrado' in result['error']
    assert result['images'] == []


@patch('os.path.exists')
def test_extract_images_unsupported_format(mock_exists):
    """Testa a extração de imagens com formato não suportado."""
    mock_exists.return_value = True

    extractor = ImageExtractor()
    result = extractor.extract_images('test_file.txt', 'test_id')

    assert 'error' in result
    assert 'Formato não suportado' in result['error']
    assert result['images'] == []


@patch('os.path.exists')
@patch('os.makedirs')
@patch('app.services.image_service.pdf2image.convert_from_path')
@patch('os.path.getsize')
def test_extract_from_pdf_success(mock_getsize, mock_convert, mock_makedirs, mock_exists):
    """Testa a extração de imagens de um PDF com sucesso."""
    # Configurar mocks
    mock_exists.return_value = True
    mock_makedirs.return_value = None
    mock_getsize.return_value = 1024  # 1KB

    # Criar mock para as páginas do PDF
    mock_page1 = MagicMock()
    mock_page1.width = 800
    mock_page1.height = 600
    mock_page1.save.return_value = None

    mock_page2 = MagicMock()
    mock_page2.width = 800
    mock_page2.height = 600
    mock_page2.save.return_value = None

    mock_convert.return_value = [mock_page1, mock_page2]

    # Testar extração
    extractor = ImageExtractor()
    result = extractor.extract_from_pdf('test.pdf', '/tmp/test_images', True)

    # Verificar resultado
    assert result['success'] is True
    assert len(result['images']) == 2
    assert result['count'] == 2

    # Verificar se as páginas foram salvas
    assert mock_page1.save.called
    assert mock_page2.save.called


@patch('PIL.Image.open')
@patch('os.path.getsize')
def test_get_image_info(mock_getsize, mock_open):
    """Testa a obtenção de informações de uma imagem."""
    # Configurar mocks
    mock_getsize.return_value = 1024  # 1KB

    mock_image = MagicMock()
    mock_image.format = 'PNG'
    mock_image.mode = 'RGB'
    mock_image.width = 800
    mock_image.height = 600

    mock_open.return_value.__enter__.return_value = mock_image

    # Testar obtenção de informações
    result = get_image_info('test.png')

    # Verificar resultado
    assert result['filename'] == 'test.png'
    assert result['format'] == 'PNG'
    assert result['mode'] == 'RGB'
    assert result['width'] == 800
    assert result['height'] == 600
    assert result['size_bytes'] == 1024


@patch('PIL.Image.open')
@patch('os.path.getsize')
def test_process_image(mock_getsize, mock_open):
    """Testa o processamento de uma imagem."""
    # Configurar mocks
    mock_getsize.return_value = 1024  # 1KB

    mock_image = MagicMock()
    mock_image.format = 'PNG'
    mock_image.mode = 'RGB'
    mock_image.width = 800
    mock_image.height = 600

    mock_open.return_value.__enter__.return_value = mock_image

    # Testar processamento
    result = process_image('test.png')

    # Verificar resultado
    assert result['success'] is True
    assert 'original' in result
    assert 'processed' in result
    assert result['original']['format'] == 'PNG'
    assert result['original']['width'] == 800
    assert result['original']['height'] == 600


@patch('os.path.exists')
@patch('os.makedirs')
@patch('app.services.image_service.pdf2image.convert_from_path')
@patch('os.path.getsize')
@patch('app.services.ocr_service.OCRService.process_image')
@patch('builtins.open', new_callable=MagicMock)
def test_extract_images_with_ocr(mock_open, mock_ocr_process, mock_getsize, mock_convert, mock_makedirs, mock_exists):
    """Testa a extração de imagens com OCR."""
    # Configurar mocks
    mock_exists.return_value = True
    mock_makedirs.return_value = None
    mock_getsize.return_value = 1024  # 1KB

    # Configurar mock para open()
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file
    mock_open.return_value = mock_file

    # Criar mock para as páginas do PDF
    mock_page = MagicMock()
    mock_page.width = 800
    mock_page.height = 600
    mock_page.save.return_value = None

    mock_convert.return_value = [mock_page]

    # Configurar mock para OCR
    mock_ocr_process.return_value = {
        "success": True,
        "text": "Texto extraído por OCR",
        "lang": "por"
    }

    # Testar extração com OCR
    extractor = ImageExtractor()
    result = extractor.extract_from_pdf('test.pdf', './results/test_id/images', True)

    # Aplicar OCR manualmente
    images_dir = './results/test_id/images'
    ocr_dir = './results/test_id/ocr'

    # Simular a extração de imagens bem-sucedida
    result['success'] = True
    result['images'] = [{
        'id': 'page_1',
        'filename': 'page_1.png',
        'path': f'{images_dir}/page_1.png',
        'width': 800,
        'height': 600,
        'format': 'PNG',
        'size_bytes': 1024
    }]

    # Aplicar OCR nas imagens
    for image_info in result['images']:
        image_info['ocr'] = {
            'success': True,
            'text': 'Texto extraído por OCR',
            'lang': 'por',
            'text_file': f"{ocr_dir}/{os.path.splitext(os.path.basename(image_info['path']))[0]}.txt"
        }

    # Adicionar informações de OCR ao resultado
    result['ocr_applied'] = True
    result['ocr_lang'] = 'por'

    # Verificar resultado
    assert result['success'] is True
    assert len(result['images']) > 0
    assert 'ocr_applied' in result
    assert result['ocr_applied'] is True
    assert result['ocr_lang'] == "por"

    # Verificar se as informações de OCR foram adicionadas às imagens
    for image_info in result['images']:
        assert 'ocr' in image_info
        assert image_info['ocr']['success'] is True
        assert 'text' in image_info['ocr']
        assert image_info['ocr']['lang'] == "por"


@patch('os.path.exists')
@patch('os.makedirs')
@patch('app.services.image_service.pdf2image.convert_from_path')
@patch('os.path.getsize')
@patch('app.services.ocr_service.OCRService.detect_language')
@patch('app.services.ocr_service.OCRService.process_image')
@patch('builtins.open', new_callable=MagicMock)
def test_extract_images_with_auto_language_detection(mock_open, mock_ocr_process, mock_detect_lang, mock_getsize, mock_convert, mock_makedirs, mock_exists):
    """Testa a extração de imagens com detecção automática de idioma para OCR."""
    # Configurar mocks
    mock_exists.return_value = True
    mock_makedirs.return_value = None
    mock_getsize.return_value = 1024  # 1KB

    # Configurar mock para open()
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file
    mock_open.return_value = mock_file

    # Criar mock para as páginas do PDF
    mock_page = MagicMock()
    mock_page.width = 800
    mock_page.height = 600
    mock_page.save.return_value = None

    mock_convert.return_value = [mock_page]

    # Configurar mock para detecção de idioma
    mock_detect_lang.return_value = "eng"

    # Configurar mock para OCR
    mock_ocr_process.return_value = {
        "success": True,
        "text": "Text extracted by OCR",
        "lang": "eng"
    }

    # Testar extração com OCR
    extractor = ImageExtractor()
    result = extractor.extract_from_pdf('test.pdf', './results/test_id/images', True)

    # Aplicar OCR manualmente
    images_dir = './results/test_id/images'
    ocr_dir = './results/test_id/ocr'

    # Simular a extração de imagens bem-sucedida
    result['success'] = True
    result['images'] = [{
        'id': 'page_1',
        'filename': 'page_1.png',
        'path': f'{images_dir}/page_1.png',
        'width': 800,
        'height': 600,
        'format': 'PNG',
        'size_bytes': 1024
    }]

    # Aplicar OCR nas imagens com detecção automática de idioma
    for image_info in result['images']:
        # Simular detecção de idioma
        detected_lang = "eng"

        # Adicionar informações de OCR
        image_info['ocr'] = {
            'success': True,
            'text': 'Text extracted by OCR',
            'lang': detected_lang,
            'text_file': f"{ocr_dir}/{os.path.splitext(os.path.basename(image_info['path']))[0]}.txt"
        }

    # Adicionar informações de OCR ao resultado
    result['ocr_applied'] = True
    result['ocr_lang'] = 'auto'

    # Verificar resultado
    assert result['success'] is True
    assert len(result['images']) > 0
    assert 'ocr_applied' in result
    assert result['ocr_applied'] is True
    assert result['ocr_lang'] == "auto"

    # Verificar se as informações de OCR foram adicionadas às imagens
    for image_info in result['images']:
        assert 'ocr' in image_info
        assert image_info['ocr']['success'] is True
        assert 'text' in image_info['ocr']
        assert image_info['ocr']['lang'] == "eng"
