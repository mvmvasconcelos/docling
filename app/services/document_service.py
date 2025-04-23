import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import shutil

from app.core.config import UPLOAD_DIR, RESULTS_DIR

def process_document(
    file_path: str,
    original_filename: str,
    extract_text: bool = True,
    extract_tables: bool = True,
    extract_images: bool = False
) -> Dict[str, Any]:
    """
    Processa um documento e retorna os resultados básicos.
    Esta é uma versão simplificada que não depende do Docling.

    Args:
        file_path: Caminho para o arquivo a ser processado
        original_filename: Nome original do arquivo
        extract_text: Se deve extrair texto (não implementado ainda)
        extract_tables: Se deve extrair tabelas (não implementado ainda)
        extract_images: Se deve extrair imagens (não implementado ainda)

    Returns:
        Dicionário com os resultados do processamento
    """
    try:
        # Gerar ID único para o documento
        document_id = str(uuid.uuid4())

        # Criar diretório para os resultados
        result_dir = os.path.join(RESULTS_DIR, document_id)
        os.makedirs(result_dir, exist_ok=True)

        # Preparar resultados básicos
        document_info = {
            "id": document_id,
            "original_filename": original_filename,
            "processed_at": datetime.now().isoformat(),
            "file_type": os.path.splitext(original_filename)[1].lower()[1:],
            "file_size": os.path.getsize(file_path),
            "status": "received",
            "message": "Documento recebido. Processamento completo será implementado em breve."
        }

        # Salvar metadados do documento
        with open(os.path.join(result_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(document_info, f, ensure_ascii=False, indent=2)

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
    metadata_path = os.path.join(RESULTS_DIR, document_id, "metadata.json")

    if not os.path.exists(metadata_path):
        return None

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)

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
