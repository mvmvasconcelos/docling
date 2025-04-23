from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Path
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, PlainTextResponse
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.services.document_service import process_document, get_document_info
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
):
    """
    Processa um documento enviado pelo usuário.

    - **file**: Arquivo a ser processado (PDF, DOCX, XLSX)
    - **extract_text**: Se deve extrair texto do documento
    - **extract_tables**: Se deve extrair tabelas do documento
    - **extract_images**: Se deve extrair imagens do documento
    """
    # Verificar tipo de arquivo
    allowed_extensions = [".pdf", ".docx", ".xlsx"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
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
        result = process_document(
            file_path=file_path,
            original_filename=file.filename,
            extract_text=extract_text,
            extract_tables=extract_tables,
            extract_images=extract_images
        )
        return result
    except Exception as e:
        # Em caso de erro, remover o arquivo
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Erro ao processar documento: {str(e)}")

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
        return document_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações do documento: {str(e)}")

@router.get("/documents/{document_id}/download/{format}")
async def download_document(document_id: str, format: str = Path(..., description="Formato de download: original, markdown, html")):
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
            raise HTTPException(status_code=404, detail=f"Arquivo no formato {format} não disponível")

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
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer download do documento: {str(e)}")

@router.get("/documents/{document_id}/preview/{format}")
async def preview_document(document_id: str, format: str = Path(..., description="Formato de preview: markdown, html, text")):
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
            raise HTTPException(status_code=404, detail=f"Conteúdo no formato {format} não disponível")

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

@router.get("/version")
async def get_version():
    """
    Retorna informações sobre a versão atual do serviço.
    """
    return get_version_info()
