"""
Módulo para extração e processamento de imagens de documentos.

Este módulo fornece funcionalidades para extrair imagens de diferentes tipos de documentos
(PDF, DOCX, PPTX) e realizar processamento básico nessas imagens.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import io
import uuid

from PIL import Image
import pdf2image
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError

from app.core.config import RESULTS_DIR

# Configurar logger
logger = logging.getLogger(__name__)

class ImageExtractor:
    """
    Classe para extrair imagens de documentos.
    """

    def __init__(self):
        """
        Inicializa o extrator de imagens.
        """
        self.supported_formats = {
            'pdf': self.extract_from_pdf,
            'docx': self.extract_from_docx,
            'pptx': self.extract_from_pptx,
        }

    def extract_images(self, file_path: str, document_id: str, extract_pages: bool = False) -> Dict[str, Any]:
        """
        Extrai imagens de um documento.

        Args:
            file_path: Caminho para o arquivo
            document_id: ID do documento
            extract_pages: Se True, também extrai páginas como imagens (para PDFs)

        Returns:
            Dicionário com informações sobre as imagens extraídas
        """
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return {
                "success": False,
                "error": "Arquivo não encontrado",
                "images": []
            }

        # Obter extensão do arquivo
        file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')

        # Verificar se o formato é suportado
        if file_ext not in self.supported_formats:
            logger.warning(f"Formato não suportado para extração de imagens: {file_ext}")
            return {
                "success": False,
                "error": f"Formato não suportado: {file_ext}",
                "images": []
            }

        try:
            # Criar diretório para armazenar as imagens
            images_dir = self._create_images_directory(document_id)

            # Extrair imagens usando o método apropriado
            extract_method = self.supported_formats[file_ext]
            result = extract_method(file_path, images_dir, extract_pages)

            return result
        except Exception as e:
            logger.error(f"Erro ao extrair imagens de {file_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao extrair imagens: {str(e)}",
                "images": []
            }

    def extract_from_pdf(self, file_path: str, images_dir: str, extract_pages: bool = True) -> Dict[str, Any]:
        """
        Extrai imagens de um documento PDF.

        Args:
            file_path: Caminho para o arquivo PDF
            images_dir: Diretório para salvar as imagens
            extract_pages: Se True, também extrai páginas como imagens

        Returns:
            Dicionário com informações sobre as imagens extraídas
        """
        logger.info(f"Extraindo imagens do PDF: {file_path}")

        extracted_images = []

        try:
            # Garantir que o diretório de imagens exista
            os.makedirs(images_dir, exist_ok=True)

            # Extrair páginas como imagens se solicitado
            if extract_pages:
                logger.info("Convertendo páginas do PDF em imagens")
                try:
                    # Converter páginas do PDF em imagens
                    pages = pdf2image.convert_from_path(
                        file_path,
                        dpi=200,  # Resolução razoável para a maioria dos casos
                        fmt="png"
                    )

                    # Salvar cada página como uma imagem
                    for i, page in enumerate(pages):
                        page_number = i + 1
                        image_filename = f"page_{page_number}.png"
                        image_path = os.path.join(images_dir, image_filename)

                        # Salvar a imagem
                        page.save(image_path, "PNG")

                        # Adicionar informações da imagem ao resultado
                        image_info = {
                            "filename": image_filename,
                            "path": image_path,
                            "type": "page",
                            "page": page_number,
                            "format": "png",
                            "width": page.width,
                            "height": page.height,
                            "size_bytes": os.path.getsize(image_path)
                        }
                        extracted_images.append(image_info)

                    logger.info(f"Extraídas {len(pages)} páginas como imagens")
                except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError) as e:
                    logger.error(f"Erro ao converter páginas do PDF em imagens: {str(e)}")
                    return {"error": f"Erro ao converter páginas do PDF: {str(e)}", "images": [], "success": False}

            # TODO: Implementar extração de imagens incorporadas no PDF
            # Esta funcionalidade será implementada em uma versão futura

            # Retornar resultado com sucesso
            return {
                "success": True,
                "images": extracted_images,
                "count": len(extracted_images)
            }
        except Exception as e:
            logger.error(f"Erro ao extrair imagens do PDF {file_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao extrair imagens: {str(e)}",
                "images": extracted_images
            }

    def extract_from_docx(self, file_path: str, images_dir: str, extract_pages: bool = False) -> Dict[str, Any]:
        """
        Extrai imagens de um documento DOCX.

        Args:
            file_path: Caminho para o arquivo DOCX
            images_dir: Diretório para salvar as imagens
            extract_pages: Não utilizado para DOCX

        Returns:
            Dicionário com informações sobre as imagens extraídas
        """
        logger.info(f"Extraindo imagens do DOCX: {file_path}")

        try:
            # Garantir que o diretório de imagens exista
            os.makedirs(images_dir, exist_ok=True)

            # TODO: Implementar extração de imagens de documentos DOCX
            # Esta funcionalidade será implementada em uma versão futura

            return {
                "success": False,
                "error": "Extração de imagens de documentos DOCX ainda não implementada",
                "images": []
            }
        except Exception as e:
            logger.error(f"Erro ao extrair imagens do DOCX {file_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao extrair imagens: {str(e)}",
                "images": []
            }

    def extract_from_pptx(self, file_path: str, images_dir: str, extract_pages: bool = False) -> Dict[str, Any]:
        """
        Extrai imagens de uma apresentação PPTX.

        Args:
            file_path: Caminho para o arquivo PPTX
            images_dir: Diretório para salvar as imagens
            extract_pages: Não utilizado para PPTX

        Returns:
            Dicionário com informações sobre as imagens extraídas
        """
        logger.info(f"Extraindo imagens do PPTX: {file_path}")

        try:
            # Garantir que o diretório de imagens exista
            os.makedirs(images_dir, exist_ok=True)

            # TODO: Implementar extração de imagens de apresentações PPTX
            # Esta funcionalidade será implementada em uma versão futura

            return {
                "success": False,
                "error": "Extração de imagens de apresentações PPTX ainda não implementada",
                "images": []
            }
        except Exception as e:
            logger.error(f"Erro ao extrair imagens do PPTX {file_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao extrair imagens: {str(e)}",
                "images": []
            }

    def _create_images_directory(self, document_id: str) -> str:
        """
        Cria um diretório para armazenar as imagens extraídas.

        Args:
            document_id: ID do documento

        Returns:
            Caminho para o diretório de imagens
        """
        # Diretório do documento
        document_dir = os.path.join(RESULTS_DIR, document_id)

        # Diretório de imagens
        images_dir = os.path.join(document_dir, "images")

        # Criar diretório se não existir
        os.makedirs(images_dir, exist_ok=True)

        return images_dir


def process_image(image_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Processa uma imagem aplicando transformações básicas.

    Args:
        image_path: Caminho para a imagem
        options: Opções de processamento (resize, format, quality, etc.)

    Returns:
        Dicionário com informações sobre a imagem processada
    """
    if options is None:
        options = {}

    try:
        # Abrir a imagem
        with Image.open(image_path) as img:
            # Informações originais da imagem
            original_info = {
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
                "size_bytes": os.path.getsize(image_path)
            }

            # Aplicar processamento (a ser implementado)
            # TODO: Implementar processamento de imagens

            return {
                "success": True,
                "original": original_info,
                "processed": original_info  # Por enquanto, retorna as mesmas informações
            }
    except Exception as e:
        logger.error(f"Erro ao processar imagem {image_path}: {str(e)}")
        return {"error": f"Erro ao processar imagem: {str(e)}"}


def get_image_info(image_path: str) -> Dict[str, Any]:
    """
    Obtém informações sobre uma imagem.

    Args:
        image_path: Caminho para a imagem

    Returns:
        Dicionário com informações sobre a imagem
    """
    try:
        # Abrir a imagem
        with Image.open(image_path) as img:
            # Informações da imagem
            info = {
                "filename": os.path.basename(image_path),
                "path": image_path,
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
                "size_bytes": os.path.getsize(image_path)
            }

            return info
    except Exception as e:
        logger.error(f"Erro ao obter informações da imagem {image_path}: {str(e)}")
        return {"error": f"Erro ao obter informações da imagem: {str(e)}"}
