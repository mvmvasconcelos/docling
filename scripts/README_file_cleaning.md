# Sistema de Limpeza Automática de Arquivos Temporários

## Visão Geral

Este sistema gerencia o espaço em disco do Docling, removendo automaticamente arquivos temporários obsoletos de acordo com políticas de retenção configuráveis.

## Scripts Disponíveis

- **clean_temp_files.py**: Executa a limpeza de arquivos temporários
- **monitor_disk_space.py**: Monitora o espaço em disco e gera alertas
- **setup_cron_job.sh**: Configura a limpeza automática via cron

## Uso Rápido

### Limpeza Manual

```bash
# Simulação (não remove arquivos)
python scripts/clean_temp_files.py --dry-run --verbose

# Limpeza real
python scripts/clean_temp_files.py

# Limpeza com políticas personalizadas
python scripts/clean_temp_files.py --uploads-max-age=7 --results-max-age=60
```

### Monitoramento de Disco

```bash
# Verificação básica
python scripts/monitor_disk_space.py

# Verificação com limites personalizados
python scripts/monitor_disk_space.py --warning=30 --critical=15
```

### Configuração de Limpeza Automática

```bash
# Configurar job cron (requer privilégios de administrador)
sudo ./scripts/setup_cron_job.sh
```

## Políticas de Retenção Padrão

- **Uploads**: 1 dia
- **Resultados**: 30 dias
- **Arquivos Temporários**: 24 horas

## Configuração via Variáveis de Ambiente

```bash
# Configurar políticas de retenção
export RETENTION_UPLOADS_MAX_AGE_DAYS=7
export RETENTION_RESULTS_MAX_AGE_DAYS=90
export RETENTION_TEMP_FILES_MAX_AGE_HOURS=48
```

## Logs e Monitoramento

Os logs de limpeza são armazenados em:
- `logs/file_cleaner_cron.log`: Logs da execução automática via cron
- `logs/docling.log`: Logs gerais da aplicação (inclui operações de limpeza)

## Melhorias Futuras

- Sistema de quarentena para arquivos antes da remoção definitiva
- Interface web para visualização de estatísticas de limpeza
- Integração com Prometheus/Grafana para monitoramento avançado
- Backup seletivo de arquivos importantes antes da remoção
- Sistema de recuperação para restaurar arquivos removidos acidentalmente

Para documentação completa, consulte [docs/file_cleaning_system.md](../docs/file_cleaning_system.md).
