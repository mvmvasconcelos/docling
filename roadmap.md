# Roadmap do Projeto Docling

## 1. Fundação do Projeto (MVP - Fase 1)

### 1.1 Configuração do Ambiente de Desenvolvimento
#### [x] 1.1.1 Criar ambiente virtual Python com dependências isoladas
Estabelecer um ambiente Python isolado usando virtualenv ou Docker para garantir consistência entre ambientes de desenvolvimento e produção, evitando conflitos de dependências.

#### [ ] 1.1.2 Configurar linting e formatação (black, flake8, mypy)
Implementar ferramentas de qualidade de código para manter padrões consistentes, facilitando a manutenção e colaboração. Essencial para projetos em containers Docker onde a consistência é crucial.

#### [ ] 1.1.3 Implementar testes unitários básicos
Criar testes automatizados para validar funcionalidades core, garantindo que alterações futuras não quebrem funcionalidades existentes, especialmente importante em ambiente containerizado.

#### [x] 1.1.4 Configurar CI/CD básico
Estabelecer pipeline de integração e entrega contínua para automatizar testes, build e deploy dos containers Docker no servidor Ubuntu, mantendo o site https://ifva.duckdns.org/docling/ sempre atualizado.

### 1.2 Implementação Core do Docling
#### [ ] 1.2.1 Integrar biblioteca Docling como dependência
Incorporar a biblioteca principal de processamento de documentos, garantindo compatibilidade com o ambiente Docker e configurando corretamente no container de aplicação.

#### [ ] 1.2.2 Criar adaptadores para isolamento da biblioteca (padrão adapter)
Desenvolver camada de abstração para isolar dependências externas, facilitando atualizações futuras e testes, essencial para manter a aplicação resiliente em ambiente containerizado.

#### [x] 1.2.3 Implementar interface básica de processamento
Criar APIs internas para processamento de documentos que serão expostas via Nginx, permitindo operações básicas acessíveis através da URL https://ifva.duckdns.org/docling/.

#### [ ] 1.2.4 Criar testes para funcionalidades core
Desenvolver testes abrangentes para garantir que as funcionalidades principais funcionem corretamente em todos os ambientes, especialmente no container Docker de produção.

### 1.3 Sistema de Armazenamento
#### [x] 1.3.1 Implementar interface de armazenamento (Storage Interface)
Criar abstração para operações de armazenamento, permitindo diferentes implementações (local, volumes Docker, serviços em nuvem) sem alterar o código da aplicação.

#### [x] 1.3.2 Criar implementação para armazenamento local
Desenvolver sistema de armazenamento que utilize o sistema de arquivos do container ou volumes Docker persistentes, garantindo que os dados sobrevivam a reinicializações.

#### [ ] 1.3.3 Adicionar sistema de limpeza automática de arquivos temporários
Implementar rotinas para remover arquivos temporários não utilizados, otimizando o uso de espaço em disco no servidor Ubuntu e nos volumes Docker.

#### [ ] 1.3.4 Implementar logging de operações de arquivo
Criar sistema de logs detalhados para rastrear operações de arquivo, facilitando diagnóstico de problemas no ambiente containerizado e monitoramento via Nginx.

## 2. Desenvolvimento da API (MVP - Fase 2)

### 2.1 Endpoints Básicos
#### [x] 2.1.1 Implementar upload de documento único
Desenvolver endpoint REST para receber documentos, acessível via https://ifva.duckdns.org/docling/api/upload, com configuração adequada no Nginx para suportar uploads de arquivos grandes.

#### [x] 2.1.2 Criar endpoint de status do processamento
Implementar API para consultar o status de processamento de documentos, permitindo monitoramento assíncrono através da interface web ou chamadas diretas à API.

#### [ ] 2.1.3 Desenvolver endpoint de download de resultados
Criar rota para baixar resultados processados, configurando corretamente o Nginx para servir arquivos estáticos de forma eficiente e segura.

#### [x] 2.1.4 Adicionar validação de tipos de arquivo
Implementar verificações de segurança para garantir que apenas tipos de arquivo permitidos sejam processados, protegendo o sistema contra uploads maliciosos.

### 2.2 Processamento de Documentos
#### [ ] 2.2.1 Implementar extração de texto básica
Desenvolver funcionalidade para extrair conteúdo textual de documentos comuns (PDF, DOC, TXT), otimizada para execução dentro do container Docker.

#### [ ] 2.2.2 Adicionar extração de tabelas
Criar sistema para identificar e extrair dados tabulares de documentos, utilizando bibliotecas compatíveis com o ambiente Linux do container.

#### [ ] 2.2.3 Desenvolver extração de imagens
Implementar funcionalidade para extrair e processar imagens de documentos, com suporte adequado às bibliotecas gráficas necessárias no container Docker.

#### [ ] 2.2.4 Criar sistema de filas para processamento assíncrono
Desenvolver infraestrutura de filas (como Redis ou RabbitMQ) em containers separados para gerenciar processamento assíncrono, evitando sobrecarga do servidor web Nginx.

### 2.3 Documentação e Testes
#### [x] 2.3.1 Documentar todos os endpoints com OpenAPI
Criar documentação interativa da API usando OpenAPI/Swagger, acessível via https://ifva.duckdns.org/docling/api/docs, facilitando integração por terceiros.

#### [ ] 2.3.2 Criar collection Postman para testes
Desenvolver conjunto de requisições Postman para testar a API, facilitando testes manuais e automatizados contra o ambiente containerizado.

#### [ ] 2.3.3 Implementar testes de integração
Criar testes automatizados que validem o funcionamento completo do sistema, incluindo comunicação entre containers e integração com Nginx.

#### [ ] 2.3.4 Documentar fluxos de uso comum
Elaborar documentação detalhada sobre casos de uso típicos, com exemplos práticos de como utilizar o sistema através da URL https://ifva.duckdns.org/docling/.

## 3. Melhorias e Otimizações (Pós-MVP)

### 3.1 Performance
#### [ ] 3.1.1 Implementar cache de resultados
Desenvolver sistema de cache (Redis em container separado) para armazenar resultados frequentemente acessados, reduzindo carga no servidor e melhorando tempo de resposta.

#### [ ] 3.1.2 Otimizar processamento de arquivos grandes
Implementar processamento em chunks para arquivos volumosos, evitando sobrecarga de memória nos containers Docker e garantindo estabilidade do sistema.

#### [ ] 3.1.3 Adicionar compressão de resultados
Configurar compressão gzip no Nginx e na aplicação para reduzir volume de dados transferidos, melhorando performance especialmente em conexões lentas.

#### [ ] 3.1.4 Implementar limites de tamanho e quota
Criar sistema de controle de uso de recursos para evitar abuso, configurando limites no Nginx para tamanho máximo de upload e quotas de armazenamento por usuário.

### 3.2 Armazenamento em Nuvem
#### [ ] 3.2.1 Criar adapter para Google Drive
Implementar integração com Google Drive como opção de armazenamento externo, permitindo escalar além dos limites do servidor Ubuntu local.

#### [ ] 3.2.2 Implementar adapter para OneDrive
Desenvolver suporte ao OneDrive como alternativa de armazenamento, oferecendo flexibilidade para diferentes ambientes corporativos.

#### [ ] 3.2.3 Adicionar sistema de configuração de storage
Criar interface para administradores configurarem opções de armazenamento via painel web, sem necessidade de modificar containers Docker.

#### [ ] 3.2.4 Implementar migração entre storages
Desenvolver funcionalidade para transferir dados entre diferentes sistemas de armazenamento de forma transparente, facilitando upgrades e manutenção.

### 3.3 Segurança
#### [ ] 3.3.1 Implementar autenticação básica
Criar sistema de autenticação para proteger a API e interface web, integrando com o Nginx para garantir que todas as rotas em https://ifva.duckdns.org/docling/ sejam seguras.

#### [ ] 3.3.2 Adicionar rate limiting
Configurar limitação de requisições no Nginx para prevenir ataques de força bruta e garantir disponibilidade do serviço para todos os usuários.

#### [ ] 3.3.3 Criar sistema de permissões
Implementar controle de acesso baseado em papéis (RBAC) para diferentes funcionalidades do sistema, permitindo uso compartilhado seguro.

#### [ ] 3.3.4 Implementar sanitização de arquivos
Desenvolver verificação avançada de segurança para arquivos enviados, protegendo o sistema contra malware e ataques via upload de documentos maliciosos.

## 4. Funcionalidades Avançadas

### 4.1 Processamento Avançado
#### [ ] 4.1.1 Adicionar OCR para imagens
Implementar reconhecimento óptico de caracteres usando Tesseract em container dedicado, permitindo extrair texto de imagens e PDFs escaneados.

#### [ ] 4.1.2 Implementar extração de metadados
Desenvolver funcionalidade para extrair e indexar metadados de documentos, facilitando organização e busca no sistema.

#### [ ] 4.1.3 Criar sistema de templates de extração
Implementar mecanismo para definir padrões de extração personalizados, permitindo processamento específico para diferentes tipos de documentos.

#### [ ] 4.1.4 Adicionar suporte a documentos compostos
Desenvolver capacidade de processar arquivos complexos (como ZIP contendo múltiplos documentos), mantendo relações entre os componentes.

### 4.2 Integração com Outros Serviços
#### [ ] 4.2.1 Criar webhooks para notificações
Implementar sistema de callbacks HTTP para notificar sistemas externos sobre eventos de processamento, facilitando automação de fluxos de trabalho.

#### [ ] 4.2.2 Implementar integração com n8n
Desenvolver conectores específicos para a plataforma n8n, permitindo automação visual de processos envolvendo documentos processados pelo Docling.

#### [ ] 4.2.3 Desenvolver API para batch processing
Criar endpoints otimizados para processamento em lote, permitindo operações eficientes sobre múltiplos documentos simultaneamente.

#### [ ] 4.2.4 Adicionar suporte a plugins
Implementar arquitetura extensível via plugins, permitindo adicionar funcionalidades sem modificar o core do sistema ou reconstruir containers.

### 4.3 Monitoramento e Manutenção
#### [ ] 4.3.1 Implementar métricas detalhadas
Criar sistema de coleta de métricas (Prometheus em container dedicado) para monitorar performance e uso de recursos dos containers Docker.

#### [ ] 4.3.2 Criar dashboard de monitoramento
Implementar visualização de métricas (Grafana em container dedicado) para acompanhamento em tempo real do estado do sistema.

#### [ ] 4.3.3 Adicionar sistema de alertas
Desenvolver notificações automáticas para condições críticas (disco cheio, containers inativos, erros frequentes), garantindo resposta rápida a problemas.

#### [ ] 4.3.4 Implementar backup automático
Criar rotinas de backup para dados críticos, garantindo que informações importantes possam ser recuperadas em caso de falha do servidor Ubuntu ou corrupção de volumes Docker.

## 5. Interface Web (Opcional)

### 5.1 Frontend Básico
#### [x] 5.1.1 Criar página de upload
Desenvolver interface web responsiva para envio de documentos, acessível via https://ifva.duckdns.org/docling/, com suporte a drag-and-drop e feedback visual.

#### [ ] 5.1.2 Implementar visualização de resultados
Criar visualizador web para documentos processados, permitindo navegar pelo conteúdo extraído sem necessidade de download.

#### [x] 5.1.3 Adicionar feedback de processamento
Implementar indicadores visuais de progresso para operações longas, utilizando WebSockets para atualizações em tempo real do status de processamento.

#### [ ] 5.1.4 Criar área de administração
Desenvolver painel administrativo para configuração do sistema, monitoramento de uso e gerenciamento de usuários, protegido por autenticação.

### 5.2 Funcionalidades Avançadas
#### [ ] 5.2.1 Implementar preview de documentos
Criar visualização prévia de documentos diretamente no navegador, utilizando bibliotecas JavaScript compatíveis com os formatos suportados.

#### [ ] 5.2.2 Adicionar edição de templates
Desenvolver interface visual para criação e edição de templates de extração, permitindo personalização sem conhecimento técnico.

#### [ ] 5.2.3 Criar dashboard de uso
Implementar painéis visuais com estatísticas de uso do sistema, facilitando planejamento de capacidade e identificação de padrões.

#### [ ] 5.2.4 Implementar gestão de usuários
Desenvolver interface completa para administração de usuários, incluindo criação de contas, definição de permissões e monitoramento de atividades.