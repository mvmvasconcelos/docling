import os
import sys
import pdf2image
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError

def extract_images_from_pdf(file_path, output_dir):
    """
    Extrai imagens de um PDF.
    
    Args:
        file_path: Caminho para o arquivo PDF
        output_dir: Diretório para salvar as imagens
    """
    print(f"Extraindo imagens do PDF: {file_path}")
    print(f"Salvando em: {output_dir}")
    
    # Garantir que o diretório de saída exista
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Converter páginas do PDF em imagens
        pages = pdf2image.convert_from_path(
            file_path,
            dpi=200,  # Resolução razoável para a maioria dos casos
            fmt="png"
        )
        
        print(f"Convertidas {len(pages)} páginas")
        
        # Salvar cada página como uma imagem
        for i, page in enumerate(pages):
            page_number = i + 1
            image_filename = f"page_{page_number}.png"
            image_path = os.path.join(output_dir, image_filename)
            
            # Salvar a imagem
            page.save(image_path, "PNG")
            print(f"Salva imagem: {image_path}")
            
            # Informações da imagem
            print(f"  Dimensões: {page.width}x{page.height}")
            print(f"  Tamanho: {os.path.getsize(image_path)} bytes")
        
        return True
    except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError) as e:
        print(f"Erro ao converter páginas do PDF em imagens: {str(e)}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_pdf_image_extraction.py <caminho_para_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = "test_output"
    
    if not os.path.exists(pdf_path):
        print(f"Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    success = extract_images_from_pdf(pdf_path, output_dir)
    
    if success:
        print("Extração concluída com sucesso!")
    else:
        print("Falha na extração de imagens.")
