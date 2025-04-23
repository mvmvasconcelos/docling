"""
Módulo para monitoramento de espaço em disco.

Este módulo fornece funcionalidades para monitorar o espaço em disco
e gerar alertas quando o espaço disponível estiver abaixo de limites configuráveis.
"""

import os
import shutil
import logging
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.core.config import UPLOAD_DIR, RESULTS_DIR

# Configurar logger
logger = logging.getLogger(__name__)

# Limites padrão para alertas
DEFAULT_THRESHOLDS = {
    "warning": 20,  # Alerta de aviso quando o espaço livre for menor que 20%
    "critical": 10,  # Alerta crítico quando o espaço livre for menor que 10%
    "emergency": 5,  # Alerta de emergência quando o espaço livre for menor que 5%
}

# Configurações de e-mail padrão
DEFAULT_EMAIL_CONFIG = {
    "enabled": False,
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
    "from_email": "docling@example.com",
    "to_emails": ["admin@example.com"],
    "use_tls": True,
}


class DiskMonitor:
    """
    Classe para monitorar o espaço em disco e gerar alertas.
    """
    
    def __init__(
        self,
        thresholds: Optional[Dict[str, int]] = None,
        email_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa o monitor de disco.
        
        Args:
            thresholds: Limites personalizados para alertas
            email_config: Configurações personalizadas para envio de e-mails
        """
        self.thresholds = DEFAULT_THRESHOLDS.copy()
        if thresholds:
            self.thresholds.update(thresholds)
        
        self.email_config = DEFAULT_EMAIL_CONFIG.copy()
        if email_config:
            self.email_config.update(email_config)
    
    def check_disk_space(self, path: str) -> Dict[str, Any]:
        """
        Verifica o espaço em disco para um caminho específico.
        
        Args:
            path: Caminho para verificar
            
        Returns:
            Dicionário com informações sobre o espaço em disco
        """
        try:
            # Obter estatísticas de uso de disco
            disk_usage = shutil.disk_usage(path)
            
            # Calcular porcentagem de espaço livre
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            # Determinar nível de alerta
            alert_level = "normal"
            for level, threshold in sorted(self.thresholds.items(), key=lambda x: x[1]):
                if free_percent < threshold:
                    alert_level = level
            
            # Formatar tamanhos para exibição
            total_gb = disk_usage.total / (1024 ** 3)
            used_gb = disk_usage.used / (1024 ** 3)
            free_gb = disk_usage.free / (1024 ** 3)
            
            return {
                "path": path,
                "total_bytes": disk_usage.total,
                "used_bytes": disk_usage.used,
                "free_bytes": disk_usage.free,
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "free_percent": round(free_percent, 2),
                "alert_level": alert_level,
                "timestamp": datetime.now().isoformat(),
            }
        
        except Exception as e:
            logger.error(f"Erro ao verificar espaço em disco para {path}: {str(e)}")
            return {
                "path": path,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def check_all_paths(self) -> Dict[str, Dict[str, Any]]:
        """
        Verifica o espaço em disco para todos os caminhos relevantes.
        
        Returns:
            Dicionário com informações sobre o espaço em disco para cada caminho
        """
        paths = {
            "uploads": UPLOAD_DIR,
            "results": RESULTS_DIR,
            "root": "/",
        }
        
        results = {}
        for name, path in paths.items():
            results[name] = self.check_disk_space(path)
        
        return results
    
    def get_largest_files(self, path: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém os maiores arquivos em um diretório.
        
        Args:
            path: Caminho para verificar
            count: Número de arquivos a retornar
            
        Returns:
            Lista de dicionários com informações sobre os maiores arquivos
        """
        try:
            # Usar o comando find para encontrar os maiores arquivos
            cmd = [
                "find", path, "-type", "f", "-exec", "du", "-h", "{}", ";",
                "|", "sort", "-rh", "|", "head", f"-{count}"
            ]
            
            # Executar o comando
            result = subprocess.run(
                " ".join(cmd),
                shell=True,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                logger.error(f"Erro ao executar comando find: {result.stderr}")
                return []
            
            # Processar a saída
            largest_files = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                
                parts = line.split("\t")
                if len(parts) != 2:
                    continue
                
                size, file_path = parts
                largest_files.append({
                    "path": file_path,
                    "size": size,
                    "name": os.path.basename(file_path),
                })
            
            return largest_files
        
        except Exception as e:
            logger.error(f"Erro ao obter maiores arquivos em {path}: {str(e)}")
            return []
    
    def send_alert_email(self, disk_info: Dict[str, Dict[str, Any]]) -> bool:
        """
        Envia um e-mail de alerta sobre espaço em disco.
        
        Args:
            disk_info: Informações sobre o espaço em disco
            
        Returns:
            True se o e-mail foi enviado com sucesso, False caso contrário
        """
        if not self.email_config["enabled"]:
            logger.info("Envio de e-mail desativado nas configurações")
            return False
        
        try:
            # Verificar se há algum alerta
            has_alert = False
            for path_info in disk_info.values():
                if "alert_level" in path_info and path_info["alert_level"] != "normal":
                    has_alert = True
                    break
            
            if not has_alert:
                logger.debug("Nenhum alerta para enviar")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg["From"] = self.email_config["from_email"]
            msg["To"] = ", ".join(self.email_config["to_emails"])
            msg["Subject"] = f"[Docling] Alerta de espaço em disco - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Construir corpo do e-mail
            body = "Alerta de espaço em disco no servidor Docling\n\n"
            
            for name, path_info in disk_info.items():
                if "error" in path_info:
                    body += f"{name.upper()}: Erro ao verificar espaço em disco: {path_info['error']}\n"
                    continue
                
                alert_level = path_info.get("alert_level", "normal")
                if alert_level != "normal":
                    alert_text = alert_level.upper()
                else:
                    alert_text = "OK"
                
                body += f"{name.upper()} ({path_info['path']}): {alert_text}\n"
                body += f"  Espaço livre: {path_info['free_gb']} GB ({path_info['free_percent']}%)\n"
                body += f"  Espaço total: {path_info['total_gb']} GB\n"
                body += f"  Espaço usado: {path_info['used_gb']} GB\n\n"
            
            # Adicionar informações sobre os maiores arquivos
            body += "Maiores arquivos em diretórios críticos:\n\n"
            
            for name, path_info in disk_info.items():
                if "error" in path_info or name == "root":
                    continue
                
                path = path_info["path"]
                largest_files = self.get_largest_files(path, count=5)
                
                if largest_files:
                    body += f"Maiores arquivos em {name} ({path}):\n"
                    for file_info in largest_files:
                        body += f"  {file_info['size']}\t{file_info['path']}\n"
                    body += "\n"
            
            # Adicionar recomendações
            body += "Recomendações:\n"
            body += "1. Execute o script de limpeza de arquivos temporários: ./scripts/clean_temp_files.py\n"
            body += "2. Verifique e remova arquivos grandes desnecessários\n"
            body += "3. Considere aumentar o espaço em disco disponível\n"
            
            msg.attach(MIMEText(body, "plain"))
            
            # Enviar e-mail
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                if self.email_config["use_tls"]:
                    server.starttls()
                
                if self.email_config["smtp_user"] and self.email_config["smtp_password"]:
                    server.login(self.email_config["smtp_user"], self.email_config["smtp_password"])
                
                server.send_message(msg)
            
            logger.info(f"E-mail de alerta enviado para {', '.join(self.email_config['to_emails'])}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de alerta: {str(e)}")
            return False
    
    def check_and_alert(self) -> Dict[str, Any]:
        """
        Verifica o espaço em disco e envia alertas se necessário.
        
        Returns:
            Dicionário com informações sobre o espaço em disco e status do alerta
        """
        # Verificar espaço em disco
        disk_info = self.check_all_paths()
        
        # Verificar se há algum alerta
        has_alert = False
        highest_alert = "normal"
        
        for path_info in disk_info.values():
            if "alert_level" in path_info and path_info["alert_level"] != "normal":
                has_alert = True
                
                # Determinar o nível de alerta mais alto
                alert_level = path_info["alert_level"]
                alert_levels = ["normal", "warning", "critical", "emergency"]
                
                if alert_levels.index(alert_level) > alert_levels.index(highest_alert):
                    highest_alert = alert_level
        
        # Registrar informações no log
        if has_alert:
            log_message = f"Alerta de espaço em disco: {highest_alert.upper()}"
            
            if highest_alert == "emergency":
                logger.critical(log_message)
            elif highest_alert == "critical":
                logger.error(log_message)
            else:
                logger.warning(log_message)
            
            # Enviar e-mail de alerta
            email_sent = self.send_alert_email(disk_info)
        else:
            logger.info("Espaço em disco OK")
            email_sent = False
        
        # Retornar informações
        return {
            "disk_info": disk_info,
            "has_alert": has_alert,
            "highest_alert": highest_alert,
            "email_sent": email_sent,
            "timestamp": datetime.now().isoformat(),
        }


def check_disk_space() -> Dict[str, Any]:
    """
    Função de conveniência para verificar o espaço em disco.
    
    Returns:
        Dicionário com informações sobre o espaço em disco
    """
    monitor = DiskMonitor()
    return monitor.check_all_paths()


def monitor_and_alert() -> Dict[str, Any]:
    """
    Função de conveniência para verificar o espaço em disco e enviar alertas.
    
    Returns:
        Dicionário com informações sobre o espaço em disco e status do alerta
    """
    monitor = DiskMonitor()
    return monitor.check_and_alert()
