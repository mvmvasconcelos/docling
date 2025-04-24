"""
Testes para o módulo de extração de imagens.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from app.services.image_service import ImageExtractor


class TestImageExtractor(unittest.TestCase):
    """Testes para a classe ImageExtractor."""

    def setUp(self):
        """Configuração para os testes."""
        # Criar diretório temporário para os testes
        self.test_dir = tempfile.mkdtemp()
        self.extractor = ImageExtractor()
        
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

    def tearDown(self):
        """Limpeza após os testes."""
        # Remover diretório temporário
        shutil.rmtree(self.test_dir)

    def test_extract_from_pdf_pages(self):
        """Testa a extração de páginas como imagens de um PDF."""
        # Verificar se o arquivo de teste existe
        if not os.path.exists(self.test_pdf):
            self.skipTest("Arquivo de teste não encontrado")
            
        # Extrair imagens
        result = self.extractor.extract_from_pdf(
            file_path=self.test_pdf,
            images_dir=self.test_dir,
            extract_pages=True
        )
        
        # Verificar resultado
        self.assertTrue(result["success"])
        self.assertGreater(len(result["images"]), 0)
        
        # Verificar se as imagens foram salvas
        for image_info in result["images"]:
            self.assertTrue(os.path.exists(image_info["path"]))
            self.assertEqual(image_info["type"], "page")
            self.assertGreater(image_info["width"], 0)
            self.assertGreater(image_info["height"], 0)
            self.assertGreater(image_info["size_bytes"], 0)

    def test_extract_from_pdf_no_pages(self):
        """Testa a extração de imagens de um PDF sem converter páginas."""
        # Verificar se o arquivo de teste existe
        if not os.path.exists(self.test_pdf):
            self.skipTest("Arquivo de teste não encontrado")
            
        # Extrair imagens
        result = self.extractor.extract_from_pdf(
            file_path=self.test_pdf,
            images_dir=self.test_dir,
            extract_pages=False
        )
        
        # Verificar resultado
        self.assertTrue(result["success"])
        
        # Nota: Como não estamos extraindo páginas como imagens e o PDF de teste
        # pode não ter imagens incorporadas, o resultado pode estar vazio
        # Isso não é um erro, apenas uma característica do arquivo de teste

    def test_extract_from_nonexistent_file(self):
        """Testa a extração de imagens de um arquivo que não existe."""
        # Extrair imagens
        result = self.extractor.extract_from_pdf(
            file_path="arquivo_inexistente.pdf",
            images_dir=self.test_dir,
            extract_pages=True
        )
        
        # Verificar resultado
        self.assertFalse(result["success"])
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
