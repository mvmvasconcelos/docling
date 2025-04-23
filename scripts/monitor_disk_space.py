#!/usr/bin/env python3
"""
Script para monitoramento de espaço em disco.

Este script verifica o espaço em disco disponível e envia alertas
quando o espaço estiver abaixo de limites configuráveis.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.disk_monitor import DiskMonitor
from app.utils.log_config import configure_logging


def setup_logging(verbose: bool = False) -> None:
    """
    Configura o sistema de logging.
    
    Args:
        verbose: Se True, configura o nível de log para DEBUG
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configurar logging
    configure_logging(
        log_file="disk_monitor.log",
        level=log_level,
        console=True,
        config={
            "format": "%(asctime)s [%(levelname)s] [DiskMonitor] %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
        },
    )


def parse_args() -> argparse.Namespace:
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        Argumentos analisados
    """
    parser = argparse.ArgumentParser(
        description="Monitora o espaço em disco e envia alertas",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Exibe informações detalhadas durante a execução",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Salva as informações em um arquivo JSON",
    )
    
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Desativa o envio de e-mails de alerta",
    )
    
    # Opções para personalizar limites de alerta
    thresholds_group = parser.add_argument_group("Limites de alerta")
    
    thresholds_group.add_argument(
        "--warning",
        type=int,
        help="Limite para alerta de aviso (porcentagem de espaço livre)",
    )
    
    thresholds_group.add_argument(
        "--critical",
        type=int,
        help="Limite para alerta crítico (porcentagem de espaço livre)",
    )
    
    thresholds_group.add_argument(
        "--emergency",
        type=int,
        help="Limite para alerta de emergência (porcentagem de espaço livre)",
    )
    
    # Opções para configuração de e-mail
    email_group = parser.add_argument_group("Configuração de e-mail")
    
    email_group.add_argument(
        "--smtp-server",
        type=str,
        help="Servidor SMTP para envio de e-mails",
    )
    
    email_group.add_argument(
        "--smtp-port",
        type=int,
        help="Porta do servidor SMTP",
    )
    
    email_group.add_argument(
        "--smtp-user",
        type=str,
        help="Usuário para autenticação SMTP",
    )
    
    email_group.add_argument(
        "--smtp-password",
        type=str,
        help="Senha para autenticação SMTP",
    )
    
    email_group.add_argument(
        "--from-email",
        type=str,
        help="Endereço de e-mail do remetente",
    )
    
    email_group.add_argument(
        "--to-emails",
        type=str,
        help="Endereços de e-mail dos destinatários (separados por vírgula)",
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Função principal do script.
    """
    # Analisar argumentos
    args = parse_args()
    
    # Configurar logging
    setup_logging(args.verbose)
    
    # Configurar limites personalizados
    thresholds = {}
    
    if args.warning is not None:
        thresholds["warning"] = args.warning
    
    if args.critical is not None:
        thresholds["critical"] = args.critical
    
    if args.emergency is not None:
        thresholds["emergency"] = args.emergency
    
    # Configurar e-mail
    email_config = {
        "enabled": not args.no_email,
    }
    
    if args.smtp_server:
        email_config["smtp_server"] = args.smtp_server
    
    if args.smtp_port:
        email_config["smtp_port"] = args.smtp_port
    
    if args.smtp_user:
        email_config["smtp_user"] = args.smtp_user
    
    if args.smtp_password:
        email_config["smtp_password"] = args.smtp_password
    
    if args.from_email:
        email_config["from_email"] = args.from_email
    
    if args.to_emails:
        email_config["to_emails"] = args.to_emails.split(",")
    
    # Criar monitor de disco
    monitor = DiskMonitor(
        thresholds=thresholds or None,
        email_config=email_config or None,
    )
    
    # Verificar espaço em disco e enviar alertas
    result = monitor.check_and_alert()
    
    # Exibir informações
    print("\n=== Informações de Espaço em Disco ===")
    
    for name, path_info in result["disk_info"].items():
        if "error" in path_info:
            print(f"{name.upper()}: Erro ao verificar espaço em disco: {path_info['error']}")
            continue
        
        alert_level = path_info.get("alert_level", "normal")
        if alert_level != "normal":
            alert_text = f"ALERTA: {alert_level.upper()}"
        else:
            alert_text = "OK"
        
        print(f"{name.upper()} ({path_info['path']}): {alert_text}")
        print(f"  Espaço livre: {path_info['free_gb']} GB ({path_info['free_percent']}%)")
        print(f"  Espaço total: {path_info['total_gb']} GB")
        print(f"  Espaço usado: {path_info['used_gb']} GB")
        print()
    
    # Exibir status de alerta
    if result["has_alert"]:
        print(f"Status de alerta: {result['highest_alert'].upper()}")
        print(f"E-mail enviado: {'Sim' if result['email_sent'] else 'Não'}")
        
        print("\nRecomendações:")
        print("1. Execute o script de limpeza de arquivos temporários: ./scripts/clean_temp_files.py")
        print("2. Verifique e remova arquivos grandes desnecessários")
        print("3. Considere aumentar o espaço em disco disponível")
    else:
        print("Status de alerta: OK")
    
    # Salvar informações em arquivo, se solicitado
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nInformações salvas em: {args.output}")
        except Exception as e:
            logging.error(f"Erro ao salvar informações: {str(e)}")


if __name__ == "__main__":
    main()
