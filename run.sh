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
    echo "  dev           Inicia o container de desenvolvimento"
    echo "  lint          Executa verificação de código (linting)"
    echo "  format        Formata o código automaticamente"
    echo "  test          Executa os testes unitários"
    echo "  coverage      Executa os testes e gera relatório de cobertura"
    echo "  clean         Limpa arquivos temporários"
    echo "  monitor       Monitora o espaço em disco"
    echo "  setup-clean   Configura a limpeza automática de arquivos temporários"
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
    dev)
        echo "Iniciando o container de desenvolvimento..."
        docker-compose up -d docling-dev
        echo "Container de desenvolvimento iniciado! Acesse http://localhost:8083/docs para a documentação da API."
        echo "Use './run.sh lint' para verificar o código ou './run.sh format' para formatá-lo."
        ;;
    lint)
        echo "Executando verificação de código (linting)..."
        ./scripts/lint.sh --check
        ;;
    format)
        echo "Formatando o código automaticamente..."
        ./scripts/lint.sh --format
        ;;
    test)
        echo "Executando testes unitários..."
        ./scripts/test.sh
        ;;
    coverage)
        echo "Executando testes e gerando relatório de cobertura..."
        ./scripts/test.sh --coverage
        ;;
    clean)
        echo "Limpando arquivos temporários..."
        if [ -z "$2" ]; then
            docker exec docling python scripts/clean_temp_files.py
        else
            docker exec docling python scripts/clean_temp_files.py $2 $3 $4 $5 $6 $7 $8 $9
        fi
        ;;
    monitor)
        echo "Monitorando espaço em disco..."
        if [ -z "$2" ]; then
            docker exec docling python scripts/monitor_disk_space.py
        else
            docker exec docling python scripts/monitor_disk_space.py $2 $3 $4 $5 $6 $7 $8 $9
        fi
        ;;
    setup-clean)
        echo "Configurando limpeza automática de arquivos temporários..."
        sudo ./scripts/setup_cron_job.sh
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit 0
