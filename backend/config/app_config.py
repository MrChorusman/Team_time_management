"""
Gestor centralizado de configuración de la aplicación
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class AppConfig:
    """Gestor centralizado de configuración"""
    
    def __init__(self, environment: str = None):
        """
        Inicializa el gestor de configuración
        
        Args:
            environment: Nombre del entorno ('development', 'staging', 'production')
                        Si no se especifica, se toma de APP_ENV o por defecto 'development'
        """
        self.environment = environment or os.getenv('APP_ENV', 'development')
        self.config_path = Path(__file__).parent / 'environments'
        self._config = {}
        self._env_loaded = False
        
        # Cargar configuración
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """Carga la configuración del entorno actual"""
        logger.info(f"Cargando configuración para entorno: {self.environment}")
        
        # 1. Cargar configuración base (compartida entre todos los entornos)
        base_config = self._load_json_config('base.json')
        if base_config:
            self._config.update(base_config)
            logger.debug(f"Configuración base cargada: {len(base_config)} valores")
        
        # 2. Cargar configuración específica del entorno
        env_config = self._load_json_config(f'{self.environment}.json')
        if env_config:
            self._config.update(env_config)
            logger.debug(f"Configuración de {self.environment} cargada: {len(env_config)} valores")
        
        # 3. Cargar variables de entorno desde archivo .env
        env_file = self.config_path / f'.env.{self.environment}'
        if env_file.exists():
            load_dotenv(env_file, override=True)
            self._env_loaded = True
            logger.info(f"Variables de entorno cargadas desde: {env_file}")
        else:
            logger.warning(f"Archivo de entorno no encontrado: {env_file}")
    
    def _load_json_config(self, filename: str) -> Dict:
        """Carga un archivo de configuración JSON"""
        config_file = self.config_path / filename
        
        if not config_file.exists():
            logger.debug(f"Archivo de configuración no encontrado: {config_file}")
            return {}
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON {config_file}: {e}")
            raise ValueError(f"Configuración JSON inválida en {filename}")
        except Exception as e:
            logger.error(f"Error leyendo {config_file}: {e}")
            raise
    
    def _validate_config(self):
        """Valida que la configuración tenga todos los campos requeridos"""
        # Definir campos requeridos por entorno
        required_fields = {
            'development': [
                'secret_key',
                'debug',
                'port'
            ],
            'production': [
                'secret_key',
                'debug',
                'port',
                'database_url'
            ]
        }
        
        # Obtener campos requeridos para el entorno actual
        env_requirements = required_fields.get(self.environment, [])
        missing = []
        
        for field in env_requirements:
            if not self.get(field):
                missing.append(field)
        
        if missing:
            logger.error(f"Configuración incompleta. Campos faltantes: {missing}")
            raise ValueError(f"Configuración incompleta para {self.environment}. Faltan: {missing}")
        
        logger.info(f"Configuración validada exitosamente para {self.environment}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración
        
        Orden de precedencia:
        1. Variable de entorno (mayúsculas)
        2. Configuración cargada desde JSON
        3. Valor por defecto
        
        Args:
            key: Clave de configuración (se convierte a mayúsculas para env vars)
            default: Valor por defecto si no se encuentra
            
        Returns:
            El valor de configuración o el default
        """
        # Primero buscar en variables de entorno
        env_key = key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Intentar convertir tipos básicos
            if env_value.lower() in ('true', 'false'):
                return env_value.lower() == 'true'
            try:
                # Intentar como número
                if '.' in env_value:
                    return float(env_value)
                return int(env_value)
            except ValueError:
                # Retornar como string
                return env_value
        
        # Luego en la configuración cargada
        return self._config.get(key, default)
    
    def get_nested(self, path: str, default: Any = None) -> Any:
        """
        Obtiene un valor anidado de la configuración
        
        Args:
            path: Ruta con puntos, ej: 'database.host'
            default: Valor por defecto
            
        Returns:
            El valor encontrado o el default
        """
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_database_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de base de datos"""
        # Primero intentar obtener DATABASE_URL completa
        database_url = self.get('DATABASE_URL')
        if database_url:
            return {'url': database_url}
        
        # Si no, construir desde componentes
        return {
            'host': self.get('SUPABASE_HOST'),
            'port': self.get('SUPABASE_PORT'),
            'database': self.get('SUPABASE_DB', 'postgres'),
            'user': self.get('SUPABASE_USER'),
            'password': self.get('SUPABASE_DB_PASSWORD')
        }
    
    def get_all(self) -> Dict[str, Any]:
        """Retorna toda la configuración (útil para debugging)"""
        # Combinar configuración cargada con variables de entorno relevantes
        all_config = self._config.copy()
        
        # Agregar variables de entorno relevantes
        for key in os.environ:
            if any(prefix in key for prefix in ['SUPABASE', 'FLASK', 'APP']):
                all_config[key.lower()] = os.environ[key]
        
        return all_config
    
    def is_production(self) -> bool:
        """Verifica si estamos en entorno de producción"""
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        """Verifica si estamos en entorno de desarrollo"""
        return self.environment == 'development'
    
    def __repr__(self):
        return f"<AppConfig environment='{self.environment}' loaded={self._env_loaded}>"


# Instancia singleton para uso global
_config_instance = None

def get_config(environment: str = None) -> AppConfig:
    """
    Obtiene la instancia de configuración (patrón singleton)
    
    Args:
        environment: Forzar un entorno específico (opcional)
        
    Returns:
        Instancia de AppConfig
    """
    global _config_instance
    
    if _config_instance is None or (environment and environment != _config_instance.environment):
        _config_instance = AppConfig(environment)
    
    return _config_instance
