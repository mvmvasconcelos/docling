import os
import sys
import uuid
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar o DoclingAdapter
from app.core.docling_adapter import DoclingAdapter
from app.services.image_service import ImageExtractor

def test_process_document(file_path: str):
    """
    Testa o processamento de um documento usando o DoclingAdapter.
    
    Args:
        file_path: Caminho para o arquivo a ser processado
    """
    print(f"Testando processamento do documento: {file_path}")
    
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return
    
    try:
        # Inicializar o adaptador
        print("Inicializando DoclingAdapter...")
        adapter = DoclingAdapter()
        
        # Verificar se o ImageExtractor foi inicializado corretamente
        print(f"ImageExtractor inicializado: {adapter.image_extractor is not None}")
        
        # Processar o documento
        print("Processando documento...")
        result = adapter.process_document(
            file_path=file_path,
            extract_text=True,
            extract_tables=True,
            extract_images=True,
            extract_pages_as_images=True,
        )
        
        # Verificar o resultado
        print(f"Status do processamento: {result.get('status')}")
        print(f"Mensagem: {result.get('message')}")
        
        # Verificar se há imagens extraídas
        if result.get('content') and 'images' in result['content']:
            images = result['content']['images']
            print(f"Imagens extraídas: {len(images)}")
            for i, image in enumerate(images):
                print(f"Imagem {i+1}:")
                print(f"  Tipo: {image.get('type', 'N/A')}")
                print(f"  Arquivo: {image.get('filename', 'N/A')}")
                print(f"  Caminho: {image.get('path', 'N/A')}")
                print(f"  Formato: {image.get('format', 'N/A')}")
                print(f"  Dimensões: {image.get('width', 'N/A')}x{image.get('height', 'N/A')}")
                print(f"  Tamanho: {image.get('size_bytes', 'N/A')} bytes")
        else:
            print("Nenhuma imagem extraída.")
            
        # Verificar se há erro de extração de imagens
        if result.get('metadata') and 'image_extraction_error' in result['metadata']:
            print(f"Erro de extração de imagens: {result['metadata']['image_extraction_error']}")
        
        return result
    except Exception as e:
        print(f"Erro ao processar documento: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_docling_adapter.py <caminho_para_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_process_document(pdf_path)
