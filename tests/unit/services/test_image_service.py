"""
Testes para o módulo de serviço de imagens.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from app.services.image_service import ImageExtractor, get_image_info, process_image


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
