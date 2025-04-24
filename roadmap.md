# 🚀 Roadmap do Projeto Docling

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)](http://localhost:8082/docling/)
[![Versão](https://img.shields.io/badge/Versão-1.4.1-blue)](http://localhost:8082/docling/)
[![Última atualização](https://img.shields.io/badge/Última%20atualização-Abril%202025-green)](http://localhost:8082/docling/)

<!-- Nota: A versão do projeto é gerenciada centralmente em app/core/version.py -->

> **Descrição:** Este documento apresenta o plano de desenvolvimento do projeto Docling, organizado em fases e com acompanhamento de progresso.

## 📋 Sumário

- [📊 Resumo de Progresso](#-resumo-de-progresso)
- [🔍 Legenda](#-legenda)
- [🏗️ 1. Fundação do Projeto](#️-1-fundação-do-projeto-mvp---fase-1)
  - [🔧 1.1 Configuração do Ambiente](#-11-configuração-do-ambiente-de-desenvolvimento)
  - [📚 1.2 Implementação Core](#-12-implementação-core-do-docling)
  - [💾 1.3 Sistema de Armazenamento](#-13-sistema-de-armazenamento)
- [🌐 2. Desenvolvimento da API](#-2-desenvolvimento-da-api-mvp---fase-2)
  - [🔌 2.1 Endpoints Básicos](#-21-endpoints-básicos)
  - [📄 2.2 Processamento de Documentos](#-22-processamento-de-documentos)
  - [📝 2.3 Documentação e Testes](#-23-documentação-e-testes)
- [⚡ 3. Melhorias e Otimizações](#-3-melhorias-e-otimizações-pós-mvp)
  - [🚀 3.1 Performance](#-31-performance)
  - [☁️ 3.2 Armazenamento em Nuvem](#️-32-armazenamento-em-nuvem)
  - [🔒 3.3 Segurança](#-33-segurança)
- [🧠 4. Funcionalidades Avançadas](#-4-funcionalidades-avançadas)
  - [🔬 4.1 Processamento Avançado](#-41-processamento-avançado)
  - [🔄 4.2 Integração com Outros Serviços](#-42-integração-com-outros-serviços)
  - [📊 4.3 Monitoramento e Manutenção](#-43-monitoramento-e-manutenção)
- [💻 5. Interface Web](#-5-interface-web-opcional)
  - [🖥️ 5.1 Frontend Básico](#️-51-frontend-básico)
  - [✨ 5.2 Funcionalidades Avançadas](#-52-funcionalidades-avançadas)
- [📝 Notas](#-notas)

---

## 📊 Resumo de Progresso

| Fase | Descrição | Progresso | Status |
|:----:|:------------|:----------:|:--------:|
| **1** | **Fundação do Projeto** | `⬛⬛⬛⬛⬛⬛⬛⬛⬛⬜` 98% | 🛠️ Em andamento |
| **2** | **Desenvolvimento da API** | `⬛⬛⬛⬛⬛⬛⬜⬜⬜⬜` 65% | 🛠️ Em andamento |
| **3** | **Melhorias e Otimizações** | `⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜` 0% | ⏳ Pendente |
| **4** | **Funcionalidades Avançadas** | `⬛⬛⬜⬜⬜⬜⬜⬜⬜⬜` 20% | 🛠️ Em andamento |
| **5** | **Interface Web** | `⬛⬛⬛⬛⬛⬛⬛⬛⬜⬜` 85% | 🛠️ Em andamento |

---

## 🔍 Legenda

| Símbolo | Status | Descrição |
|:--------:|:-----------:|:------------|
| ✅ | **Concluído** | Tarefa finalizada e testada |
| 🛠️ | **Em andamento** | Trabalho em progresso ativo |
| 🔜 | **Planejado** | Próximos itens na fila de desenvolvimento |
| ❌ | **Bloqueado** | Impedimentos técnicos ou dependências |

---

# 🏗️ 1. Fundação do Projeto (MVP - Fase 1)

> **Progresso**: `⬛⬛⬛⬛⬛⬛⬛⬛⬛⬜` 98%
>
> **Status**: 🛠️ Em andamento

## 🔧 1.1 Configuração do Ambiente de Desenvolvimento

### ✅ 1.1.1 Criar ambiente virtual Python com dependências isoladas
Estabelecer um ambiente Python isolado usando virtualenv ou Docker para garantir consistência entre ambientes de desenvolvimento e produção, evitando conflitos de dependências.

### ✅ 1.1.2 Configurar linting e formatação (black, flake8, mypy)
Implementar ferramentas de qualidade de código para manter padrões consistentes, facilitando a manutenção e colaboração. Essencial para projetos em containers Docker onde a consistência é crucial.

### ✅ 1.1.3 Implementar testes unitários básicos
Criar testes automatizados para validar funcionalidades core, garantindo que alterações futuras não quebrem funcionalidades existentes, especialmente importante em ambiente containerizado.

**Subtarefas:**
- ✅ **1.1.3.1** Configurar pytest e pytest-cov no ambiente Docker
- ✅ **1.1.3.2** Criar estrutura de diretórios para testes
- ✅ **1.1.3.3** Configurar geração de relatórios de cobertura
- ✅ **1.1.3.4** Implementar testes para app/core/version.py
- ✅ **1.1.3.5** Implementar testes para app/core/config.py
- ✅ **1.1.3.6** Implementar testes para app/core/docling_adapter.py
- ✅ **1.1.3.7** Implementar testes para app/services/document_service.py
- ✅ **1.1.3.8** Criar mocks para dependências externas
- ✅ **1.1.3.9** Implementar testes para endpoints da API
- ✅ **1.1.3.10** Criar fixtures para simular uploads
- ✅ **1.1.3.11** Adicionar comandos ao script run.sh
- ✅ **1.1.3.12** Configurar limites mínimos de cobertura

### ✅ 1.1.4 Configurar CI/CD básico
Estabelecer pipeline de integração e entrega contínua para automatizar testes, build e deploy dos containers Docker no servidor Ubuntu, mantendo o site http://localhost:8082/docling/ sempre atualizado.

## 📚 1.2 Implementação Core do Docling

### ✅ 1.2.1 Integrar bibliotecas de processamento de documentos
Incorporar bibliotecas leves para processamento de documentos (python-docx, PyPDF2, pandas, openpyxl, markdown), garantindo compatibilidade com o ambiente Docker e evitando dependências pesadas que causam problemas de instalação.

### ✅ 1.2.2 Criar adaptadores para isolamento da biblioteca (padrão adapter)
Desenvolver camada de abstração para isolar dependências externas, facilitando atualizações futuras e testes, essencial para manter a aplicação resiliente em ambiente containerizado.

### ✅ 1.2.3 Implementar interface básica de processamento
Criar APIs internas para processamento de documentos que serão expostas via Nginx, permitindo operações básicas acessíveis através da URL http://localhost:8082/docling/.

### ✅ 1.2.4 Criar testes para funcionalidades core
Desenvolver testes abrangentes para garantir que as funcionalidades principais funcionem corretamente em todos os ambientes, especialmente no container Docker de produção.

## 💾 1.3 Sistema de Armazenamento

### ✅ 1.3.1 Implementar interface de armazenamento (Storage Interface)
Criar abstração para operações de armazenamento, permitindo diferentes implementações (local, volumes Docker, serviços em nuvem) sem alterar o código da aplicação.

**Subtarefas:**
- ✅ **1.3.1.1** Definição da interface StorageInterface
- ✅ **1.3.1.2** Implementação de fábrica para criação de instâncias de storage
- ✅ **1.3.1.3** Desenvolvimento de métodos para gerenciamento de arquivos
- ✅ **1.3.1.4** Criação de sistema de configuração para diferentes storages

### ✅ 1.3.2 Criar implementação para armazenamento local
Desenvolver sistema de armazenamento que utilize o sistema de arquivos do container ou volumes Docker persistentes, garantindo que os dados sobrevivam a reinicializações.

**Subtarefas:**
- ✅ **1.3.2.1** Implementação da classe LocalStorage
- ✅ **1.3.2.2** Configuração de volumes Docker persistentes
- ✅ **1.3.2.3** Desenvolvimento de métodos para operações CRUD de arquivos
- ✅ **1.3.2.4** Implementação de estrutura de diretórios para diferentes tipos de dados

### ✅ 1.3.3 Adicionar sistema de limpeza automática de arquivos temporários
Implementar rotinas para remover arquivos temporários não utilizados, otimizando o uso de espaço em disco no servidor Ubuntu e nos volumes Docker.

**Subtarefas:**
- ✅ **1.3.3.1** Análise e identificação de tipos de arquivos temporários
- ✅ **1.3.3.2** Definição de políticas de retenção por tipo de arquivo
- ✅ **1.3.3.3** Implementação de módulo para identificação de arquivos obsoletos
- ✅ **1.3.3.4** Desenvolvimento de mecanismo de remoção segura
- ✅ **1.3.3.5** Criação de script de linha de comando para limpeza manual
- ✅ **1.3.3.6** Implementação de agendamento periódico via cron
- ✅ **1.3.3.7** Integração com sistema de logging para registro de operações
- ✅ **1.3.3.8** Desenvolvimento de testes automatizados para o sistema de limpeza
- ✅ **1.3.3.9** Configuração de alertas para situações críticas de espaço em disco
- ✅ **1.3.3.10** Documentação do sistema de limpeza e políticas de retenção

### 🔜 1.3.4 Implementar logging de operações de arquivo
Criar sistema de logs detalhados para rastrear operações de arquivo, facilitando diagnóstico de problemas no ambiente containerizado e monitoramento via Nginx.

**Subtarefas:**
- 🔜 **1.3.4.1** Definição de estrutura e formato de logs para operações de arquivo
- 🔜 **1.3.4.2** Implementação de middleware para interceptação de operações de I/O
- 🔜 **1.3.4.3** Criação de sistema de rotação de logs para evitar arquivos muito grandes
- 🔜 **1.3.4.4** Integração com sistema de alerta para operações críticas
- 🔜 **1.3.4.5** Desenvolvimento de interface para consulta e análise de logs

# 🌐 2. Desenvolvimento da API (MVP - Fase 2)

> **Progresso**: `⬛⬛⬛⬛⬛⬛⬜⬜⬜⬜` 65%
>
> **Status**: 🛠️ Em andamento

## 🔌 2.1 Endpoints Básicos

### ✅ 2.1.1 Implementar upload de documento único
Desenvolver endpoint REST para receber documentos, acessível via http://localhost:8082/docling/api/upload, com configuração adequada no Nginx para suportar uploads de arquivos grandes.

### ✅ 2.1.2 Criar endpoint de status do processamento
Implementar API para consultar o status de processamento de documentos, permitindo monitoramento assíncrono através da interface web ou chamadas diretas à API.

### ✅ 2.1.3 Desenvolver endpoint de download de resultados
Criar rota para baixar resultados processados, configurando corretamente o Nginx para servir arquivos estáticos de forma eficiente e segura.

### ✅ 2.1.4 Adicionar validação de tipos de arquivo
Implementar verificações de segurança para garantir que apenas tipos de arquivo permitidos sejam processados, protegendo o sistema contra uploads maliciosos.

## 📄 2.2 Processamento de Documentos

### ✅ 2.2.1 Implementar extração de texto básica
Desenvolver funcionalidade para extrair conteúdo textual de documentos comuns (PDF, DOC, TXT), otimizada para execução dentro do container Docker.

### ✅ 2.2.2 Adicionar extração de tabelas
Criar sistema para identificar e extrair dados tabulares de documentos, utilizando bibliotecas compatíveis com o ambiente Linux do container. Implementado para documentos DOCX e planilhas Excel.

### ✅ 2.2.3 Desenvolver extração de imagens
Implementar funcionalidade para extrair e processar imagens de documentos, com suporte adequado às bibliotecas gráficas necessárias no container Docker.

**Subtarefas:**
- ✅ **2.2.3.1** Integrar bibliotecas de processamento de imagens (Pillow, pdf2image)
  - Adicionar dependências ao requirements.txt
  - Configurar suporte a bibliotecas gráficas no container Docker
  - Implementar testes para verificar a correta instalação das bibliotecas

- ✅ **2.2.3.2** Implementar extração de imagens de documentos PDF
  - Desenvolver função para identificar e extrair imagens incorporadas em PDFs
  - Criar sistema para converter páginas de PDF em imagens quando necessário
  - Implementar metadados para imagens extraídas (página de origem, posição, tamanho)
  - Adicionar suporte a diferentes formatos de compressão em PDFs

- ✅ **2.2.3.7** Desenvolver API para acesso às imagens extraídas
  - Criar endpoints para listar imagens de um documento
  - Implementar endpoint para download de imagens individuais
  - Desenvolver suporte a filtros e parâmetros de processamento
  - Adicionar documentação OpenAPI para os novos endpoints

- ✅ **2.2.3.8** Implementar testes e validação
  - Criar testes unitários para cada formato de documento
  - Desenvolver testes de integração para o fluxo completo
  - Implementar validação de qualidade das imagens extraídas
  - Adicionar testes de performance para documentos com muitas imagens

**Melhorias futuras:**

- 🔜 **2.2.3.3** Implementar extração de imagens de documentos DOCX
  - Desenvolver função para extrair imagens incorporadas em documentos Word
  - Criar sistema para preservar nomes e referências originais das imagens
  - Implementar extração de imagens de cabeçalhos, rodapés e caixas de texto
  - Adicionar suporte a imagens em diferentes formatos (PNG, JPEG, GIF, etc.)

- 🔜 **2.2.3.4** Implementar extração de imagens de apresentações PPTX
  - Desenvolver função para extrair imagens de slides
  - Criar sistema para associar imagens aos slides correspondentes
  - Implementar extração de imagens de plano de fundo e formas
  - Adicionar suporte a imagens em SmartArt e outros elementos complexos

- 🔜 **2.2.3.5** Criar sistema de armazenamento otimizado para imagens
  - Desenvolver estrutura de diretórios para organizar imagens extraídas
  - Implementar naming convention para facilitar rastreamento da origem
  - Criar sistema para evitar duplicação de imagens idênticas
  - Adicionar suporte a thumbnails para preview rápido

- 🔜 **2.2.3.6** Implementar processamento básico de imagens
  - Desenvolver funções para redimensionamento preservando proporções
  - Criar sistema para otimização de tamanho de arquivo
  - Implementar conversão entre formatos de imagem
  - Adicionar suporte a ajustes básicos (brilho, contraste, etc.)

### 🔜 2.2.4 Criar sistema de filas para processamento assíncrono
Desenvolver infraestrutura de filas (como Redis ou RabbitMQ) em containers separados para gerenciar processamento assíncrono, evitando sobrecarga do servidor web Nginx.

## 📝 2.3 Documentação e Testes

### ✅ 2.3.1 Documentar todos os endpoints com OpenAPI
Criar documentação interativa da API usando OpenAPI/Swagger, acessível via http://localhost:8082/docling/api/docs, facilitando integração por terceiros.

### 🔜 2.3.2 Criar collection Postman para testes
Desenvolver conjunto de requisições Postman para testar a API, facilitando testes manuais e automatizados contra o ambiente containerizado.

### 🔜 2.3.3 Implementar testes de integração
Criar testes automatizados que validem o funcionamento completo do sistema, incluindo comunicação entre containers e integração com Nginx.

### 🔜 2.3.4 Documentar fluxos de uso comum
Elaborar documentação detalhada sobre casos de uso típicos, com exemplos práticos de como utilizar o sistema através da URL http://localhost:8082/docling/.

# ⚡ 3. Melhorias e Otimizações (Pós-MVP)

> **Progresso**: `⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜` 0%
>
> **Status**: ⏳ Planejado

## 🚀 3.1 Performance

### 🔜 3.1.1 Implementar cache de resultados
Desenvolver sistema de cache (Redis em container separado) para armazenar resultados frequentemente acessados, reduzindo carga no servidor e melhorando tempo de resposta.

### 🔜 3.1.2 Otimizar processamento de arquivos grandes
Implementar processamento em chunks para arquivos volumosos, evitando sobrecarga de memória nos containers Docker e garantindo estabilidade do sistema.

### 🔜 3.1.3 Adicionar compressão de resultados
Configurar compressão gzip no Nginx e na aplicação para reduzir volume de dados transferidos, melhorando performance especialmente em conexões lentas.

### 🔜 3.1.4 Implementar limites de tamanho e quota
Criar sistema de controle de uso de recursos para evitar abuso, configurando limites no Nginx para tamanho máximo de upload e quotas de armazenamento por usuário.

## ☁️ 3.2 Armazenamento em Nuvem

### 🔜 3.2.1 Criar adapter para Google Drive
Implementar integração com Google Drive como opção de armazenamento externo, permitindo escalar além dos limites do servidor Ubuntu local.

### 🔜 3.2.2 Implementar adapter para OneDrive
Desenvolver suporte ao OneDrive como alternativa de armazenamento, oferecendo flexibilidade para diferentes ambientes corporativos.

### 🔜 3.2.3 Adicionar sistema de configuração de storage
Criar interface para administradores configurarem opções de armazenamento via painel web, sem necessidade de modificar containers Docker.

### 🔜 3.2.4 Implementar migração entre storages
Desenvolver funcionalidade para transferir dados entre diferentes sistemas de armazenamento de forma transparente, facilitando upgrades e manutenção.

## 🔒 3.3 Segurança

### 🔜 3.3.1 Implementar autenticação básica
Criar sistema de autenticação para proteger a API e interface web, integrando com o Nginx para garantir que todas as rotas em http://localhost:8082/docling/ sejam seguras.

### 🔜 3.3.2 Adicionar rate limiting
Configurar limitação de requisições no Nginx para prevenir ataques de força bruta e garantir disponibilidade do serviço para todos os usuários.

### 🔜 3.3.3 Criar sistema de permissões
Implementar controle de acesso baseado em papéis (RBAC) para diferentes funcionalidades do sistema, permitindo uso compartilhado seguro.

### 🔜 3.3.4 Implementar sanitização de arquivos
Desenvolver verificação avançada de segurança para arquivos enviados, protegendo o sistema contra malware e ataques via upload de documentos maliciosos.

## 🧹 3.4 Gerenciamento Avançado de Arquivos

### 🔜 3.4.1 Implementar sistema de quarentena para arquivos
Desenvolver mecanismo para mover arquivos obsoletos para área de quarentena antes da remoção definitiva, permitindo recuperação em caso de exclusão acidental.

### 🔜 3.4.2 Criar interface web para estatísticas de limpeza
Implementar dashboard para visualização de estatísticas do sistema de limpeza automática, incluindo histórico de operações e espaço recuperado.

### 🔜 3.4.3 Integrar com Prometheus/Grafana para monitoramento
Desenvolver exportadores de métricas para o sistema de limpeza, permitindo monitoramento avançado de espaço em disco e operações de arquivo via Grafana.

### 🔜 3.4.4 Adicionar backup seletivo antes da remoção
Implementar sistema para criar backups automáticos de arquivos importantes antes da remoção, baseado em regras configuráveis de seleção.

### 🔜 3.4.5 Desenvolver sistema de recuperação de arquivos
Criar mecanismo para restaurar arquivos removidos acidentalmente, utilizando snapshots incrementais e logs detalhados de operações.

# 🧠 4. Funcionalidades Avançadas

> **Progresso**: `⬛⬛⬜⬜⬜⬜⬜⬜⬜⬜` 20%
>
> **Status**: 🛠️ Em andamento

## 🔬 4.1 Processamento Avançado

### 🔜 4.1.1 Adicionar OCR para imagens
Implementar reconhecimento óptico de caracteres usando Tesseract em container dedicado, permitindo extrair texto de imagens e PDFs escaneados.

### ✅ 4.1.2 Implementar extração de metadados
Desenvolver funcionalidade para extrair e indexar metadados de documentos, facilitando organização e busca no sistema. Implementado para PDF, DOCX e Excel.

### 🔜 4.1.3 Criar sistema de templates de extração
Implementar mecanismo para definir padrões de extração personalizados, permitindo processamento específico para diferentes tipos de documentos.

### 🔜 4.1.4 Adicionar suporte a documentos compostos
Desenvolver capacidade de processar arquivos complexos (como ZIP contendo múltiplos documentos), mantendo relações entre os componentes.

## 🔄 4.2 Integração com Outros Serviços

### 🔜 4.2.1 Criar webhooks para notificações
Implementar sistema de callbacks HTTP para notificar sistemas externos sobre eventos de processamento, facilitando automação de fluxos de trabalho.

### 🔜 4.2.2 Implementar integração com n8n
Desenvolver conectores específicos para a plataforma n8n, permitindo automação visual de processos envolvendo documentos processados pelo Docling.

### 🔜 4.2.3 Desenvolver API para batch processing
Criar endpoints otimizados para processamento em lote, permitindo operações eficientes sobre múltiplos documentos simultaneamente.

### 🔜 4.2.4 Adicionar suporte a plugins
Implementar arquitetura extensível via plugins, permitindo adicionar funcionalidades sem modificar o core do sistema ou reconstruir containers.

## 📊 4.3 Monitoramento e Manutenção

### 🔜 4.3.1 Implementar métricas detalhadas
Criar sistema de coleta de métricas (Prometheus em container dedicado) para monitorar performance e uso de recursos dos containers Docker.

### 🔜 4.3.2 Criar dashboard de monitoramento
Implementar visualização de métricas (Grafana em container dedicado) para acompanhamento em tempo real do estado do sistema.

### 🔜 4.3.3 Adicionar sistema de alertas
Desenvolver notificações automáticas para condições críticas (disco cheio, containers inativos, erros frequentes), garantindo resposta rápida a problemas.

### 🔜 4.3.4 Implementar backup automático
Criar rotinas de backup para dados críticos, garantindo que informações importantes possam ser recuperadas em caso de falha do servidor Ubuntu ou corrupção de volumes Docker.

# 💻 5. Interface Web (Opcional)

> **Progresso**: `⬛⬛⬛⬛⬛⬛⬛⬛⬜⬜` 85%
>
> **Status**: 🛠️ Em andamento

## 🖥️ 5.1 Frontend Básico

### ✅ 5.1.1 Criar página de upload
Desenvolver interface web responsiva para envio de documentos, acessível via http://localhost:8082/docling/, com suporte a drag-and-drop e feedback visual.

### ✅ 5.1.2 Implementar visualização de resultados
Criar visualizador web para documentos processados, permitindo navegar pelo conteúdo extraído sem necessidade de download.

### ✅ 5.1.3 Adicionar feedback de processamento
Implementar indicadores visuais de progresso para operações longas, utilizando WebSockets para atualizações em tempo real do status de processamento.

### 🔜 5.1.4 Criar área de administração
Desenvolver painel administrativo para configuração do sistema, monitoramento de uso e gerenciamento de usuários, protegido por autenticação.

## ✨ 5.2 Funcionalidades Avançadas

### ✅ 5.2.1 Implementar preview de documentos
Criar visualização prévia de documentos diretamente no navegador, utilizando bibliotecas JavaScript compatíveis com os formatos suportados. Implementado para texto, markdown e HTML.

### 🔜 5.2.2 Adicionar edição de templates
Desenvolver interface visual para criação e edição de templates de extração, permitindo personalização sem conhecimento técnico.

### 🔜 5.2.3 Criar dashboard de uso
Implementar painéis visuais com estatísticas de uso do sistema, facilitando planejamento de capacidade e identificação de padrões.

### 🔜 5.2.4 Implementar gestão de usuários
Desenvolver interface completa para administração de usuários, incluindo criação de contas, definição de permissões e monitoramento de atividades.

---

## 📝 Notas

- O progresso é atualizado mensalmente com base nas tarefas concluídas
- A ordem de implementação pode mudar conforme necessidades do projeto
- Sugestões e feedback são bem-vindos através das issues no repositório
- As tarefas marcadas como "Planejado" (🔜) serão priorizadas no próximo ciclo de desenvolvimento

---

**Projeto Docling**
**IFSul Câmpus Venâncio Aires**
Última atualização: 25 de Abril 2025 - Conclusão da funcionalidade de extração de imagens e atualização do progresso
