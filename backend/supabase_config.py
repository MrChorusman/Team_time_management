# -*- coding: utf-8 -*-
"""
Configuración específica para Supabase PostgreSQL
Este archivo contiene la configuración para conectar con Supabase
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SupabaseConfig:
    """Configuración específica para Supabase"""
    
    # Información del proyecto Supabase
    PROJECT_URL = os.environ.get('SUPABASE_URL')
    SERVICE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Configuración de base de datos PostgreSQL
    DB_PASSWORD = os.environ.get('SUPABASE_DB_PASSWORD')
    DB_HOST = os.environ.get('SUPABASE_HOST', 'aws-0-eu-west-3.pooler.supabase.com')
    DB_PORT = os.environ.get('SUPABASE_PORT', '6543')
    DB_NAME = os.environ.get('SUPABASE_DB_NAME', 'postgres')
    DB_USER = os.environ.get('SUPABASE_DB_USER', 'postgres')
    
    @classmethod
    def get_database_url(cls):
        """Construye la URL de conexión a la base de datos"""
        if not cls.DB_PASSWORD:
            raise ValueError("SUPABASE_DB_PASSWORD no está configurado")
        
        # Usar variables de entorno directas si están disponibles
        db_password = os.environ.get('SUPABASE_DB_PASSWORD')
        db_host = os.environ.get('SUPABASE_HOST', cls.DB_HOST)
        db_port = os.environ.get('SUPABASE_PORT', cls.DB_PORT)
        db_name = os.environ.get('SUPABASE_DB_NAME', cls.DB_NAME)
        db_user = os.environ.get('SUPABASE_DB_USER', cls.DB_USER)
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @classmethod
    def is_configured(cls):
        """Verifica si la configuración de Supabase está completa"""
        required_vars = [
            cls.PROJECT_URL,
            cls.SERVICE_KEY,
            cls.DB_PASSWORD
        ]
        return all(var for var in required_vars)
    
    @classmethod
    def get_missing_vars(cls):
        """Retorna las variables de entorno faltantes"""
        missing = []
        if not cls.PROJECT_URL:
            missing.append('SUPABASE_URL')
        if not cls.SERVICE_KEY:
            missing.append('SUPABASE_KEY')
        if not cls.DB_PASSWORD:
            missing.append('SUPABASE_DB_PASSWORD')
        return missing

# Configuración de conexión a Supabase
SUPABASE_DATABASE_URL = SupabaseConfig.get_database_url() if SupabaseConfig.is_configured() else None
