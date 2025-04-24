"""
Testes de integração para a API.
"""

import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app


class TestAPIIntegration(unittest.TestCase):
    """Testes de integração para a API."""

    def setUp(self):
        """Configuração para os testes."""
        self.client = TestClient(app)
        
        # Caminho para o arquivo de teste
        self.test_pdf = os.path.join(os.path.dirname(__file__), "data", "test_document.pdf")
        
        # Verificar se o arquivo de teste existe
        if not os.path.exists(self.test_pdf):
            # Criar diretório de dados se não existir
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(data_dir, exist_ok=True)
            
            # Copiar arquivo de teste do diretório raiz
            root_test_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_document.pdf")
            if os.path.exists(root_test_pdf):
                shutil.copy2(root_test_pdf, self.test_pdf)
            else:
                self.skipTest("Arquivo de teste não encontrado")

    def test_process_document_with_images(self):
        """Testa o processamento de um documento com extração de imagens."""
        # Verificar se o arquivo de teste existe
        if not os.path.exists(self.test_pdf):
            self.skipTest("Arquivo de teste não encontrado")
            
        # Abrir o arquivo para envio
        with open(self.test_pdf, "rb") as f:
            # Enviar requisição
            response = self.client.post(
                "/docling/api/process",
                files={"file": ("test_document.pdf", f, "application/pdf")},
                data={
                    "extract_text": "true",
                    "extract_tables": "true",
                    "extract_images": "true",
                    "extract_pages_as_images": "true"
                }
            )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar campos básicos
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["message"], "Documento processado com sucesso")
        self.assertEqual(data["file_type"], "pdf")
        
        # Verificar conteúdo
        self.assertIn("content", data)
        self.assertIn("text", data["content"])
        self.assertIn("markdown", data["content"])
        self.assertIn("html", data["content"])
        
        # Verificar imagens
        self.assertIn("images", data["content"])
        self.assertGreater(len(data["content"]["images"]), 0)
        
        # Verificar metadados da primeira imagem
        image = data["content"]["images"][0]
        self.assertEqual(image["type"], "page")
        self.assertGreater(image["width"], 0)
        self.assertGreater(image["height"], 0)
        self.assertGreater(image["size_bytes"], 0)
        
        # Verificar se o arquivo de imagem existe
        self.assertTrue(os.path.exists(image["path"]))

    def test_process_document_without_images(self):
        """Testa o processamento de um documento sem extração de imagens."""
        # Verificar se o arquivo de teste existe
        if not os.path.exists(self.test_pdf):
            self.skipTest("Arquivo de teste não encontrado")
            
        # Abrir o arquivo para envio
        with open(self.test_pdf, "rb") as f:
            # Enviar requisição
            response = self.client.post(
                "/docling/api/process",
                files={"file": ("test_document.pdf", f, "application/pdf")},
                data={
                    "extract_text": "true",
                    "extract_tables": "true",
                    "extract_images": "false",
                    "extract_pages_as_images": "false"
                }
            )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar campos básicos
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["message"], "Documento processado com sucesso")
        
        # Verificar conteúdo
        self.assertIn("content", data)
        self.assertIn("text", data["content"])
        
        # Verificar que não há imagens
        self.assertNotIn("images", data["content"])


if __name__ == "__main__":
    unittest.main()
