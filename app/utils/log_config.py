"""
Configuração do sistema de logging para o Docling.

Este módulo configura o sistema de logging para o Docling, incluindo
formatação, rotação de logs e níveis de log para diferentes componentes.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Diretório para logs
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Garantir que o diretório de logs exista
os.makedirs(LOG_DIR, exist_ok=True)

# Configurações padrão
DEFAULT_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file_size_limit": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
}


def configure_logging(
    log_file: Optional[str] = None,
    level: Optional[int] = None,
    console: bool = True,
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Configura o sistema de logging.
    
    Args:
        log_file: Nome do arquivo de log (relativo ao diretório de logs)
        level: Nível de log (logging.DEBUG, logging.INFO, etc.)
        console: Se True, adiciona um handler para console
        config: Configurações personalizadas
    """
    # Mesclar configurações personalizadas com padrões
    cfg = DEFAULT_CONFIG.copy()
    if config:
        cfg.update(config)
    
    # Usar nível de log fornecido ou da configuração
    log_level = level if level is not None else cfg["level"]
    
    # Configurar formato do log
    log_format = cfg["format"]
    date_format = cfg["date_format"]
    formatter = logging.Formatter(log_format, date_format)
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Adicionar handler para console, se solicitado
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Adicionar handler para arquivo, se fornecido
    if log_file:
        file_path = os.path.join(LOG_DIR, log_file)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=cfg["file_size_limit"],
            backupCount=cfg["backup_count"],
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def configure_file_cleaner_logging(console: bool = True) -> None:
    """
    Configura o logging específico para o sistema de limpeza de arquivos.
    
    Args:
        console: Se True, adiciona um handler para console
    """
    # Configurações específicas para o limpador de arquivos
    config = {
        "level": logging.INFO,
        "format": "%(asctime)s [%(levelname)s] [FileClean] %(message)s",
        "file_size_limit": 5 * 1024 * 1024,  # 5 MB
        "backup_count": 3,
    }
    
    # Configurar logging
    configure_logging(
        log_file="file_cleaner.log",
        console=console,
        config=config,
    )
    
    # Configurar logger específico para o módulo
    logger = logging.getLogger("app.utils.file_cleaner")
    logger.setLevel(config["level"])
    
    # Adicionar mensagem inicial
    logger.info("Sistema de limpeza de arquivos inicializado")
