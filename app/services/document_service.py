import os
import simplejson as json
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
    extract_images: bool = False,
    extract_pages_as_images: bool = False,
    apply_ocr: bool = False,
    ocr_lang: str = "por",
) -> Dict[str, Any]:
    """
    Processa um documento usando a biblioteca Docling.

    Args:
        file_path: Caminho para o arquivo a ser processado
        original_filename: Nome original do arquivo
        extract_text: Se deve extrair texto do documento
        extract_tables: Se deve extrair tabelas do documento
        extract_images: Se deve extrair imagens incorporadas do documento
        extract_pages_as_images: Se deve converter páginas inteiras em imagens (apenas para PDF)
        apply_ocr: Se deve aplicar OCR nas imagens extraídas
        ocr_lang: Idioma para OCR (por=português, eng=inglês, auto=detecção automática)

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
            extract_images=extract_images,
            extract_pages_as_images=extract_pages_as_images,
            apply_ocr=apply_ocr,
            ocr_lang=ocr_lang,
        )

        # Preparar informações do documento
        document_info = {
            "id": document_id,
            "original_filename": original_filename,
            "processed_at": datetime.now().isoformat(),
            "file_type": os.path.splitext(original_filename)[1].lower()[1:],
            "file_size": os.path.getsize(file_path),
            "status": processing_result.get("status", "error"),
            "message": processing_result.get(
                "message", "Erro desconhecido durante o processamento"
            ),
        }

        # Adicionar conteúdo processado se disponível
        if processing_result.get("content"):
            document_info["content"] = processing_result["content"]

        # Não precisamos mais da função clean_json_values, pois simplejson lida com NaN automaticamente
        # Apenas garantir que não há valores problemáticos
        try:
            # Testar se o objeto pode ser serializado
            json.dumps(document_info)
        except Exception as e:
            print(f"Aviso: Erro ao serializar JSON: {str(e)}")
            # Se não puder, aplicar uma limpeza básica
            import math
            import numpy as np

            def clean_json_values(obj):
                if isinstance(obj, dict):
                    return {k: clean_json_values(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_json_values(item) for item in obj]
                elif isinstance(obj, (float, np.float64, np.float32)) and (math.isnan(obj) or math.isinf(obj)):
                    return None
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                else:
                    return obj

            document_info = clean_json_values(document_info)

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
        print(f"Tipo de erro: {type(e)}")
        print(f"Erro detalhado: {repr(e)}")
        import traceback
        print("Stack trace:")
        traceback.print_exc()  # Imprimir o stack trace completo
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

    # Não precisamos mais da função clean_json_values, pois simplejson lida com NaN automaticamente
    # Apenas garantir que não há valores problemáticos
    try:
        # Testar se o objeto pode ser serializado
        json.dumps(document_info)
    except Exception as e:
        print(f"Aviso: Erro ao serializar JSON: {str(e)}")
        # Se não puder, aplicar uma limpeza básica
        import math
        import numpy as np

        def clean_json_values(obj):
            if isinstance(obj, dict):
                return {k: clean_json_values(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_json_values(item) for item in obj]
            elif isinstance(obj, (float, np.float64, np.float32)) and (math.isnan(obj) or math.isinf(obj)):
                return None
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj

        document_info = clean_json_values(document_info)

    # Adicionar caminhos para arquivos de conteúdo se existirem
    markdown_path = os.path.join(result_dir, "content.md")
    html_path = os.path.join(result_dir, "content.html")

    document_info["files"] = {
        "metadata": metadata_path,
        "markdown": markdown_path if os.path.exists(markdown_path) else None,
        "html": html_path if os.path.exists(html_path) else None,
        "original": os.path.join(
            result_dir, os.path.basename(document_info.get("original_filename", ""))
        ),
    }

    return document_info


def save_document_result(document_id: str, result: Dict[str, Any], file_path: str, original_filename: str) -> None:
    """
    Salva os resultados do processamento de um documento.

    Args:
        document_id: ID do documento
        result: Resultado do processamento
        file_path: Caminho para o arquivo original
        original_filename: Nome original do arquivo
    """
    # Criar diretório para os resultados
    result_dir = os.path.join(RESULTS_DIR, document_id)
    os.makedirs(result_dir, exist_ok=True)

    # Salvar metadados do documento
    with open(os.path.join(result_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Salvar conteúdo em markdown se disponível
    if result.get("content", {}).get("markdown"):
        with open(os.path.join(result_dir, "content.md"), "w", encoding="utf-8") as f:
            f.write(result["content"]["markdown"])

    # Salvar conteúdo em HTML se disponível
    if result.get("content", {}).get("html"):
        with open(os.path.join(result_dir, "content.html"), "w", encoding="utf-8") as f:
            f.write(result["content"]["html"])

    # Copiar o arquivo original para o diretório de resultados
    shutil.copy2(file_path, os.path.join(result_dir, os.path.basename(file_path)))


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
        dirs = dirs[offset : offset + limit]

        # Obter metadados de cada documento
        for dir_name in dirs:
            doc_info = get_document_info(dir_name)
            if doc_info:
                documents.append(doc_info)

    return documents
