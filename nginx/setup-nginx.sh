#!/bin/bash

# Script para configurar o Nginx para um serviço

# Verificar se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo "Este script precisa ser executado como root (use sudo)"
  exit 1
fi

# Nome do serviço (altere conforme necessário)
SERVICE_NAME="docling"
CONF_FILE="${SERVICE_NAME}.conf"

echo "Configurando Nginx para o serviço ${SERVICE_NAME}..."

# Diretórios conforme info.md
CONFIGS_DIR="/home/ifsul/configs"
NGINX_APPS_DIR="/etc/nginx/conf.d/apps"

# Verificar se os diretórios existem
if [ ! -d "$CONFIGS_DIR" ]; then
  echo "Diretório $CONFIGS_DIR não encontrado. Criando..."
  mkdir -p "$CONFIGS_DIR"
fi

if [ ! -d "$NGINX_APPS_DIR" ]; then
  echo "Diretório $NGINX_APPS_DIR não encontrado. Criando..."
  mkdir -p "$NGINX_APPS_DIR"
fi

# Copiar arquivo de configuração para o diretório de configurações
echo "Copiando ${CONF_FILE} para $CONFIGS_DIR..."
cp ${CONF_FILE} "$CONFIGS_DIR/"

# Copiar arquivo de configuração para o diretório de aplicações do Nginx
echo "Copiando ${CONF_FILE} para $NGINX_APPS_DIR..."
cp ${CONF_FILE} "$NGINX_APPS_DIR/"

# Verificar a configuração do Nginx
echo "Verificando a configuração do Nginx..."
nginx -t

if [ $? -eq 0 ]; then
  # Reiniciar o serviço Nginx
  echo "Reiniciando o serviço Nginx..."
  systemctl reload nginx

  echo "Configuração do Nginx concluída com sucesso!"
  echo "O serviço ${SERVICE_NAME} estará disponível em:"
  echo "- API: https://ifva.duckdns.org/${SERVICE_NAME}/api/"
  echo "- Documentação: https://ifva.duckdns.org/${SERVICE_NAME}/docs"
  echo "- Interface Web: https://ifva.duckdns.org/${SERVICE_NAME}/web"
else
  echo "Erro na configuração do Nginx. Por favor, verifique o arquivo de configuração."
  exit 1
fi
