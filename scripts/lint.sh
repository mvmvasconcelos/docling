#!/bin/bash

# Script para executar ferramentas de linting dentro do container Docker

# Cores para saída
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Função para exibir mensagem de sucesso
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Função para exibir mensagem de erro
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Função para exibir mensagem de aviso
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado. Por favor, instale o Docker para continuar."
    exit 1
fi

# Verificar se o container de desenvolvimento está em execução
if ! docker ps | grep -q "docling-dev"; then
    warning "O container de desenvolvimento não está em execução."
    echo "Iniciando o container de desenvolvimento..."
    docker-compose up -d docling-dev
    
    # Aguardar o container iniciar
    echo "Aguardando o container iniciar..."
    sleep 5
fi

# Verificar argumentos
FORMAT=false
CHECK=true

for arg in "$@"; do
    case $arg in
        --format)
            FORMAT=true
            ;;
        --check)
            CHECK=true
            ;;
        *)
            echo "Argumento desconhecido: $arg"
            echo "Uso: $0 [--format] [--check]"
            exit 1
            ;;
    esac
done

# Diretório do projeto dentro do container
PROJECT_DIR="app"

echo "Executando verificações de código no diretório: $PROJECT_DIR"
echo "-----------------------------------------------------"

# Executar black
if [ "$FORMAT" = true ]; then
    echo "Formatando código com black..."
    docker exec docling-dev black $PROJECT_DIR
    if [ $? -eq 0 ]; then
        success "Formatação com black concluída com sucesso"
    else
        error "Erro ao formatar código com black"
        exit 1
    fi
else
    echo "Verificando formatação com black..."
    docker exec docling-dev black --check $PROJECT_DIR
    if [ $? -eq 0 ]; then
        success "Verificação de formatação com black concluída com sucesso"
    else
        warning "O código não está formatado de acordo com o black"
        echo "Execute '$0 --format' para formatar o código"
    fi
fi

# Executar flake8
echo "Verificando código com flake8..."
docker exec docling-dev flake8 $PROJECT_DIR
if [ $? -eq 0 ]; then
    success "Verificação com flake8 concluída com sucesso"
else
    error "Erros encontrados pelo flake8"
    if [ "$CHECK" = true ]; then
        exit 1
    fi
fi

# Executar mypy
echo "Verificando tipos com mypy..."
docker exec docling-dev mypy $PROJECT_DIR
if [ $? -eq 0 ]; then
    success "Verificação de tipos com mypy concluída com sucesso"
else
    error "Erros de tipo encontrados pelo mypy"
    if [ "$CHECK" = true ]; then
        exit 1
    fi
fi

echo "-----------------------------------------------------"
echo "Todas as verificações foram concluídas!"
