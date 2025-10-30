import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de base de datos
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Para desarrollo local, usar PostgreSQL local si está disponible
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
                  f'postgresql://postgres:postgres@localhost:5432/team_time_management'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Configuración de Flask-Security-Too
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'super-secret-salt'
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    
    # URLs de redirección
    SECURITY_POST_LOGIN_REDIRECT_ENDPOINT = 'main.dashboard'
    SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT = 'main.index'
    SECURITY_POST_REGISTER_REDIRECT_ENDPOINT = 'main.verify_email'
    
    # Configuración de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Configuración de Redis para sesiones y caché
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'team_time:'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # APIs externas
    NAGER_DATE_API_URL = 'https://date.nager.at/api/v3'
    
    # Configuración de paginación
    EMPLOYEES_PER_PAGE = 20
    HOLIDAYS_PER_PAGE = 50
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    
    # Base de datos local para desarrollo
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'postgresql://postgres:postgres@localhost:5432/team_time_management'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Desactivar CSRF para tests
    WTF_CSRF_ENABLED = False
    SECURITY_CSRF_PROTECT_MECHANISMS = []
    
    # Email de prueba
    MAIL_SUPPRESS_SEND = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # Usar Supabase en producción
    SQLALCHEMY_DATABASE_URI = f'postgresql://postgres:{os.environ.get("SUPABASE_DB_PASSWORD")}@{os.environ.get("SUPABASE_HOST")}/postgres'
    
    # Configuración de seguridad adicional para cookies cross-origin
    SESSION_COOKIE_SECURE = True  # HTTPS requerido
    SESSION_COOKIE_HTTPONLY = True  # No accesible desde JavaScript
    SESSION_COOKIE_SAMESITE = 'None'  # CRÍTICO: Permitir cookies cross-origin (Vercel -> Render)

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
