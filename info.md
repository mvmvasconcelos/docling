# Documentação do Servidor IFVA

Este documento contém informações importantes sobre a configuração e organização do servidor IFVA, bem como orientações para a criação e manutenção de aplicações.

## 1. Orientações Administrativas

Este arquivo será replicado automaticamente para todos os diretórios do projeto através do script em `/home/scripts/vigia_alteracoes.py`.

### 1.1 Criando um Novo Projeto

Sempre que um novo projeto for criado:
- Edite o arquivo `/home/ifsul/pathtoprojects.json` incluindo o novo caminho e nome do projeto na seção `projects`
- Faça cópia do `/home/ifsul/info.md` para o diretório do projeto
- Crie um diretório `nginx` na raiz do projeto
- Crie um script para atualizar os arquivos do nginx (veja abaixo)

> **Importante**:
> - Sempre que fizer alguma modificação no arquivo `info.md`, copie-o para a home usando o comando `cp info.md /home/ifsul/` no terminal.
> - A inclusão do projeto no arquivo `pathtoprojects.json` é essencial para que o projeto seja incluído automaticamente no backup do servidor.

#### Script para Atualizar os Arquivos do Nginx

Crie o script abaixo em `/nginx/setup-nginx.sh` e substitua `nome-do-projeto` pelo nome do novo projeto:

```bash
#!/bin/bash

# Script para configurar o Nginx do projeto

# Nome do projeto (altere conforme necessário)
NOME_DO_PROJETO="nome-do-projeto"
ARQUIVO_CONF="${NOME_DO_PROJETO}.conf"

# Verificar se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo "Este script precisa ser executado como root (use sudo)"
  exit 1
fi

echo "Configurando Nginx para o projeto ${NOME_DO_PROJETO}..."

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
echo "Copiando ${ARQUIVO_CONF} para $CONFIGS_DIR..."
cp ${ARQUIVO_CONF} "$CONFIGS_DIR/"

# Copiar arquivo de configuração para o diretório de aplicações do Nginx
echo "Copiando ${ARQUIVO_CONF} para $NGINX_APPS_DIR..."
cp ${ARQUIVO_CONF} "$NGINX_APPS_DIR/"

# Verificar a configuração do Nginx
echo "Verificando a configuração do Nginx..."
nginx -t

if [ $? -eq 0 ]; then
  # Reiniciar o serviço Nginx
  echo "Reiniciando o serviço Nginx..."
  systemctl reload nginx

  echo "Configuração do Nginx concluída com sucesso!"
  echo "O projeto ${NOME_DO_PROJETO} está configurado."
else
  echo "Erro na configuração do Nginx. Por favor, verifique o arquivo de configuração."
  exit 1
fi
```

### 1.2 Manutenção e Backup

#### Sistema de Backup Automatizado

O servidor possui um sistema de backup automatizado que:
- Realiza backup de todos os projetos listados no arquivo `/home/ifsul/pathtoprojects.yaml`
- Executa backup dos bancos de dados MongoDB e PostgreSQL
- Compacta todos os backups em um único arquivo
- Sincroniza o backup com o OneDrive
- Mantém os últimos 7 backups no servidor

**Para incluir um novo projeto no backup:**
1. Adicione o projeto ao arquivo `/home/ifsul/pathtoprojects.json` na seção `projects` seguindo o formato existente:
   ```json
   {
     "name": "nome_do_projeto",
     "path": "/caminho/completo/do/projeto",
     "databases": [
       {
         "type": "tipo_do_banco",
         "container": "nome_do_container",
         "user": "usuario_do_banco",
         "password": null,
         "database": "nome_do_banco"
       }
     ],
     "category": "Categoria do Projeto"
   }
   ```
2. Para adicionar um novo diretório para backup, edite a seção `backup.directories` no arquivo:
   ```json
   "backup": {
     "directories": [
       {
         "name": "nome_do_diretorio",
         "path": "/caminho/completo/do/diretorio",
         "description": "Descrição do diretório"
       }
     ]
   }
   ```
3. O script de backup lerá automaticamente este arquivo e incluirá o novo projeto, seus bancos de dados e diretórios

#### Backup de Configurações

Todas as configurações do Nginx são mantidas no diretório home do server em `configs` do projeto para facilitar o versionamento e backup.

#### Certificados SSL

Os certificados SSL são gerenciados pelo Let's Encrypt e estão localizados em:
- `/etc/letsencrypt/live/ifva.duckdns.org/fullchain.pem`
- `/etc/letsencrypt/live/ifva.duckdns.org/privkey.pem`

## 2. Configuração Técnica

### 2.1 Estrutura do Nginx

O Nginx está configurado com a seguinte estrutura de diretórios:

- **Arquivo principal**: `/etc/nginx/nginx.conf`
  - Configuração global do servidor
  - Inclui os arquivos de configuração específicos

- **Diretório de sites**: `/etc/nginx/sites-available/` e `/etc/nginx/sites-enabled/`
  - Contém configurações de sites/domínios
  - Os sites ativos são links simbólicos de sites-available para sites-enabled

- **Diretório de aplicações**: `/etc/nginx/conf.d/apps/`
  - Contém arquivos de configuração separados para cada aplicação
  - Cada arquivo define as rotas e configurações específicas de uma aplicação

### 2.2 Portas Utilizadas

#### 2.2.1 Portas Abertas no Firewall Externo

| Porta  | Status     | Serviço/Aplicação                      |
|--------|------------|----------------------------------------|
| 80     | Em uso     | HTTP (redirecionado para HTTPS)        |
| 443    | Em uso     | HTTPS                                  |
| 9090   | Em uso     | n8n (Automação de fluxos de trabalho)  |
| 9091   | Em uso     | Ubuntu Cockpit                         |
| 9092   | Em uso     | Evolution API (WhatsApp API)           |
| 9093   | Disponível | -                                      |
| 9094   | Disponível | -                                      |
| 9095   | Disponível | -                                      |

#### 2.2.2 Portas e Serviços Internos

| Porta  | Serviço                                   | Aplicação                |
|--------|-------------------------------------------|--------------------------|
| 3090   | Frontend do Sistema de Gestão             | Sistema de Gestão        |
| 5000   | Backend do Sistema de Gestão              | Sistema de Gestão        |
| 5173   | Frontend do Sistema de Fiscalização       | Sistema de Fiscalização  |
| 5678   | n8n (porta interna, não exposta)          | n8n                      |
| 8081   | Backend do Sistema de Fiscalização        | Sistema de Fiscalização  |
| 8082   | Serviço Docling                           | Docling                  |
| 9000   | Portainer.io                              | Gerenciamento de Docker  |
| 27017  | MongoDB do Sistema de Gestão              | Sistema de Gestão        |
| 27019  | MongoDB do Sistema de Fiscalização        | Sistema de Fiscalização  |
| 27021  | PostgreSQL da Evolution API               | Evolution API            |
| 27022  | Redis da Evolution API                    | Evolution API            |

## 3. Aplicações Atuais

### 3.1 Portainer.io

| Componente | Detalhes                                                      |
|------------|---------------------------------------------------------------|
| **Aplicação** | **Acesso**: Raiz do site<br>**URL**: https://ifva.duckdns.org<br>**Tecnologia**: Docker<br>**Funcionalidade**: Gerenciamento de contêineres Docker<br>**Porta**: 9000 (interna)<br>**Configuração**: Acesso através do Nginx como proxy reverso |

### 3.2 Sistema de Fiscalização

| Componente | Detalhes                                                      |
|------------|---------------------------------------------------------------|
| **Frontend** | **Rota**: `/fiscalizacao/`<br>**Porta**: 5173<br>**Tecnologia**: React + Vite |
| **API**      | **Rota**: `/fiscalizacao/api/`<br>**Porta**: 8081<br>**Tecnologia**: Node.js + Express<br>**Banco de dados**: MongoDB (porta 27019) |

### 3.3 Sistema de Gestão

| Componente | Detalhes                                                      |
|------------|---------------------------------------------------------------|
| **Frontend** | **Rota**: `/sistema/`<br>**Porta**: 3090 (anteriormente 9090)<br>**Tecnologia**: React + Vite<br>**Acesso**: https://ifva.duckdns.org/sistema |
| **API**      | **Rota**: `/sistema/api/`<br>**Porta**: 5000<br>**Tecnologia**: Node.js + Express<br>**Banco de dados**: MongoDB (porta 27017) |

### 3.4 n8n

| Componente | Detalhes                                                      |
|------------|---------------------------------------------------------------|
| **Aplicação** | **Acesso**: Direto via porta<br>**Porta**: 9090<br>**URL**: http://ifva.duckdns.org:9090<br>**Tecnologia**: Node.js<br>**Funcionalidade**: Automação de fluxos de trabalho<br>**Configuração**: Docker Compose em `/home/ifsul/servicos/n8n/`<br>**Observação**: Utiliza HTTP e não HTTPS, com cookies seguros desativados (N8N_SECURE_COOKIE=false) |

### 3.5 Serviço Docling

| Componente | Detalhes                                                      |
|------------|---------------------------------------------------------------|
| **API** | **Rota**: `/docling/api/`<br>**Porta**: 8082<br>**Tecnologia**: Python + FastAPI<br>**Funcionalidade**: Processamento de documentos (PDF, DOCX, XLSX)<br>**Configuração**: Docker Compose em `/home/ifsul/servicos/docling/`<br>**Acesso**: https://ifva.duckdns.org/docling/<br>**Documentação**: https://ifva.duckdns.org/docling/docs |

### 3.6 Evolution API

| Componente | Detalhes                                                      |
|------------|---------------------------------------------------------------|
| **API** | **Acesso**: Via HTTPS ou direto via porta<br>**Porta**: 9092<br>**URL HTTPS**: https://ifva.duckdns.org/evolutionapi/<br>**URL Direta**: http://ifva.duckdns.org:9092<br>**Tecnologia**: Node.js<br>**Funcionalidade**: API para integração com WhatsApp<br>**Versão**: 2.2.3<br>**Banco de dados**: PostgreSQL (porta 27021)<br>**Cache**: Redis (porta 27022)<br>**Configuração**: Docker Compose em `/home/ifsul/servicos/evolutionapi/`<br>**Autenticação**: API Key (`zaperson123456`)<br>**Documentação**: https://doc.evolution-api.com/ |

## 4. Guias de Procedimentos

### 4.1 Adicionando uma Nova Aplicação

1. Crie um diretório para a aplicação em `/home/ifsul/`

2. Adicione o projeto ao arquivo `/home/ifsul/pathtoprojects.yaml` seguindo o formato:
   ```yaml
   projects:
     - name: nome_do_projeto
       path: /caminho/completo/do/projeto
       databases:
         - type: tipo_do_banco (mongodb, postgresql, redis, etc)
           container: nome_do_container
           user: usuario_do_banco (ou null se não precisar)
           password: senha_do_banco (ou null se não precisar)
           database: nome_do_banco (opcional)
   ```

   Se a aplicação não tiver bancos de dados, use `databases: []`.

3. Crie um arquivo de configuração do Nginx para a aplicação

4. Configure as portas necessárias (verifique a seção de portas utilizadas)

5. Execute o script de configuração do Nginx

6. Atualize este documento com as informações da nova aplicação

### 4.2 Expondo uma Aplicação via Porta Direta

1. Configure a aplicação para usar uma porta específica (ex: 9090)
2. Certifique-se de que a porta está liberada no firewall
3. Acesse a aplicação diretamente via URL com porta (ex: http://ifva.duckdns.org:9090)
4. Se necessário, desative cookies seguros para aplicações HTTP (ex: N8N_SECURE_COOKIE=false)

## 5. Boas Práticas

### 5.1 Segurança

- Sempre use HTTPS para todas as aplicações expostas publicamente
- Mantenha os certificados SSL atualizados
- Não exponha portas desnecessárias
- Use senhas fortes para bancos de dados e serviços
- Implemente rate limiting para APIs públicas
- Mantenha todos os serviços atualizados com as últimas correções de segurança

### 5.2 Performance

- Configure cache adequado no Nginx para conteúdo estático
- Otimize imagens e assets antes de servir
- Use compressão gzip/brotli para reduzir o tamanho das respostas
- Implemente lazy loading para conteúdo não crítico
- Monitore o uso de recursos (CPU, memória, disco) regularmente

### 5.3 Organização

- Mantenha uma estrutura de diretórios consistente
- Documente todas as alterações neste arquivo
- Use nomes descritivos para arquivos de configuração
- Mantenha backups regulares de configurações importantes
- Utilize controle de versão para código e configurações

### 5.4 Desenvolvimento

- Desenvolva em ambientes locais antes de implantar no servidor
- Use Docker para garantir consistência entre ambientes
- Implemente testes automatizados quando possível
- Siga padrões de código consistentes
- Documente APIs com Swagger ou ferramentas similares

## 6. Troubleshooting e FAQ

### 6.1 Problemas Comuns

#### Nginx não reinicia após alterações

Verifique a sintaxe da configuração:
```bash
sudo nginx -t
```

#### Certificado SSL expirado

Renove o certificado Let's Encrypt:
```bash
sudo certbot renew
```

#### Porta já em uso

Verifique qual processo está usando a porta:
```bash
sudo lsof -i :<número-da-porta>
```

### 6.2 FAQ

**P: Como adicionar um novo domínio ao servidor?**
R: Crie um novo arquivo de configuração em `/etc/nginx/sites-available/` e crie um link simbólico para `/etc/nginx/sites-enabled/`.

**P: Como atualizar o certificado SSL?**
R: Os certificados Let's Encrypt são renovados automaticamente. Para forçar a renovação, use `sudo certbot renew`.

**P: Como adicionar um novo banco de dados ao backup?**
R: Edite o arquivo `/home/ifsul/pathtoprojects.yaml` e adicione as informações do banco de dados na seção `databases` do projeto correspondente, seguindo o formato existente.

**P: Como verificar se o backup está funcionando corretamente?**
R: Verifique o arquivo de log em `/var/log/backup.log` ou execute o script manualmente com `sudo /home/ifsul/scripts/backup.sh`.

**P: Como restaurar um backup?**
R: Siga as instruções na seção "Verificação e Restauração de Backup" do arquivo `/home/ifsul/scripts/instrucoes_backup.md`.

## 7. Alterações Recentes

### 22/04/2025 - Atualização do Sistema de Backup

- Implementado sistema de backup baseado em configuração centralizada
- Migrado de YAML para JSON para maior flexibilidade e facilidade de uso
- Atualizado script de backup para ler projetos e diretórios do arquivo `/home/ifsul/pathtoprojects.json`
- Implementado sistema de backup de bancos de dados baseado em configuração
- Adicionado suporte para bancos de dados MongoDB, PostgreSQL e Redis (informação)
- Adicionado suporte para exclusão de diretórios específicos do backup
- Adicionada documentação sobre como incluir novos projetos, bancos de dados e diretórios no backup
- Removidas barras de progresso do script para melhorar a legibilidade
- Atualizado o arquivo `info.md` com informações sobre o sistema de backup

### 16/04/2025 - Migração do n8n para Nova Pasta

- Migrado o n8n de `/home/ifsul/n8n/` para `/home/ifsul/servicos/n8n/`
- Mantida a configuração original e a porta 9090
- Atualizado o arquivo pathtoprojects.yaml
- Atualizada a documentação em `info.md`

### 16/04/2025 - Migração do Projeto para Nova Pasta

- Migrado o projeto de `/home/ifsul/servicos/zaperson/` para `/home/ifsul/servicos/evolutionapi/`
- Atualizado o caminho de acesso HTTPS para https://ifva.duckdns.org/evolutionapi/
- Mantida a API key como `zaperson123456` para compatibilidade com sistemas existentes
- Mantido o nome da instância como `zaperson` para evitar quebrar integrações
- Atualizada a configuração do Nginx para refletir o novo caminho
- Atualizada a documentação em `endpoints.md` e `README.md`

### 16/04/2025 - Migração da Evolution API para HTTPS

- Configurado proxy reverso Nginx para a Evolution API
- Implementado acesso seguro via HTTPS em https://ifva.duckdns.org/evolutionapi/
- Configurado suporte a WebSockets para funcionamento correto da API
- Removida configuração conflitante do Nginx (evolutionapi.conf)
- Mantido acesso direto via porta 9092 para compatibilidade
- Adicionadas configurações de segurança e otimização no Nginx

### 15/04/2025 - Atualização da Evolution API

- Adicionado Redis na porta 27022 para cache e melhor desempenho
- Atualizada configuração do docker-compose.yml para incluir dependências corretas
- Criado arquivo .env com configurações baseadas na documentação oficial
- Documentados endpoints funcionais em endpoints.md para referência futura

### 15/04/2025 - Implementação da Evolution API

- Nova API para integração com WhatsApp implementada
- Utiliza a Evolution API v2.2.3 em contêineres Docker
- Configurada para acesso direto via porta 9092
- Utiliza PostgreSQL na porta 27021
- Inclui autenticação via API Key
- Disponível em http://ifva.duckdns.org:9092

### 10/04/2025 - Implementação do Serviço Docling

- Novo serviço para processamento de documentos (PDF, DOCX, XLSX)
- Implementado com Python + FastAPI em containers Docker
- Configurado na porta 8082 com acesso via proxy reverso
- Acessível via https://ifva.duckdns.org/docling/
- Documentação disponível em https://ifva.duckdns.org/docling/docs

### 08/04/2025 - Configuração do n8n

- O n8n foi configurado para acesso direto via porta 9090
- Configurado para usar HTTP em vez de HTTPS
- Cookies seguros desativados com N8N_SECURE_COOKIE=false

### 08/04/2025 - Mudança de Porta do Sistema de Gestão

- A porta do frontend do Sistema de Gestão foi alterada de 9090 para 3090
- A porta 9090 foi liberada para uso em novos projetos
- O sistema continua acessível em https://ifva.duckdns.org/sistema
- A configuração do Nginx foi atualizada para refletir essa mudança
