from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

from app.api.routes import router as api_router

# Carregar variáveis de ambiente
load_dotenv()

# Obter configurações de rota
API_PREFIX = os.getenv("API_PREFIX", "/api")
BASE_PATH = os.getenv("BASE_PATH", "")

# Configurar caminhos para templates e arquivos estáticos
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Configurar FastAPI com o caminho base correto para funcionar com o proxy reverso
app = FastAPI(
    title="Docling Service",
    description="Serviço para processamento de documentos usando Docling",
    version="0.1.0",
    # Definir o caminho base para a documentação e rotas
    # Isso é importante quando o serviço está atrás de um proxy reverso
    root_path=BASE_PATH
)

# Configurar templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API
app.include_router(api_router, prefix="/api")

# Rota raiz - API JSON
@app.get("/", response_class=JSONResponse)
async def root():
    return {"message": "Bem-vindo ao serviço Docling", "status": "online"}

# Rota para a interface web
@app.get("/web", response_class=HTMLResponse)
async def web_interface(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Docling - Interface Web"}
    )

# Manipulador de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
