import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import shutil

from app.core.config import UPLOAD_DIR, RESULTS_DIR
from app.core.docling_adapter import DoclingAdapter

# Inicializar o adaptador Docling
docling_adapter = DoclingAdapter()

def process_document(
    file_path: str,
    original_filename: str,
    extract_text: bool = True,
    extract_tables: bool = True,
    extract_images: bool = False
) -> Dict[str, Any]:
    """
    Processa um documento usando a biblioteca Docling.

    Args:
        file_path: Caminho para o arquivo a ser processado
        original_filename: Nome original do arquivo
        extract_text: Se deve extrair texto do documento
        extract_tables: Se deve extrair tabelas do documento
        extract_images: Se deve extrair imagens do documento

    Returns:
        Dicionário com os resultados do processamento
    """
    try:
        # Gerar ID único para o documento
        document_id = str(uuid.uuid4())

        # Criar diretório para os resultados
        result_dir = os.path.join(RESULTS_DIR, document_id)
        os.makedirs(result_dir, exist_ok=True)

        # Processar o documento usando o adaptador Docling
        processing_result = docling_adapter.process_document(
            file_path=file_path,
            extract_text=extract_text,
            extract_tables=extract_tables,
            extract_images=extract_images
        )

        # Preparar informações do documento
        document_info = {
            "id": document_id,
            "original_filename": original_filename,
            "processed_at": datetime.now().isoformat(),
            "file_type": os.path.splitext(original_filename)[1].lower()[1:],
            "file_size": os.path.getsize(file_path),
            "status": processing_result.get("status", "error"),
            "message": processing_result.get("message", "Erro desconhecido durante o processamento")
        }

        # Adicionar conteúdo processado se disponível
        if processing_result.get("content"):
            document_info["content"] = processing_result["content"]

        # Salvar metadados do documento
        with open(os.path.join(result_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(document_info, f, ensure_ascii=False, indent=2)

        # Salvar conteúdo em markdown se disponível
        if extract_text and processing_result.get("content", {}).get("markdown"):
            with open(os.path.join(result_dir, "content.md"), "w", encoding="utf-8") as f:
                f.write(processing_result["content"]["markdown"])

        # Salvar conteúdo em HTML se disponível
        if extract_text and processing_result.get("content", {}).get("html"):
            with open(os.path.join(result_dir, "content.html"), "w", encoding="utf-8") as f:
                f.write(processing_result["content"]["html"])

        # Copiar o arquivo original para o diretório de resultados
        shutil.copy2(file_path, os.path.join(result_dir, os.path.basename(file_path)))

        return document_info

    except Exception as e:
        # Registrar erro e repassar a exceção
        print(f"Erro ao processar documento: {str(e)}")
        raise

def get_document_info(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtém informações sobre um documento processado.

    Args:
        document_id: ID do documento

    Returns:
        Dicionário com informações do documento ou None se não encontrado
    """
    result_dir = os.path.join(RESULTS_DIR, document_id)
    metadata_path = os.path.join(result_dir, "metadata.json")

    if not os.path.exists(metadata_path):
        return None

    # Carregar metadados do documento
    with open(metadata_path, "r", encoding="utf-8") as f:
        document_info = json.load(f)

    # Adicionar caminhos para arquivos de conteúdo se existirem
    markdown_path = os.path.join(result_dir, "content.md")
    html_path = os.path.join(result_dir, "content.html")

    document_info["files"] = {
        "metadata": metadata_path,
        "markdown": markdown_path if os.path.exists(markdown_path) else None,
        "html": html_path if os.path.exists(html_path) else None,
        "original": os.path.join(result_dir, os.path.basename(document_info.get("original_filename", "")))
    }

    return document_info

def list_documents(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Lista documentos processados.

    Args:
        limit: Número máximo de documentos a retornar
        offset: Índice inicial

    Returns:
        Lista de documentos
    """
    documents = []

    # Listar diretórios em RESULTS_DIR
    if os.path.exists(RESULTS_DIR):
        dirs = [d for d in os.listdir(RESULTS_DIR) if os.path.isdir(os.path.join(RESULTS_DIR, d))]

        # Ordenar por data de modificação (mais recente primeiro)
        dirs.sort(key=lambda d: os.path.getmtime(os.path.join(RESULTS_DIR, d)), reverse=True)

        # Aplicar paginação
        dirs = dirs[offset:offset+limit]

        # Obter metadados de cada documento
        for dir_name in dirs:
            doc_info = get_document_info(dir_name)
            if doc_info:
                documents.append(doc_info)

    return documents
