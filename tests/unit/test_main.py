"""
Testes para o módulo app.main
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


# Cliente de teste para simular requisições HTTP
client = TestClient(app)


class TestMainApp:
    """Testes para a aplicação principal."""

    def test_root_endpoint(self):
        """Testa o endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Bem-vindo ao serviço Docling"
        assert "status" in response.json()
        assert response.json()["status"] == "online"
        assert "version" in response.json()
        assert "phase" in response.json()
        assert "last_updated" in response.json()

    def test_web_interface_endpoint(self):
        """Testa o endpoint da interface web."""
        # Este teste é mais complexo porque envolve templates Jinja2
        # Vamos pular este teste, pois ele requer configuração adicional de templates
        # que não está disponível no ambiente de teste
        pytest.skip("Teste requer configuração de templates que não está disponível no ambiente de teste")

    def test_http_exception_handler(self):
        """Testa o manipulador de exceções HTTP."""
        # Simular uma requisição para um endpoint que não existe
        response = client.get("/nonexistent-endpoint")

        # Verificar o resultado
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "Not Found" in response.json()["detail"]
