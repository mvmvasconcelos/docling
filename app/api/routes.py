from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Path
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, PlainTextResponse
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime
import simplejson as json

from app.services.document_service import process_document, get_document_info, save_document_result
from app.core.config import UPLOAD_DIR, RESULTS_DIR
from app.core.version import get_version_info

router = APIRouter()

# Garantir que o diretório de upload exista
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/process")
async def upload_and_process_document(
    file: UploadFile = File(...),
    extract_text: bool = Form(True),
    extract_tables: bool = Form(True),
    extract_images: bool = Form(False),
    extract_pages_as_images: bool = Form(False),
    apply_ocr: bool = Form(False),
    ocr_lang: str = Form("por"),
):
    """
    Processa um documento enviado pelo usuário.

    - **file**: Arquivo a ser processado (PDF, DOCX, XLSX)
    - **extract_text**: Se deve extrair texto do documento
    - **extract_tables**: Se deve extrair tabelas do documento
    - **extract_images**: Se deve extrair imagens incorporadas no documento
    - **extract_pages_as_images**: Se deve converter páginas inteiras em imagens (apenas para PDF)
    - **apply_ocr**: Se deve aplicar OCR nas imagens extraídas
    - **ocr_lang**: Idioma para OCR (por=português, eng=inglês, auto=detecção automática)
    """
    # Verificar tipo de arquivo
    allowed_extensions = [".pdf", ".docx", ".xlsx"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}",
        )

    # Gerar nome único para o arquivo
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Salvar arquivo
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")

    # Processar documento
    try:
        # Se for um arquivo XLSX, tratamos de forma especial para evitar problemas com NaN
        if file_ext == ".xlsx":
            try:
                import pandas as pd
                import numpy as np

                # Criar resultado básico
                document_id = str(uuid.uuid4())
                result = {
                    "id": document_id,
                    "filename": file.filename,
                    "status": "success",
                    "content": {
                        "text": "",
                        "markdown": "",
                        "html": "",
                        "tables": []
                    },
                    "metadata": {
                        "title": file.filename,
                        "sheets": []
                    }
                }

                # Processar o arquivo XLSX manualmente
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                result["metadata"]["sheets"] = sheet_names

                # Extrair tabelas
                if extract_tables:
                    tables = []
                    for sheet_name in sheet_names:
                        try:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)

                            # Substituir NaN por None para compatibilidade com JSON
                            df = df.replace({np.nan: None})

                            # Extrair cabeçalhos e dados
                            headers = df.columns.tolist()
                            data = []

                            # Converter cada linha para lista, substituindo NaN por None
                            for _, row in df.iterrows():
                                row_data = []
                                for col in headers:
                                    val = row[col]
                                    if pd.isna(val):
                                        row_data.append(None)
                                    else:
                                        row_data.append(val)
                                data.append(row_data)

                            tables.append({
                                "page": 1,  # Excel não tem conceito de página
                                "sheet": sheet_name,
                                "data": data,
                                "headers": headers,
                            })
                        except Exception as e:
                            # Em caso de erro, adicionar informação de erro
                            tables.append({
                                "page": 1,
                                "sheet": sheet_name,
                                "error": str(e),
                                "headers": [],
                                "data": []
                            })

                    result["content"]["tables"] = tables

                # Extrair texto
                if extract_text:
                    text = ""
                    for sheet_name in sheet_names:
                        try:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                            # Substituir NaN por strings vazias para exibição de texto
                            df = df.fillna("")
                            text += f"Sheet: {sheet_name}\n\n"
                            text += df.to_string(index=False, na_rep="") + "\n\n"
                        except Exception as e:
                            text += f"Sheet: {sheet_name}\n\nErro ao processar: {str(e)}\n\n"

                    result["content"]["text"] = text
                    result["content"]["markdown"] = text
                    result["content"]["html"] = f"<pre>{text}</pre>"

                # Salvar resultado no diretório de resultados
                save_document_result(document_id, result, file_path, file.filename)

                # Usar simplejson para lidar com valores NaN
                return result
            except Exception as e:
                # Se falhar o processamento especial, tentamos o processamento normal
                print(f"Erro no processamento especial de XLSX: {str(e)}")

        # Processamento normal para outros tipos de arquivo
        result = process_document(
            file_path=file_path,
            original_filename=file.filename,
            extract_text=extract_text,
            extract_tables=extract_tables,
            extract_images=extract_images,
            extract_pages_as_images=extract_pages_as_images,
            apply_ocr=apply_ocr,
            ocr_lang=ocr_lang,
        )

        # Não precisamos mais limpar valores NaN, pois simplejson lida com isso automaticamente
        return result
    except Exception as e:
        # Em caso de erro, retornar uma resposta de erro mais amigável
        error_id = str(uuid.uuid4())
        error_message = f"Erro ao processar o documento: {str(e)}"
        print(f"Erro {error_id}: {error_message}")
        import traceback
        traceback.print_exc()  # Imprimir o stack trace completo

        # Em caso de erro, remover o arquivo
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "id": error_id,
            "filename": file.filename,
            "status": "error",
            "error": error_message,
            "content": {
                "text": "",
                "markdown": "",
                "html": "",
                "tables": []
            }
        }


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Obtém informações sobre um documento processado.

    - **document_id**: ID do documento
    """
    try:
        document_info = get_document_info(document_id)
        if not document_info:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Não precisamos mais limpar valores NaN, pois simplejson lida com isso automaticamente
        return document_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao obter informações do documento: {str(e)}"
        )


@router.get("/documents/{document_id}/download/{format}")
async def download_document(
    document_id: str,
    format: str = Path(..., description="Formato de download: original, markdown, html"),
):
    """
    Faz o download do documento processado no formato especificado.

    - **document_id**: ID do documento
    - **format**: Formato de download (original, markdown, html)
    """
    try:
        document_info = get_document_info(document_id)
        if not document_info:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Verificar se o formato solicitado está disponível
        if format not in ["original", "markdown", "html"]:
            raise HTTPException(status_code=400, detail=f"Formato não suportado: {format}")

        # Obter o caminho do arquivo solicitado
        file_path = document_info.get("files", {}).get(format)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, detail=f"Arquivo no formato {format} não disponível"
            )

        # Definir o tipo de conteúdo e nome do arquivo para download
        filename = os.path.basename(file_path)
        if format == "original":
            media_type = "application/octet-stream"
            filename = document_info.get("original_filename", filename)
        elif format == "markdown":
            media_type = "text/markdown"
            filename = f"{document_id}.md"
        elif format == "html":
            media_type = "text/html"
            filename = f"{document_id}.html"

        # Retornar o arquivo para download
        return FileResponse(path=file_path, media_type=media_type, filename=filename)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao fazer download do documento: {str(e)}"
        )


@router.get("/documents/{document_id}/preview/{format}")
async def preview_document(
    document_id: str,
    format: str = Path(..., description="Formato de preview: markdown, html, text"),
):
    """
    Visualiza o conteúdo do documento processado no formato especificado.

    - **document_id**: ID do documento
    - **format**: Formato de visualização (markdown, html, text)
    """
    try:
        document_info = get_document_info(document_id)
        if not document_info:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Verificar se o formato solicitado está disponível
        if format not in ["markdown", "html", "text"]:
            raise HTTPException(status_code=400, detail=f"Formato não suportado: {format}")

        # Obter o caminho do arquivo solicitado
        if format == "text":
            # Para texto, usamos o conteúdo do markdown
            file_path = document_info.get("files", {}).get("markdown")
        else:
            file_path = document_info.get("files", {}).get(format)

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, detail=f"Conteúdo no formato {format} não disponível"
            )

        # Ler o conteúdo do arquivo
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Retornar o conteúdo no formato apropriado
        if format == "html":
            return HTMLResponse(content=content)
        elif format in ["markdown", "text"]:
            return PlainTextResponse(content=content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao visualizar o documento: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Verifica o status do serviço.
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.get("/documents/{document_id}/images")
async def list_document_images(document_id: str):
    """
    Lista todas as imagens extraídas de um documento.

    - **document_id**: ID do documento
    """
    try:
        document_info = get_document_info(document_id)
        if not document_info:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Verificar se o documento tem imagens
        images = document_info.get("content", {}).get("images", [])

        if not images:
            return {
                "document_id": document_id,
                "count": 0,
                "images": []
            }

        return {
            "document_id": document_id,
            "count": len(images),
            "images": images
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar imagens do documento: {str(e)}"
        )


@router.get("/documents/{document_id}/images/{image_id}")
async def get_document_image(document_id: str, image_id: str):
    """
    Obtém uma imagem específica extraída de um documento.

    - **document_id**: ID do documento
    - **image_id**: ID ou nome do arquivo da imagem
    """
    try:
        document_info = get_document_info(document_id)
        if not document_info:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Verificar se o documento tem imagens
        images = document_info.get("content", {}).get("images", [])

        if not images:
            raise HTTPException(status_code=404, detail="Documento não possui imagens")

        # Procurar a imagem pelo ID ou nome do arquivo
        image_info = None
        for img in images:
            if img.get("id") == image_id or img.get("filename") == image_id:
                image_info = img
                break

        if not image_info:
            raise HTTPException(status_code=404, detail=f"Imagem {image_id} não encontrada")

        # Verificar se o arquivo existe
        image_path = image_info.get("path")
        if not image_path or not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Arquivo de imagem não encontrado")

        # Retornar a imagem
        return FileResponse(
            path=image_path,
            media_type=f"image/{image_info.get('format', 'png').lower()}",
            filename=image_info.get("filename")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao obter imagem do documento: {str(e)}"
        )


@router.post("/documents/{document_id}/images/{image_id}/ocr")
async def process_image_ocr(
    document_id: str,
    image_id: str,
    lang: str = Form("por"),
):
    """
    Processa OCR em uma imagem específica de um documento.

    - **document_id**: ID do documento
    - **image_id**: ID ou nome do arquivo da imagem
    - **lang**: Idioma para OCR (por=português, eng=inglês, auto=detecção automática)
    """
    try:
        # Obter informações do documento
        document_info = get_document_info(document_id)
        if not document_info:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Verificar se o documento tem imagens
        images = document_info.get("content", {}).get("images", [])
        if not images:
            raise HTTPException(status_code=404, detail="Documento não possui imagens")

        # Procurar a imagem pelo ID ou nome do arquivo
        image_info = None
        for img in images:
            if img.get("id") == image_id or img.get("filename") == image_id:
                image_info = img
                break

        if not image_info:
            raise HTTPException(status_code=404, detail=f"Imagem {image_id} não encontrada")

        # Verificar se o arquivo existe
        image_path = image_info.get("path")
        if not image_path or not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Arquivo de imagem não encontrado")

        # Importar o serviço de OCR
        from app.services.ocr_service import OCRService
        ocr_service = OCRService()

        # Processar OCR na imagem
        if lang == "auto":
            # Detectar idioma automaticamente
            detected_lang = ocr_service.detect_language(image_path)
            ocr_result = ocr_service.process_image(image_path, lang=detected_lang)
            ocr_result["detected_lang"] = detected_lang
        else:
            # Usar o idioma especificado
            ocr_result = ocr_service.process_image(image_path, lang=lang)

        # Adicionar informações da imagem ao resultado
        ocr_result["image"] = {
            "id": image_info.get("id"),
            "filename": image_info.get("filename"),
            "format": image_info.get("format"),
            "width": image_info.get("width"),
            "height": image_info.get("height"),
        }

        # Se o OCR foi bem-sucedido, salvar o texto em um arquivo
        if ocr_result.get("success") and ocr_result.get("text"):
            # Criar diretório para resultados de OCR
            result_dir = os.path.join(RESULTS_DIR, document_id)
            ocr_dir = os.path.join(result_dir, "ocr")
            os.makedirs(ocr_dir, exist_ok=True)

            # Salvar texto extraído em arquivo
            text_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}.txt"
            text_path = os.path.join(ocr_dir, text_filename)

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(ocr_result["text"])

            ocr_result["text_file"] = text_path

        return ocr_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar OCR na imagem: {str(e)}"
        )


@router.get("/version")
async def get_version():
    """
    Retorna informações sobre a versão atual do serviço.
    """
    return get_version_info()
