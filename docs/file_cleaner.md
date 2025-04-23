# Sistema de Limpeza Automática de Arquivos Temporários

## 1. Visão Geral

O sistema de limpeza automática de arquivos temporários do Docling foi projetado para otimizar o uso de espaço em disco, removendo arquivos temporários e resultados de processamento obsoletos de forma segura e configurável.

## 2. Estrutura de Armazenamento e Tipos de Arquivos

O sistema Docling utiliza dois diretórios principais para armazenamento de arquivos:

- **UPLOAD_DIR**: Diretório para arquivos enviados pelos usuários (`/app/uploads/`)
- **RESULTS_DIR**: Diretório para resultados processados (`/app/results/`)

### 2.1. Tipos de Arquivos Gerenciados

#### 2.1.1. Arquivos de Upload

**Localização**: `UPLOAD_DIR` (normalmente `/app/uploads/`)

**Descrição**: Arquivos enviados pelos usuários através da API ou interface web. Estes arquivos são salvos com nomes únicos gerados usando UUID.

**Ciclo de Vida**:
1. Criados quando um usuário faz upload de um documento
2. Processados pelo sistema
3. Copiados para o diretório de resultados
4. Não são mais necessários após o processamento bem-sucedido

**Exemplo de Nome**: `123e4567-e89b-12d3-a456-426614174000.pdf`

#### 2.1.2. Arquivos de Processamento Intermediário

**Localização**: Diretório temporário do sistema (gerenciado por `tempfile`)

**Descrição**: Arquivos criados durante o processamento de documentos, como imagens extraídas temporariamente ou arquivos convertidos.

**Ciclo de Vida**:
1. Criados durante o processamento
2. Utilizados para operações intermediárias
3. Deveriam ser removidos automaticamente pelo módulo `tempfile`, mas podem permanecer em caso de falhas

#### 2.1.3. Resultados de Processamento

**Localização**: `RESULTS_DIR` (normalmente `/app/results/`)

**Descrição**: Diretórios contendo resultados de processamento.

**Estrutura**:
- Cada resultado é armazenado em um diretório com ID único (UUID)
- Contém arquivos como `metadata.json`, `content.md`, `content.html` e o arquivo original

**Ciclo de Vida**:
1. Criados após o processamento bem-sucedido
2. Acessados pelos usuários para visualização ou download
3. Podem se tornar obsoletos após um período sem acesso

## 3. Componentes do Sistema

O sistema de limpeza é composto pelos seguintes componentes:

1. **Políticas de Retenção** (`app/core/retention_policy.py`): Define por quanto tempo diferentes tipos de arquivos devem ser mantidos.

2. **Limpador de Arquivos** (`app/utils/file_cleaner.py`): Identifica e remove arquivos temporários obsoletos com base nas políticas de retenção.

3. **Monitor de Disco** (`app/utils/disk_monitor.py`): Monitora o espaço em disco disponível e gera alertas quando necessário.

4. **Scripts de Linha de Comando**:
   - `scripts/clean_temp_files.py`: Script para limpeza manual de arquivos temporários.
   - `scripts/monitor_disk_space.py`: Script para monitoramento manual de espaço em disco.
   - `scripts/setup_cron_job.sh`: Script para configurar a limpeza automática via cron.

5. **Sistema de Logging** (`app/utils/log_config.py`): Registra todas as operações de limpeza e alertas.

## 4. Políticas de Retenção

As políticas de retenção definem por quanto tempo diferentes tipos de arquivos devem ser mantidos antes de serem considerados obsoletos e elegíveis para remoção.

### 4.1. Critérios para Identificação de Arquivos Temporários

#### 4.1.1. Arquivos de Upload
- **Idade**: Arquivos com mais de X dias (configurável)
- **Status**: Arquivos que não foram processados com sucesso ou não têm entrada correspondente no diretório de resultados
- **Tamanho**: Arquivos muito grandes que excedem limites configuráveis

#### 4.1.2. Arquivos de Processamento Intermediário
- **Idade**: Arquivos com mais de X horas (configurável)
- **Localização**: Arquivos em diretórios temporários que não foram limpos corretamente

#### 4.1.3. Resultados de Processamento Antigos
- **Idade**: Resultados com mais de X dias (configurável)
- **Acesso**: Resultados que não foram acessados nos últimos X dias
- **Status**: Resultados de processamentos incompletos ou com erros

### 4.2. Configurações Padrão

| Tipo de Arquivo | Período de Retenção | Critério de Remoção |
|-----------------|---------------------|---------------------|
| Uploads | 1 dia | Idade + Processamento concluído |
| Arquivos Temporários | 24 horas | Idade |
| Resultados | 30 dias | Idade + Último acesso |

### 4.3. Personalização

As políticas de retenção podem ser personalizadas através de variáveis de ambiente:

- `RETENTION_UPLOADS_MAX_AGE_DAYS`: Idade máxima para arquivos de upload (em dias)
- `RETENTION_TEMP_FILES_MAX_AGE_HOURS`: Idade máxima para arquivos temporários (em horas)
- `RETENTION_RESULTS_MAX_AGE_DAYS`: Idade máxima para resultados de processamento (em dias)

## 5. Uso do Sistema

### 5.1. Limpeza Manual

Para executar a limpeza manual de arquivos temporários:

```bash
python scripts/clean_temp_files.py [opções]
```

Opções disponíveis:
- `--dry-run`: Simula a limpeza sem remover arquivos
- `--verbose`: Exibe informações detalhadas durante a execução
- `--output ARQUIVO`: Salva as estatísticas em um arquivo JSON
- `--uploads-max-age DIAS`: Idade máxima para arquivos de upload
- `--results-max-age DIAS`: Idade máxima para resultados de processamento
- `--temp-files-max-age HORAS`: Idade máxima para arquivos temporários
- `--uploads-only`: Limpa apenas arquivos de upload
- `--results-only`: Limpa apenas resultados de processamento
- `--temp-files-only`: Limpa apenas arquivos temporários

### 5.2. Monitoramento de Espaço em Disco

Para verificar o espaço em disco disponível:

```bash
python scripts/monitor_disk_space.py [opções]
```

Opções disponíveis:
- `--verbose`: Exibe informações detalhadas durante a execução
- `--output ARQUIVO`: Salva as informações em um arquivo JSON
- `--no-email`: Desativa o envio de e-mails de alerta
- `--warning PORCENTAGEM`: Limite para alerta de aviso
- `--critical PORCENTAGEM`: Limite para alerta crítico
- `--emergency PORCENTAGEM`: Limite para alerta de emergência

### 5.3. Configuração de Limpeza Automática

Para configurar a limpeza automática via cron:

```bash
sudo ./scripts/setup_cron_job.sh
```

Este script interativo permite configurar:
- Frequência de execução (diária, semanal, mensal ou personalizada)
- Políticas de retenção personalizadas
- Diretório de logs

## 6. Alertas e Monitoramento

O sistema de monitoramento de disco pode enviar alertas por e-mail quando o espaço em disco disponível estiver abaixo de limites configuráveis.

### 6.1. Níveis de Alerta

- **Normal**: Espaço em disco suficiente
- **Aviso**: Espaço em disco abaixo de 20% (configurável)
- **Crítico**: Espaço em disco abaixo de 10% (configurável)
- **Emergência**: Espaço em disco abaixo de 5% (configurável)

### 6.2. Configuração de E-mail

Para configurar o envio de alertas por e-mail, edite as configurações no script `monitor_disk_space.py` ou forneça os parâmetros na linha de comando:

```bash
python scripts/monitor_disk_space.py --smtp-server smtp.example.com --smtp-port 587 --smtp-user usuario --smtp-password senha --from-email docling@example.com --to-emails admin@example.com
```

## 7. Logs e Auditoria

Todas as operações de limpeza e alertas são registradas em arquivos de log:

- `/logs/file_cleaner.log`: Operações de limpeza de arquivos
- `/logs/disk_monitor.log`: Monitoramento de espaço em disco e alertas

Os logs são rotacionados automaticamente para evitar arquivos muito grandes.

## 8. Segurança e Considerações

O sistema de limpeza inclui várias medidas de segurança:

1. **Modo Dry-Run**: Permite simular a limpeza sem remover arquivos
2. **Verificações de Segurança**: Evita a remoção de arquivos importantes
3. **Logging Detalhado**: Registra todas as operações para auditoria
4. **Políticas Configuráveis**: Permite ajustar as políticas de retenção conforme necessário

Considerações adicionais:
- Implementar verificações para evitar remoção acidental de arquivos em uso
- Adicionar mecanismo de recuperação ou período de "quarentena" antes da remoção definitiva

## 9. Solução de Problemas

### 9.1. Arquivos não estão sendo removidos

Verifique:
- Se as políticas de retenção estão configuradas corretamente
- Se o job cron está configurado e em execução
- Se há erros nos logs (`/logs/file_cleaner.log`)

### 9.2. Alertas não estão sendo enviados

Verifique:
- Se a configuração de e-mail está correta
- Se o servidor SMTP está acessível
- Se há erros nos logs (`/logs/disk_monitor.log`)

## 10. Desenvolvimento e Testes

O sistema de limpeza inclui testes automatizados para garantir seu funcionamento correto:

```bash
pytest tests/unit/utils/test_file_cleaner.py
```

Para contribuir com o desenvolvimento, consulte o código-fonte e os testes para entender a implementação.
