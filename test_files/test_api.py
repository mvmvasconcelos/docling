import requests
import json
import os

# URL da API
url = "http://docling:8080/api/process"

# Caminho para o arquivo PDF
file_path = "/app/uploads/test_document.pdf"

# Verificar se o arquivo existe
if not os.path.exists(file_path):
    print(f"Arquivo não encontrado: {file_path}")
    exit(1)

# Preparar os dados do formulário
files = {"file": open(file_path, "rb")}
data = {
    "extract_text": "true",
    "extract_tables": "true",
    "extract_images": "true",
    "extract_pages_as_images": "true"
}

# Fazer a requisição
print(f"Enviando requisição para {url} com o arquivo {file_path}...")
response = requests.post(url, files=files, data=data)

# Verificar o status da resposta
print(f"Status da resposta: {response.status_code}")

# Imprimir a resposta
try:
    json_response = response.json()
    print(json.dumps(json_response, indent=2))

    # Verificar se há imagens extraídas
    if "content" in json_response and "images" in json_response["content"]:
        images = json_response["content"]["images"]
        print(f"\nImagens extraídas: {len(images)}")
        for i, image in enumerate(images):
            print(f"Imagem {i+1}:")
            print(f"  Tipo: {image.get('type', 'N/A')}")
            print(f"  Arquivo: {image.get('filename', 'N/A')}")
            print(f"  Caminho: {image.get('path', 'N/A')}")
            print(f"  Formato: {image.get('format', 'N/A')}")
            print(f"  Dimensões: {image.get('width', 'N/A')}x{image.get('height', 'N/A')}")
            print(f"  Tamanho: {image.get('size_bytes', 'N/A')} bytes")
    else:
        print("\nNenhuma imagem extraída.")
except Exception as e:
    print(f"Erro ao processar a resposta: {str(e)}")
    print(f"Resposta: {response.text}")
