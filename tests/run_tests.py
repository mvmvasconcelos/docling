#!/usr/bin/env python
"""
Script para executar os testes do projeto.
"""

import os
import sys
import unittest
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


def run_tests(test_type=None, verbose=False):
    """
    Executa os testes do projeto.
    
    Args:
        test_type: Tipo de teste a ser executado (unit, integration, all)
        verbose: Se True, exibe informações detalhadas sobre os testes
    """
    # Configurar o nível de verbosidade
    verbosity = 2 if verbose else 1
    
    # Descobrir e executar os testes
    if test_type == "unit":
        print("Executando testes unitários...")
        test_suite = unittest.defaultTestLoader.discover(
            start_dir=os.path.dirname(__file__),
            pattern="test_*_extractor.py"
        )
    elif test_type == "integration":
        print("Executando testes de integração...")
        test_suite = unittest.defaultTestLoader.discover(
            start_dir=os.path.dirname(__file__),
            pattern="test_api_integration.py"
        )
    else:  # all
        print("Executando todos os testes...")
        test_suite = unittest.defaultTestLoader.discover(
            start_dir=os.path.dirname(__file__),
            pattern="test_*.py"
        )
    
    # Executar os testes
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)
    
    # Retornar código de saída
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Executa os testes do projeto.")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all"],
        default="all",
        help="Tipo de teste a ser executado (unit, integration, all)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe informações detalhadas sobre os testes"
    )
    
    # Analisar argumentos
    args = parser.parse_args()
    
    # Executar testes
    sys.exit(run_tests(args.type, args.verbose))
