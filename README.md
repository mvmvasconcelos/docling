<div align="left">

# 📚 Serviço Docling

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)](http://localhost:8082/docling/)
[![Versão](https://img.shields.io/badge/Versão-1.3.1-blue)](http://localhost:8082/docling/)
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
| 🕐 Extração de Imagens    | 🕐 Edição de Templates    | 🕐 Processamento Assíncrono |

</div>

### 📚 Recursos Adicionais

- **Interface Web Intuitiva**: Upload, visualização e gerenciamento de documentos
- **Armazenamento Persistente**: Documentos e resultados armazenados localmente
- **Metadados**: Extração e indexação de metadados de documentos
- **Arquitetura Modular**: Fácil extensão e personalização
- **Containerização**: Isolamento e facilidade de implantação via Docker

## 💻 Requisitos Técnicos

- **Docker**: 20.10.0 ou superior
- **Docker Compose**: 2.0.0 ou superior
- **Python**: 3.10+ (apenas para desenvolvimento local)
- **Navegador**: Chrome, Firefox, Edge ou Safari recentes

## 💻 Instalação e Execução

O serviço Docling é executado exclusivamente via Docker para garantir isolamento e facilidade de implantação.

### 📦 Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/docling-service.git
cd docling-service

# Construir e iniciar os containers
./run.sh build
./run.sh start
```

### 🔧 Comandos de Gerenciamento

O script `run.sh` fornece comandos intuitivos para gerenciar o serviço:

```bash
./run.sh start         # Iniciar os containers
./run.sh stop          # Parar os containers
./run.sh restart       # Reiniciar os containers
./run.sh status        # Verificar status dos containers
./run.sh logs          # Ver logs em tempo real
./run.sh build         # Reconstruir os containers (após alterações)
```

### 📈 Estado Atual do Projeto

O serviço já implementa as seguintes funcionalidades:

- **Processamento de Documentos**: PDF, DOCX e XLSX
- **Extração de Conteúdo**: Texto e tabelas
- **Conversão de Formatos**: Markdown, HTML e texto plano
- **API REST Completa**: Upload, processamento e download de documentos
- **Interface Web**: Upload, visualização e gerenciamento de documentos
- **Metadados**: Extração de informações como título, número de páginas, etc.

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
│   ├── api/            # Rotas da API
│   ├── core/           # Configurações e funcionalidades centrais
│   │   └── docling_adapter.py  # Adaptador para processamento de documentos
│   ├── models/         # Modelos de dados
│   ├── services/       # Serviços de processamento
│   ├── static/         # Arquivos estáticos (CSS, JS)
│   ├── templates/      # Templates HTML
│   └── utils/          # Utilitários
├── nginx/              # Configuração do Nginx
├── uploads/            # Diretório para upload de arquivos
├── results/            # Diretório para resultados processados
├── Dockerfile          # Configuração do Docker
├── docker-compose.yml  # Configuração do Docker Compose
├── requirements.txt    # Dependências Python
└── roadmap.md          # Plano de desenvolvimento
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