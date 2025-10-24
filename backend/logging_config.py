"""
Configuración de logging estructurado para Team Time Management
Incluye rotación de logs, diferentes niveles y contexto estructurado
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
import json
from flask import request, g, has_request_context

class StructuredFormatter(logging.Formatter):
    """Formateador personalizado para logs estructurados"""
    
    def format(self, record):
        # Crear estructura base del log
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Añadir contexto de request si está disponible
        if has_request_context():
            log_entry['request'] = {
                'method': request.method,
                'url': request.url,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'endpoint': request.endpoint
            }
            
            # Añadir información del usuario si está disponible
            if hasattr(g, 'user') and g.user:
                log_entry['user'] = {
                    'id': g.user.id,
                    'email': g.user.email,
                    'roles': [role.name for role in g.user.roles]
                }
        
        # Añadir campos adicionales del record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Añadir información de excepción si existe
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, ensure_ascii=False)

class ContextualLogger:
    """Logger contextual que añade información adicional automáticamente"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log_with_context(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log con contexto adicional"""
        extra = {}
        if extra_fields:
            extra['extra_fields'] = extra_fields
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log de debug con contexto"""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de información con contexto"""
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de advertencia con contexto"""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de error con contexto"""
        self._log_with_context(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico con contexto"""
        self._log_with_context(logging.CRITICAL, message, kwargs)

def setup_logging(app):
    """Configura el sistema de logging para la aplicación"""
    
    # Obtener configuración
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_dir = app.config.get('LOG_DIR', 'logs')
    
    # Crear directorio de logs si no existe
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar nivel de logging
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    app.logger.handlers.clear()
    
    # Configurar formateador estructurado
    structured_formatter = StructuredFormatter()
    
    # Handler para archivo principal con rotación
    main_log_file = os.path.join(log_dir, 'team_time_management.log')
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(structured_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para errores separado
    error_log_file = os.path.join(log_dir, 'errors.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setFormatter(structured_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Handler para consola (solo en desarrollo)
    if app.config.get('DEBUG', False):
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    # Añadir handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    
    # Configurar loggers específicos
    configure_specific_loggers(log_dir, structured_formatter)
    
    # Log de inicio
    app.logger.info("Sistema de logging inicializado", extra_fields={
        'log_level': log_level,
        'log_dir': log_dir,
        'handlers': ['file', 'error_file'] + (['console'] if app.config.get('DEBUG') else [])
    })

def configure_specific_loggers(log_dir: str, formatter: StructuredFormatter):
    """Configura loggers específicos para diferentes componentes"""
    
    # Logger para autenticación
    auth_logger = logging.getLogger('team_time.auth')
    auth_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'auth.log'),
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    auth_handler.setFormatter(formatter)
    auth_logger.addHandler(auth_handler)
    auth_logger.setLevel(logging.INFO)
    
    # Logger para emails
    email_logger = logging.getLogger('team_time.email')
    email_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'email.log'),
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    email_handler.setFormatter(formatter)
    email_logger.addHandler(email_handler)
    email_logger.setLevel(logging.INFO)
    
    # Logger para base de datos
    db_logger = logging.getLogger('team_time.database')
    db_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'database.log'),
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    db_handler.setFormatter(formatter)
    db_logger.addHandler(db_handler)
    db_logger.setLevel(logging.WARNING)
    
    # Logger para APIs externas
    api_logger = logging.getLogger('team_time.external_api')
    api_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'external_api.log'),
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    api_handler.setFormatter(formatter)
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)

def get_logger(name: str) -> ContextualLogger:
    """Obtiene un logger contextual para un módulo específico"""
    return ContextualLogger(f'team_time.{name}')

def log_user_action(user_id: int, action: str, details: Optional[Dict[str, Any]] = None):
    """Log específico para acciones de usuario"""
    logger = get_logger('user_actions')
    logger.info(f"Acción de usuario: {action}", 
                user_id=user_id,
                action=action,
                details=details or {})

def log_security_event(event_type: str, details: Optional[Dict[str, Any]] = None):
    """Log específico para eventos de seguridad"""
    logger = get_logger('security')
    logger.warning(f"Evento de seguridad: {event_type}",
                   event_type=event_type,
                   details=details or {})

def log_performance_metric(metric_name: str, value: float, unit: str = 'ms'):
    """Log específico para métricas de rendimiento"""
    logger = get_logger('performance')
    logger.info(f"Métrica de rendimiento: {metric_name}",
                metric_name=metric_name,
                value=value,
                unit=unit)

def log_business_event(event_type: str, details: Optional[Dict[str, Any]] = None):
    """Log específico para eventos de negocio"""
    logger = get_logger('business')
    logger.info(f"Evento de negocio: {event_type}",
                event_type=event_type,
                details=details or {})

# Configuración específica para diferentes entornos
class LoggingConfig:
    """Configuración de logging por entorno"""
    
    @staticmethod
    def development():
        """Configuración para desarrollo"""
        return {
            'LOG_LEVEL': 'DEBUG',
            'LOG_DIR': 'logs',
            'CONSOLE_OUTPUT': True,
            'FILE_ROTATION': True
        }
    
    @staticmethod
    def production():
        """Configuración para producción"""
        return {
            'LOG_LEVEL': 'INFO',
            'LOG_DIR': '/var/log/team_time_management',
            'CONSOLE_OUTPUT': False,
            'FILE_ROTATION': True,
            'MAX_FILE_SIZE': 50*1024*1024,  # 50MB
            'BACKUP_COUNT': 10
        }
    
    @staticmethod
    def testing():
        """Configuración para testing"""
        return {
            'LOG_LEVEL': 'WARNING',
            'LOG_DIR': 'test_logs',
            'CONSOLE_OUTPUT': False,
            'FILE_ROTATION': False
        }
