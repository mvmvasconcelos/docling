"""
Módulo para definição de políticas de retenção de arquivos temporários.

Este módulo define as políticas de retenção para diferentes tipos de arquivos temporários
no sistema Docling, incluindo uploads, arquivos de processamento intermediário e resultados.
"""

from typing import Dict, Any, List, Optional
import os
from datetime import timedelta

# Configurações padrão para políticas de retenção
DEFAULT_RETENTION_POLICIES = {
    # Arquivos de upload
    "uploads": {
        "max_age_days": 1,  # Manter por 1 dia
        "remove_after_processing": True,  # Remover após processamento bem-sucedido
        "exempt_extensions": [],  # Extensões que não devem ser removidas automaticamente
    },
    
    # Arquivos de processamento intermediário
    "temp_files": {
        "max_age_hours": 24,  # Manter por 24 horas
    },
    
    # Resultados de processamento
    "results": {
        "max_age_days": 30,  # Manter por 30 dias
        "consider_last_access": True,  # Considerar data do último acesso
        "exempt_tags": ["important", "permanent"],  # Tags que indicam que o resultado não deve ser removido
    }
}


class RetentionPolicy:
    """
    Classe para gerenciar políticas de retenção de arquivos temporários.
    """
    
    def __init__(self, custom_policies: Optional[Dict[str, Any]] = None):
        """
        Inicializa a política de retenção com configurações personalizadas.
        
        Args:
            custom_policies: Configurações personalizadas que substituem os valores padrão
        """
        self.policies = DEFAULT_RETENTION_POLICIES.copy()
        
        # Aplicar configurações personalizadas, se fornecidas
        if custom_policies:
            for category, settings in custom_policies.items():
                if category in self.policies:
                    self.policies[category].update(settings)
                else:
                    self.policies[category] = settings
    
    def get_upload_max_age(self) -> timedelta:
        """
        Retorna a idade máxima para arquivos de upload.
        
        Returns:
            Idade máxima como timedelta
        """
        days = self.policies["uploads"]["max_age_days"]
        return timedelta(days=days)
    
    def get_temp_files_max_age(self) -> timedelta:
        """
        Retorna a idade máxima para arquivos de processamento intermediário.
        
        Returns:
            Idade máxima como timedelta
        """
        hours = self.policies["temp_files"]["max_age_hours"]
        return timedelta(hours=hours)
    
    def get_results_max_age(self) -> timedelta:
        """
        Retorna a idade máxima para resultados de processamento.
        
        Returns:
            Idade máxima como timedelta
        """
        days = self.policies["results"]["max_age_days"]
        return timedelta(days=days)
    
    def should_remove_after_processing(self) -> bool:
        """
        Verifica se os arquivos de upload devem ser removidos após o processamento.
        
        Returns:
            True se os arquivos devem ser removidos, False caso contrário
        """
        return self.policies["uploads"]["remove_after_processing"]
    
    def is_extension_exempt(self, extension: str) -> bool:
        """
        Verifica se uma extensão de arquivo está isenta de remoção automática.
        
        Args:
            extension: Extensão do arquivo (com ou sem ponto)
            
        Returns:
            True se a extensão estiver isenta, False caso contrário
        """
        # Normalizar extensão (remover ponto inicial se presente)
        if extension.startswith("."):
            extension = extension[1:]
        
        return extension.lower() in [ext.lower() for ext in self.policies["uploads"]["exempt_extensions"]]
    
    def is_result_exempt(self, tags: List[str]) -> bool:
        """
        Verifica se um resultado está isento de remoção automática com base em suas tags.
        
        Args:
            tags: Lista de tags associadas ao resultado
            
        Returns:
            True se o resultado estiver isento, False caso contrário
        """
        exempt_tags = self.policies["results"]["exempt_tags"]
        return any(tag in exempt_tags for tag in tags)
    
    def should_consider_last_access(self) -> bool:
        """
        Verifica se a data do último acesso deve ser considerada para resultados.
        
        Returns:
            True se a data do último acesso deve ser considerada, False caso contrário
        """
        return self.policies["results"]["consider_last_access"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte as políticas de retenção para um dicionário.
        
        Returns:
            Dicionário com as políticas de retenção
        """
        return self.policies.copy()


# Instância global da política de retenção com configurações padrão
default_retention_policy = RetentionPolicy()


def load_retention_policy_from_env() -> RetentionPolicy:
    """
    Carrega a política de retenção a partir de variáveis de ambiente.
    
    Returns:
        Política de retenção configurada
    """
    custom_policies = {}
    
    # Carregar configurações de uploads
    uploads_max_age = os.getenv("RETENTION_UPLOADS_MAX_AGE_DAYS")
    if uploads_max_age and uploads_max_age.isdigit():
        if "uploads" not in custom_policies:
            custom_policies["uploads"] = {}
        custom_policies["uploads"]["max_age_days"] = int(uploads_max_age)
    
    # Carregar configurações de arquivos temporários
    temp_files_max_age = os.getenv("RETENTION_TEMP_FILES_MAX_AGE_HOURS")
    if temp_files_max_age and temp_files_max_age.isdigit():
        if "temp_files" not in custom_policies:
            custom_policies["temp_files"] = {}
        custom_policies["temp_files"]["max_age_hours"] = int(temp_files_max_age)
    
    # Carregar configurações de resultados
    results_max_age = os.getenv("RETENTION_RESULTS_MAX_AGE_DAYS")
    if results_max_age and results_max_age.isdigit():
        if "results" not in custom_policies:
            custom_policies["results"] = {}
        custom_policies["results"]["max_age_days"] = int(results_max_age)
    
    return RetentionPolicy(custom_policies)


# Carregar política de retenção a partir de variáveis de ambiente
retention_policy = load_retention_policy_from_env()
