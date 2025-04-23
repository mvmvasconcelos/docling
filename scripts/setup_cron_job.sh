#!/bin/bash
# Script para configurar um job cron para limpeza automática de arquivos temporários

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

# Verificar se o script está sendo executado como root
if [ "$EUID" -ne 0 ]; then
    error "Este script precisa ser executado como root (sudo)."
    exit 1
fi

# Obter o diretório do projeto
PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
SCRIPT_PATH="$PROJECT_DIR/scripts/clean_temp_files.py"
LOG_DIR="$PROJECT_DIR/logs"
CRON_LOG="$LOG_DIR/file_cleaner_cron.log"

# Verificar se o script de limpeza existe
if [ ! -f "$SCRIPT_PATH" ]; then
    error "Script de limpeza não encontrado: $SCRIPT_PATH"
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p "$LOG_DIR"
success "Diretório de logs criado: $LOG_DIR"

# Tornar o script executável
chmod +x "$SCRIPT_PATH"
success "Script de limpeza configurado como executável"

# Definir a frequência do cron job
echo "Selecione a frequência de execução da limpeza automática:"
echo "1) Diariamente (recomendado)"
echo "2) Semanalmente"
echo "3) Mensalmente"
echo "4) Personalizado"

read -p "Opção [1-4]: " frequency_option

case $frequency_option in
    1)
        # Diariamente às 3:00 AM
        CRON_SCHEDULE="0 3 * * *"
        FREQUENCY_DESC="diariamente às 3:00 AM"
        ;;
    2)
        # Semanalmente aos domingos às 3:00 AM
        CRON_SCHEDULE="0 3 * * 0"
        FREQUENCY_DESC="semanalmente aos domingos às 3:00 AM"
        ;;
    3)
        # Mensalmente no primeiro dia do mês às 3:00 AM
        CRON_SCHEDULE="0 3 1 * *"
        FREQUENCY_DESC="mensalmente no primeiro dia do mês às 3:00 AM"
        ;;
    4)
        # Personalizado
        read -p "Digite a expressão cron (ex: '0 3 * * *' para diariamente às 3:00 AM): " CRON_SCHEDULE
        FREQUENCY_DESC="conforme programação personalizada: $CRON_SCHEDULE"
        ;;
    *)
        error "Opção inválida. Usando configuração diária padrão."
        CRON_SCHEDULE="0 3 * * *"
        FREQUENCY_DESC="diariamente às 3:00 AM"
        ;;
esac

# Configurar opções de limpeza
echo "Configurar opções de limpeza:"

read -p "Idade máxima para arquivos de upload (dias) [1]: " uploads_max_age
uploads_max_age=${uploads_max_age:-1}

read -p "Idade máxima para resultados de processamento (dias) [30]: " results_max_age
results_max_age=${results_max_age:-30}

read -p "Idade máxima para arquivos temporários (horas) [24]: " temp_files_max_age
temp_files_max_age=${temp_files_max_age:-24}

# Criar o comando cron
CRON_CMD="$CRON_SCHEDULE cd $PROJECT_DIR && python3 $SCRIPT_PATH --uploads-max-age=$uploads_max_age --results-max-age=$results_max_age --temp-files-max-age=$temp_files_max_age >> $CRON_LOG 2>&1"

# Adicionar o job ao crontab
(crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$CRON_CMD") | crontab -

success "Job cron configurado para executar $FREQUENCY_DESC"
echo "Comando: $CRON_CMD"

# Criar arquivo de configuração para referência futura
CONFIG_FILE="$PROJECT_DIR/scripts/file_cleaner_config.txt"
cat > "$CONFIG_FILE" << EOL
# Configuração da limpeza automática de arquivos temporários
# Configurado em: $(date)

Frequência: $FREQUENCY_DESC
Expressão cron: $CRON_SCHEDULE

Políticas de retenção:
- Uploads: $uploads_max_age dias
- Resultados: $results_max_age dias
- Arquivos temporários: $temp_files_max_age horas

Comando cron:
$CRON_CMD

Para modificar esta configuração, execute novamente:
sudo $0
EOL

success "Arquivo de configuração criado: $CONFIG_FILE"
echo "Configuração concluída com sucesso!"
