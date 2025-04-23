#!/bin/bash

# Script para executar testes dentro do container Docker

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
COVERAGE=false
UNIT_ONLY=true
VERBOSE=false

for arg in "$@"; do
    case $arg in
        --coverage)
            COVERAGE=true
            ;;
        --all)
            UNIT_ONLY=false
            ;;
        --verbose|-v)
            VERBOSE=true
            ;;
        *)
            echo "Argumento desconhecido: $arg"
            echo "Uso: $0 [--coverage] [--all] [--verbose]"
            exit 1
            ;;
    esac
done

echo "Executando testes..."
echo "-----------------------------------------------------"

# Construir comando de teste
TEST_CMD="pytest"

if [ "$UNIT_ONLY" = true ]; then
    TEST_CMD="$TEST_CMD tests/unit"
else
    TEST_CMD="$TEST_CMD tests"
fi

if [ "$VERBOSE" = true ]; then
    TEST_CMD="$TEST_CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    TEST_CMD="$TEST_CMD --cov=app --cov-report=term --cov-report=html"
fi

# Executar testes
echo "Executando: $TEST_CMD"
docker exec docling-dev $TEST_CMD

if [ $? -eq 0 ]; then
    success "Todos os testes passaram!"
    
    if [ "$COVERAGE" = true ]; then
        echo "Relatório de cobertura gerado em coverage_html_report/"
    fi
else
    error "Alguns testes falharam."
    exit 1
fi

echo "-----------------------------------------------------"
