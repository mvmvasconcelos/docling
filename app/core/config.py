import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Diretório para upload de arquivos
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))

# Diretório para armazenar resultados processados
RESULTS_DIR = os.getenv("RESULTS_DIR", os.path.join(BASE_DIR, "results"))

# Configurações da API
API_PREFIX = "/api"
API_VERSION = "v1"

# Configurações do servidor
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Garantir que os diretórios necessários existam
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
