from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# Caminho para o arquivo PDF de saída
output_pdf = "test_files/test_document.pdf"

# Criar o documento
doc = SimpleDocTemplate(output_pdf, pagesize=letter)

# Conteúdo do documento
content = []

# Adicionar título
styles = getSampleStyleSheet()
content.append(Paragraph("Documento de Teste", styles["Title"]))
content.append(Spacer(1, 12))

# Adicionar texto
content.append(Paragraph("Este é um documento de teste para a funcionalidade de extração de imagens do Docling.", styles["Normal"]))
content.append(Spacer(1, 12))

# Adicionar uma tabela
data = [
    ["Coluna 1", "Coluna 2", "Coluna 3"],
    ["Linha 1, Célula 1", "Linha 1, Célula 2", "Linha 1, Célula 3"],
    ["Linha 2, Célula 1", "Linha 2, Célula 2", "Linha 2, Célula 3"],
]

table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))

content.append(table)
content.append(Spacer(1, 24))

# Adicionar mais texto
content.append(Paragraph("Este documento contém uma tabela que deve ser extraída pelo serviço Docling.", styles["Normal"]))

# Construir o PDF
doc.build(content)

print(f"PDF criado com sucesso: {output_pdf}")
