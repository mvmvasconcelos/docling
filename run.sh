#!/bin/bash

# Script para gerenciar o serviço Docling usando Docker

# Criar diretórios necessários para volumes Docker
mkdir -p uploads results

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Erro: Docker e/ou Docker Compose não estão instalados."
    echo "Por favor, instale o Docker e o Docker Compose para continuar."
    exit 1
fi

# Função para mostrar o uso do script
show_usage() {
    echo "Uso: ./run.sh [comando]"
    echo ""
    echo "Comandos:"
    echo "  start         Inicia os containers (padrão se nenhum comando for fornecido)"
    echo "  stop          Para os containers"
    echo "  restart       Reinicia os containers"
    echo "  logs          Mostra os logs dos containers"
    echo "  status        Mostra o status dos containers"
    echo "  build         Reconstrói os containers"
}

# Processar comando
COMMAND=${1:-start}

case "$COMMAND" in
    start)
        echo "Iniciando os containers Docker..."
        docker-compose up -d
        echo "Serviço iniciado! Acesse http://localhost:8082/docs para a documentação da API."
        ;;
    stop)
        echo "Parando os containers Docker..."
        docker-compose down
        ;;
    restart)
        echo "Reiniciando os containers Docker..."
        docker-compose restart
        ;;
    logs)
        echo "Mostrando logs dos containers Docker..."
        docker-compose logs -f
        ;;
    status)
        echo "Status dos containers Docker:"
        docker-compose ps
        ;;
    build)
        echo "Reconstruindo os containers Docker..."
        docker-compose build --no-cache
        echo "Containers reconstruídos. Use './run.sh start' para iniciá-los."
        ;;


    *)
        show_usage
        exit 1
        ;;
esac

exit 0
