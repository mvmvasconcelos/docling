"""
Módulo para reconhecimento óptico de caracteres (OCR) em imagens.

Este módulo fornece funcionalidades para extrair texto de imagens usando
o Tesseract OCR, permitindo processar imagens individuais ou PDFs escaneados.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import tempfile

import pytesseract
from PIL import Image

from app.core.config import RESULTS_DIR

# Configurar logger
logger = logging.getLogger(__name__)

class OCRService:
    """
    Serviço para reconhecimento óptico de caracteres (OCR) em imagens.
    """

    def __init__(self):
        """
        Inicializa o serviço de OCR.
        """
        self.supported_languages = self._get_supported_languages()
        logger.info(f"OCR Service inicializado com {len(self.supported_languages)} idiomas suportados")

    def _get_supported_languages(self) -> List[str]:
        """
        Obtém a lista de idiomas suportados pelo Tesseract OCR.
        
        Returns:
            Lista de códigos de idioma suportados
        """
        try:
            # Obter idiomas disponíveis no Tesseract
            langs = pytesseract.get_languages()
            return langs if langs else ["por", "eng"]  # Fallback para português e inglês
        except Exception as e:
            logger.warning(f"Não foi possível obter idiomas do Tesseract: {str(e)}")
            return ["por", "eng"]  # Fallback para português e inglês

    def process_image(
        self, 
        image_path: str, 
        lang: str = "por", 
        config: str = "",
        output_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Processa uma imagem com OCR para extrair texto.
        
        Args:
            image_path: Caminho para a imagem a ser processada
            lang: Código do idioma para OCR (por=português, eng=inglês, etc)
            config: Configurações adicionais para o Tesseract
            output_type: Tipo de saída (text, hocr, tsv, etc)
            
        Returns:
            Dicionário com os resultados do OCR
        """
        logger.info(f"Processando OCR na imagem: {image_path}")
        
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {image_path}",
                    "text": ""
                }
            
            # Verificar se o idioma é suportado
            if lang not in self.supported_languages:
                logger.warning(f"Idioma {lang} não suportado. Usando 'por' como fallback.")
                lang = "por"
            
            # Abrir a imagem
            with Image.open(image_path) as img:
                # Pré-processamento da imagem (opcional)
                # img = self._preprocess_image(img)
                
                # Extrair texto com OCR
                if output_type == "text":
                    text = pytesseract.image_to_string(img, lang=lang, config=config)
                    result = {
                        "success": True,
                        "text": text,
                        "lang": lang
                    }
                elif output_type == "data":
                    data = pytesseract.image_to_data(img, lang=lang, config=config, output_type=pytesseract.Output.DICT)
                    result = {
                        "success": True,
                        "data": data,
                        "lang": lang
                    }
                elif output_type == "hocr":
                    hocr = pytesseract.image_to_pdf_or_hocr(img, lang=lang, config=config, extension='hocr')
                    result = {
                        "success": True,
                        "hocr": hocr,
                        "lang": lang
                    }
                else:
                    text = pytesseract.image_to_string(img, lang=lang, config=config)
                    result = {
                        "success": True,
                        "text": text,
                        "lang": lang
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao processar OCR na imagem {image_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao processar OCR: {str(e)}",
                "text": ""
            }

    def process_pdf_images(
        self, 
        images_dir: str, 
        lang: str = "por", 
        config: str = ""
    ) -> Dict[str, Any]:
        """
        Processa todas as imagens em um diretório (geralmente extraídas de um PDF).
        
        Args:
            images_dir: Diretório contendo as imagens a serem processadas
            lang: Código do idioma para OCR
            config: Configurações adicionais para o Tesseract
            
        Returns:
            Dicionário com os resultados do OCR para cada imagem
        """
        logger.info(f"Processando OCR em imagens do diretório: {images_dir}")
        
        results = {
            "success": True,
            "pages": [],
            "full_text": ""
        }
        
        try:
            # Verificar se o diretório existe
            if not os.path.exists(images_dir):
                return {
                    "success": False,
                    "error": f"Diretório não encontrado: {images_dir}",
                    "pages": [],
                    "full_text": ""
                }
            
            # Processar cada imagem no diretório
            image_files = sorted([
                f for f in os.listdir(images_dir) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))
            ])
            
            full_text = ""
            
            for image_file in image_files:
                image_path = os.path.join(images_dir, image_file)
                result = self.process_image(image_path, lang, config)
                
                if result["success"]:
                    page_text = result.get("text", "")
                    full_text += page_text + "\n\n"
                    
                    results["pages"].append({
                        "filename": image_file,
                        "text": page_text,
                        "success": True
                    })
                else:
                    results["pages"].append({
                        "filename": image_file,
                        "error": result.get("error", "Erro desconhecido"),
                        "success": False
                    })
            
            results["full_text"] = full_text
            return results
            
        except Exception as e:
            logger.error(f"Erro ao processar OCR nas imagens do diretório {images_dir}: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao processar OCR: {str(e)}",
                "pages": [],
                "full_text": ""
            }

    def detect_language(self, image_path: str) -> str:
        """
        Detecta o idioma do texto em uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Código do idioma detectado (ou 'por' como fallback)
        """
        try:
            # Esta é uma implementação simplificada
            # Uma implementação mais robusta usaria o OSD do Tesseract
            # ou uma biblioteca específica para detecção de idioma
            
            # Usar o Tesseract para extrair texto com detecção de script
            with Image.open(image_path) as img:
                osd = pytesseract.image_to_osd(img)
                
                # Extrair o script detectado
                for line in osd.split('\n'):
                    if 'Script' in line:
                        script = line.split(':')[1].strip()
                        
                        # Mapear script para idioma (simplificado)
                        script_to_lang = {
                            'Latin': 'por',  # Assumir português para script latino
                            'Arabic': 'ara',
                            'Cyrillic': 'rus',
                            'Devanagari': 'hin',
                            'Chinese': 'chi_sim',
                            'Japanese': 'jpn',
                            'Korean': 'kor'
                        }
                        
                        return script_to_lang.get(script, 'por')
            
            return 'por'  # Fallback para português
        except Exception as e:
            logger.warning(f"Erro ao detectar idioma: {str(e)}")
            return 'por'  # Fallback para português

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Pré-processa uma imagem para melhorar os resultados do OCR.
        
        Args:
            image: Imagem PIL a ser processada
            
        Returns:
            Imagem processada
        """
        # Implementação básica - pode ser expandida com técnicas mais avançadas
        # como binarização adaptativa, remoção de ruído, etc.
        
        # Converter para escala de cinza
        if image.mode != 'L':
            image = image.convert('L')
        
        # Aumentar contraste (opcional)
        # from PIL import ImageEnhance
        # enhancer = ImageEnhance.Contrast(image)
        # image = enhancer.enhance(2.0)
        
        return image
