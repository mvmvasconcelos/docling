from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# Caminho para o arquivo PDF de saída
output_pdf = "test_files/test_pdf_with_image.pdf"

# Criar o documento
doc = SimpleDocTemplate(output_pdf, pagesize=letter)

# Conteúdo do documento
content = []

# Adicionar título
styles = getSampleStyleSheet()
content.append(Paragraph("Documento de Teste com Imagem", styles["Title"]))
content.append(Spacer(1, 12))

# Adicionar texto
content.append(Paragraph("Este é um documento de teste para a funcionalidade de extração de imagens do Docling.", styles["Normal"]))
content.append(Spacer(1, 12))

# Verificar se a imagem existe
image_path = "test_files/test_image.jpg"
if os.path.exists(image_path):
    # Adicionar imagem
    img = Image(image_path, width=400, height=300)
    content.append(img)
    content.append(Spacer(1, 12))
    content.append(Paragraph("Imagem de teste acima.", styles["Normal"]))
else:
    content.append(Paragraph("Imagem não encontrada: " + image_path, styles["Normal"]))

# Adicionar mais texto
content.append(Spacer(1, 24))
content.append(Paragraph("Este documento contém uma imagem que deve ser extraída pelo serviço Docling.", styles["Normal"]))

# Construir o PDF
doc.build(content)

print(f"PDF criado com sucesso: {output_pdf}")
