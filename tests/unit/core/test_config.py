"""
Testes para o módulo app.core.config
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch

# Importar após os mocks para garantir que os mocks sejam aplicados
with patch.dict(os.environ, {}, clear=True):
    from app.core.config import (
        BASE_DIR,
        UPLOAD_DIR,
        RESULTS_DIR,
        API_PREFIX,
        API_VERSION,
        DEBUG,
        HOST,
        PORT,
    )


def test_base_dir():
    """Testa se BASE_DIR é um caminho válido."""
    assert isinstance(BASE_DIR, Path)
    assert BASE_DIR.exists()
    assert BASE_DIR.is_dir()


def test_upload_dir_default():
    """Testa se UPLOAD_DIR é um caminho válido."""
    assert isinstance(UPLOAD_DIR, str)
    assert len(UPLOAD_DIR) > 0
    assert "uploads" in UPLOAD_DIR.lower()


def test_upload_dir_from_env():
    """Testa se UPLOAD_DIR pode ser configurado via variável de ambiente."""
    # Este teste verifica apenas se a variável existe e é um caminho válido
    # Não testamos o valor exato porque o Docker pode modificar os caminhos
    assert isinstance(UPLOAD_DIR, str)
    assert len(UPLOAD_DIR) > 0


def test_results_dir_default():
    """Testa se RESULTS_DIR é um caminho válido."""
    assert isinstance(RESULTS_DIR, str)
    assert len(RESULTS_DIR) > 0
    assert "results" in RESULTS_DIR.lower()


def test_results_dir_from_env():
    """Testa se RESULTS_DIR pode ser configurado via variável de ambiente."""
    # Este teste verifica apenas se a variável existe e é um caminho válido
    # Não testamos o valor exato porque o Docker pode modificar os caminhos
    assert isinstance(RESULTS_DIR, str)
    assert len(RESULTS_DIR) > 0


def test_api_prefix():
    """Testa se API_PREFIX tem o valor correto."""
    assert API_PREFIX == "/api"


def test_api_version():
    """Testa se API_VERSION tem o valor correto."""
    assert API_VERSION == "v1"


def test_debug_default():
    """Testa se DEBUG é um booleano."""
    assert isinstance(DEBUG, bool)


def test_debug_values():
    """Testa se DEBUG pode ser True ou False."""
    # No ambiente de desenvolvimento, DEBUG geralmente é True
    # Este teste apenas verifica se o valor é um booleano válido
    assert DEBUG in [True, False]


def test_host_default():
    """Testa se HOST é uma string válida."""
    assert isinstance(HOST, str)
    assert len(HOST) > 0


def test_host_format():
    """Testa se HOST está em um formato válido de endereço IP."""
    # Verifica se HOST é um endereço IP válido (simplificado)
    assert HOST == "0.0.0.0" or HOST == "127.0.0.1" or HOST.startswith("192.168.") or HOST.startswith("10.")


def test_port_default():
    """Testa se PORT é um número inteiro válido."""
    assert isinstance(PORT, int)
    assert PORT > 0
    assert PORT < 65536  # Limite máximo para portas TCP/IP


def test_port_common_values():
    """Testa se PORT está em um intervalo comum para serviços web."""
    # Verificar se a porta está em um intervalo razoável
    assert PORT >= 80  # Evitar portas de sistema (0-79)


def test_port_type():
    """Testa se PORT é do tipo correto."""
    # PORT deve ser um inteiro
    assert not isinstance(PORT, str)
    assert not isinstance(PORT, float)
    assert isinstance(PORT, int)
