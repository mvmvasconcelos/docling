FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python básicas
RUN pip install --no-cache-dir fastapi uvicorn python-multipart pydantic python-dotenv jinja2 aiofiles

# Copiar o código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p uploads results

# Expor a porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
