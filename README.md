<div align="left">

# 📚 Serviço Docling

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)](http://localhost:8082/docling/)
[![Versão](https://img.shields.io/badge/Versão-1.4.0-blue)](http://localhost:8082/docling/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](http://localhost:8082/docling/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](http://localhost:8082/docling/)

<!-- Nota: A versão do projeto é gerenciada centralmente em app/core/version.py -->

</div>

<p align="center">
  <b>Serviço para processamento inteligente de documentos em diversos formatos</b><br>
</p>

---

## 🔎 Sobre o Projeto

O **Serviço Docling** é uma plataforma robusta para processamento de documentos em diversos formatos (PDF, DOCX, XLSX), oferecendo extração de texto, tabelas e metadados através de uma API REST e interface web intuitiva.

Desenvolvido como projeto experimental para prática e expansão de habilidades em desenvolvimento de software, utilizando a infraestrutura do **Instituto Federal Sul-Rio-Grandense de Educação, Ciência e Tecnologia Câmpus Venâncio Aires**.

### 🌐 Acesso Online

O serviço está disponível online em:
- **Interface Web**: [http://localhost:8082/docling/](http://localhost:8082/docling/)
- **API Docs**: [http://localhost:8082/docling/docs](http://localhost:8082/docling/docs)

## ✨ Funcionalidades Principais

<div align="center">

| 📄 Processamento de Documentos | 💬 Conversão de Formatos | 💻 API & Integração |
|:---------------------------:|:------------------------:|:---------------------:|
| ✅ PDF                      | ✅ Texto Plano           | ✅ API REST           |
| ✅ DOCX                     | ✅ Markdown              | ✅ Documentação Swagger |
| ✅ XLSX                     | ✅ HTML                  | ✅ Endpoints Intuitivos |
| ✅ Extração de Texto       | ✅ Visualização no Browser | ✅ Respostas JSON      |
| ✅ Extração de Tabelas     | ✅ Download de Resultados  | ✅ Upload Multipart    |
| ✅ Extração de Imagens    | 🕐 Edição de Templates    | 🕐 Processamento Assíncrono |

</div>

### 📚 Recursos Adicionais

- **Interface Web Intuitiva**: Upload, visualização e gerenciamento de documentos
- **Armazenamento Persistente**: Documentos e resultados armazenados localmente
- **Metadados**: Extração e indexação de metadados de documentos
- **Arquitetura Modular**: Fácil extensão e personalização
- **Containerização**: Isolamento e facilidade de implantação via Docker

### 🖼️ Extração de Imagens

O Docling oferece funcionalidades para extração de imagens de documentos:

- **Extração de Imagens Incorporadas**: Extrai imagens contidas em documentos PDF, DOCX e PPTX
- **Conversão de Páginas em Imagens**: Opcionalmente converte páginas inteiras de PDFs em imagens
- **Controle Granular**: Permite escolher entre extrair apenas imagens incorporadas ou também converter páginas
- **Metadados de Imagens**: Armazena informações como dimensões, formato e tamanho de cada imagem
- **Organização Automática**: Imagens são armazenadas em uma estrutura organizada de diretórios

Para usar a extração de imagens via API:

```bash
# Extrair apenas imagens incorporadas
curl -X POST "http://localhost:8082/docling/api/process" \
  -F "file=@documento.pdf" \
  -F "extract_images=true"

# Extrair imagens incorporadas e converter páginas em imagens
curl -X POST "http://localhost:8082/docling/api/process" \
  -F "file=@documento.pdf" \
  -F "extract_images=true" \
  -F "extract_pages_as_images=true"
```

## 💻 Requisitos Técnicos

- **Docker**: 20.10.0 ou superior
- **Docker Compose**: 2.0.0 ou superior
- **Python**: 3.10+ (apenas para desenvolvimento local)
- **Navegador**: Chrome, Firefox, Edge ou Safari recentes

## 💻 Execução

O serviço Docling é executado exclusivamente via Docker para garantir isolamento e facilidade de implantação.

### 🔧 Comandos de Gerenciamento

O script `run.sh` fornece comandos intuitivos para gerenciar o serviço:

```bash
./run.sh start         # Iniciar os containers
./run.sh stop          # Parar os containers
./run.sh restart       # Reiniciar os containers
./run.sh status        # Verificar status dos containers
./run.sh logs          # Ver logs em tempo real
./run.sh build         # Reconstruir os containers (após alterações)
./run.sh dev           # Iniciar o container de desenvolvimento
./run.sh lint          # Executar verificação de código (linting)
./run.sh format        # Formatar o código automaticamente
./run.sh test          # Executar testes unitários
./run.sh coverage      # Executar testes e gerar relatório de cobertura
./run.sh clean         # Limpar arquivos temporários
./run.sh monitor       # Monitorar espaço em disco
```

#### 🧪 Executando Testes

O comando `./run.sh test` executa os testes dentro do container:

```bash
# Executar todos os testes (unitários e integração)
./run.sh test

# Executar apenas testes unitários
./run.sh test unit

# Executar apenas testes de integração
./run.sh test integration

# Executar testes com saída detalhada
./run.sh test all --verbose

# Executar testes e gerar relatório de cobertura
./run.sh coverage
```

O sistema de testes oferece as seguintes opções:

- **unit**: Executa apenas testes unitários
- **integration**: Executa apenas testes de integração
- **all**: Executa todos os testes (padrão)
- **--verbose**: Exibe informações detalhadas sobre cada teste

Os testes incluem:

- **Testes Unitários**: Verificam componentes individuais como o `ImageExtractor`
- **Testes de Integração**: Verificam o fluxo completo da API e a interação entre componentes

Os relatórios de cobertura são gerados no diretório `coverage_html_report/` e podem ser visualizados em um navegador.

### 📈 Estado Atual do Projeto

O serviço já implementa as seguintes funcionalidades:

- **Processamento de Documentos**: PDF, DOCX e XLSX
- **Extração de Conteúdo**: Texto, tabelas e imagens
- **Conversão de Formatos**: Markdown, HTML e texto plano
- **API REST Completa**: Upload, processamento e download de documentos
- **Interface Web**: Upload, visualização e gerenciamento de documentos
- **Metadados**: Extração de informações como título, número de páginas, etc.
- **Extração de Imagens**: Extração de imagens de PDFs com opção para converter páginas em imagens

Consulte o [Roadmap](roadmap.md) para ver o plano de desenvolvimento futuro.

## 💯 API e Documentação

A API REST do Docling é completamente documentada e fácil de usar:

- **Swagger UI**: [http://localhost:8082/docling/docs](http://localhost:8082/docling/docs)
- **ReDoc**: [http://localhost:8082/docling/redoc](http://localhost:8082/docling/redoc)
- **Interface Web**: [http://localhost:8082/docling/](http://localhost:8082/docling/)

### 📝 Endpoints Principais

| Endpoint | Método | Descrição |
|----------|--------|------------|
| `/api/documents` | `POST` | Upload de um novo documento |
| `/api/documents` | `GET` | Listar todos os documentos |
| `/api/documents/{id}` | `GET` | Obter informações de um documento |
| `/api/documents/{id}/preview/{format}` | `GET` | Visualizar documento em formato específico |
| `/api/documents/{id}/download/{format}` | `GET` | Baixar documento em formato específico |
| `/api/health` | `GET` | Verificar status do serviço |

## 📎 Estrutura do Projeto

```
.
├── app/                # Código da aplicação
│   ├── api/            # Rotas da API REST
│   │   └── routes.py   # Definição dos endpoints
│   ├── core/           # Configurações e funcionalidades centrais
│   │   ├── config.py   # Configurações da aplicação
│   │   ├── docling_adapter.py  # Adaptador para processamento de documentos
│   │   ├── retention_policy.py # Políticas de retenção de documentos
│   │   └── version.py  # Controle de versão centralizado
│   ├── services/       # Serviços de processamento
│   │   ├── document_service.py # Serviço para processamento de documentos
│   │   └── image_service.py    # Serviço para processamento de imagens
│   ├── static/         # Arquivos estáticos (CSS, JS)
│   ├── templates/      # Templates HTML
│   │   └── index.html  # Página principal da interface web
│   ├── utils/          # Utilitários
│   │   ├── disk_monitor.py # Monitoramento de espaço em disco
│   │   ├── file_cleaner.py # Limpeza de arquivos temporários
│   │   └── log_config.py   # Configuração de logs
│   ├── tests/          # Testes da aplicação
│   └── main.py         # Ponto de entrada da aplicação
├── docs/               # Documentação adicional
│   └── file_cleaner.md # Documentação sobre limpeza de arquivos
├── logs/               # Arquivos de log
│   ├── disk_monitor.log
│   └── file_cleaner.log
├── nginx/              # Configuração do Nginx
│   ├── docling.conf    # Configuração específica para o Docling
│   └── setup-nginx.sh  # Script para configuração do Nginx
├── scripts/            # Scripts utilitários
│   ├── clean_temp_files.py  # Script para limpeza de arquivos temporários
│   ├── monitor_disk_space.py # Script para monitoramento de disco
│   ├── setup_cron_job.sh    # Configuração de tarefas agendadas
│   ├── update_badges.py     # Atualização de badges no README
│   └── update_version.py    # Atualização da versão do projeto
├── tests/              # Testes automáticos
│   ├── fixtures/       # Fixtures para testes
│   │   ├── mock_dependencies.py
│   │   └── mock_uploads.py
│   ├── integration/    # Testes de integração
│   └── unit/           # Testes unitários
│       └── test_main.py
├── uploads/            # Diretório para upload de arquivos
│   └── test_temp/      # Arquivos temporários de teste
├── results/            # Diretório para resultados processados
├── Dockerfile          # Configuração do Docker
├── docker-compose.yml  # Configuração do Docker Compose
├── requirements.txt    # Dependências Python principais
├── requirements-dev.txt # Dependências para desenvolvimento
├── mypy.ini           # Configuração do verificador de tipos mypy
├── pytest.ini         # Configuração do framework de teste pytest
├── DEPLOY.md          # Instruções de implantação
├── LICENSE            # Arquivo de licença
├── roadmap.md         # Plano de desenvolvimento futuro
└── run.sh             # Script principal para gerenciar o serviço
```

## 🔰 Versionamento

O projeto Docling segue o padrão de Versionamento Semântico (SemVer) no formato X.Y.Z:

- **X (Major)**: Incrementado quando há mudanças incompatíveis com versões anteriores
- **Y (Minor)**: Incrementado quando há adição de funcionalidades mantendo compatibilidade
- **Z (Patch)**: Incrementado quando há correções de bugs mantendo compatibilidade

A versão do projeto é definida centralmente no arquivo `app/core/version.py` e pode ser atualizada usando o script utilitário:

```bash
# Atualizar versão de patch (correção de bugs)
python scripts/update_version.py patch

# Atualizar versão minor (novas funcionalidades)
python scripts/update_version.py minor --phase "MVP Fase 2"

# Atualizar versão major (mudanças incompatíveis)
python scripts/update_version.py major --phase "Release" --date "Maio 2025"
```

## 📚 Referências e Bibliotecas

Este projeto utiliza as seguintes bibliotecas para processamento de documentos:

- [python-docx](https://python-docx.readthedocs.io/) - Para processamento de documentos DOCX
- [PyPDF2](https://pypdf2.readthedocs.io/) - Para processamento de arquivos PDF
- [pandas](https://pandas.pydata.org/) - Para manipulação de dados tabulares
- [openpyxl](https://openpyxl.readthedocs.io/) - Para processamento de planilhas Excel
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web para a API
- [Jinja2](https://jinja.palletsprojects.com/) - Engine de templates

## 🔒 Licença

Este projeto é licenciado sob a [licença MIT](https://opensource.org/licenses/MIT).

---