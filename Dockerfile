# Imagem base para produção e desenvolvimento
FROM python:3.10-slim as base

WORKDIR /app

# Instalar dependências do sistema básicas e bibliotecas necessárias para Docling
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    libreoffice \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar todas as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Criar diretórios necessários
RUN mkdir -p uploads results logs

# Imagem de produção
FROM base as production

# Copiar o código da aplicação
COPY . .

# Expor a porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Imagem de desenvolvimento com ferramentas de linting
FROM base as development

# Copiar arquivo de requisitos de desenvolvimento
COPY requirements-dev.txt .

# Instalar dependências de desenvolvimento
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copiar o código da aplicação
COPY . .

# Expor a porta
EXPOSE 8000

# Comando para iniciar a aplicação em modo de desenvolvimento
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
