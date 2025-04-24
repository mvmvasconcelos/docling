# Sistema de Limpeza Automática de Arquivos Temporários

## Visão Geral

O Sistema de Limpeza Automática de Arquivos Temporários é responsável por gerenciar o espaço em disco do Docling, identificando e removendo arquivos temporários obsoletos de acordo com políticas de retenção configuráveis. Este sistema é essencial para garantir o funcionamento contínuo da aplicação em ambientes com recursos limitados.

## Componentes Principais

### 1. Políticas de Retenção

O módulo `app/core/retention_policy.py` define por quanto tempo diferentes tipos de arquivos devem ser mantidos:

- **Uploads**: Arquivos enviados pelos usuários (padrão: 1 dia)
- **Resultados**: Resultados de processamento (padrão: 30 dias)
- **Arquivos Temporários**: Arquivos intermediários (padrão: 24 horas)

As políticas podem ser personalizadas através de variáveis de ambiente:
```
RETENTION_UPLOADS_MAX_AGE_DAYS=7
RETENTION_TEMP_FILES_MAX_AGE_HOURS=48
RETENTION_RESULTS_MAX_AGE_DAYS=90
```

### 2. Limpador de Arquivos

O módulo `app/utils/file_cleaner.py` implementa a lógica de identificação e remoção de arquivos obsoletos:

- **Identificação**: Analisa arquivos e determina quais estão obsoletos
- **Remoção**: Remove arquivos de forma segura
- **Estatísticas**: Fornece informações sobre a operação de limpeza

### 3. Monitor de Espaço em Disco

O módulo `app/utils/disk_monitor.py` monitora o espaço em disco e gera alertas quando necessário:

- **Monitoramento**: Verifica o espaço disponível em diretórios importantes
- **Alertas**: Define níveis de alerta (aviso, crítico, emergência)
- **Notificações**: Pode enviar e-mails de alerta quando o espaço estiver abaixo de limites configuráveis

### 4. Scripts de Linha de Comando

- `scripts/clean_temp_files.py`: Script para limpeza manual
- `scripts/monitor_disk_space.py`: Script para monitoramento manual
- `scripts/setup_cron_job.sh`: Script para configurar a limpeza automática via cron

## Uso

### Limpeza Manual

```bash
# Simulação (dry-run)
python scripts/clean_temp_files.py --dry-run --verbose

# Limpeza real
python scripts/clean_temp_files.py

# Limpeza com políticas personalizadas
python scripts/clean_temp_files.py --uploads-max-age=2 --results-max-age=15
```

### Monitoramento de Disco

```bash
# Verificação básica
python scripts/monitor_disk_space.py

# Verificação com limites personalizados
python scripts/monitor_disk_space.py --warning=30 --critical=15 --emergency=5
```

### Configuração de Limpeza Automática

```bash
# Configurar job cron
./scripts/setup_cron_job.sh
```

## Fluxo de Funcionamento

1. **Inicialização**:
   - Carrega as políticas de retenção
   - Configura o sistema de logging

2. **Identificação**:
   - Identifica arquivos de upload obsoletos
   - Identifica resultados de processamento obsoletos
   - Identifica arquivos temporários obsoletos

3. **Remoção**:
   - Remove os arquivos identificados (se não estiver em modo dry-run)
   - Registra estatísticas sobre a operação

4. **Relatório**:
   - Gera um relatório com estatísticas da operação
   - Registra informações detalhadas nos logs

## Melhorias Futuras

### 1. Sistema de Quarentena

Implementar um período de "quarentena" antes da remoção definitiva, permitindo recuperação de arquivos removidos acidentalmente.

**Benefícios**:
- Maior segurança contra remoções acidentais
- Possibilidade de recuperação de dados importantes
- Transição gradual para remoção definitiva

### 2. Interface Web para Estatísticas

Desenvolver uma interface web para visualização de estatísticas de limpeza e gerenciamento de políticas de retenção.

**Benefícios**:
- Monitoramento visual do uso de espaço em disco
- Configuração simplificada de políticas de retenção
- Histórico de operações de limpeza

### 3. Integração com Prometheus/Grafana

Integrar o sistema de limpeza com ferramentas de monitoramento como Prometheus e Grafana para visualização avançada de métricas.

**Benefícios**:
- Monitoramento em tempo real do espaço em disco
- Alertas configuráveis para situações críticas
- Visualização de tendências de uso ao longo do tempo

### 4. Backup Seletivo

Implementar um sistema de backup seletivo para arquivos importantes antes da remoção.

**Benefícios**:
- Preservação de dados críticos
- Redução do risco de perda de informações importantes
- Flexibilidade na definição de critérios para backup

### 5. Sistema de Recuperação

Desenvolver um mecanismo para restaurar arquivos removidos acidentalmente.

**Benefícios**:
- Recuperação de dados em caso de erro
- Maior confiança no sistema de limpeza
- Proteção contra falhas humanas ou do sistema

## Considerações Finais

O Sistema de Limpeza Automática de Arquivos Temporários é uma parte essencial da infraestrutura do Docling, garantindo o uso eficiente dos recursos de armazenamento. As melhorias futuras planejadas irão aumentar ainda mais a robustez e usabilidade do sistema, tornando-o mais seguro e fácil de gerenciar.
