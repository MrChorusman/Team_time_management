"""
Gestor unificado de conexiones a base de datos
"""
import os
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, text, pool
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool, QueuePool
import psycopg2
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor unificado de conexiones a base de datos"""
    
    def __init__(self, config: 'AppConfig'):
        """
        Inicializa el gestor de base de datos
        
        Args:
            config: Instancia de AppConfig con la configuración
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._engine = None
        self._connection_url = None
        
    def get_connection_url(self, connection_type: str = 'auto') -> str:
        """
        Construye la URL de conexión según el tipo
        
        Args:
            connection_type: 'auto', 'pooler', 'direct'
                - 'auto': Decide basado en el entorno
                - 'pooler': Fuerza Transaction Pooler (puerto 6543)
                - 'direct': Fuerza conexión directa (puerto 5432)
                
        Returns:
            URL de conexión PostgreSQL
        """
        # Si ya tenemos una URL cacheada, usarla
        if self._connection_url and connection_type == 'auto':
            return self._connection_url
        
        # Primero intentar obtener DATABASE_URL completa
        database_url = self.config.get('DATABASE_URL')
        if database_url:
            self.logger.info("Usando DATABASE_URL desde variables de entorno")
            self._connection_url = database_url
            return database_url
        
        # Determinar tipo de conexión basado en entorno
        if connection_type == 'auto':
            if self.config.is_production():
                connection_type = 'pooler'
            else:
                connection_type = 'direct'
        
        # Construir URL según el tipo
        if connection_type == 'pooler':
            url = self._build_pooler_url()
        else:
            url = self._build_direct_url()
        
        self._connection_url = url
        return url
    
    def _build_pooler_url(self) -> str:
        """Construye URL para Transaction Pooler (producción)"""
        host = self.config.get('SUPABASE_HOST')
        port = self.config.get('SUPABASE_PORT', '6543')  # Por defecto pooler
        user = self.config.get('SUPABASE_USER')
        password = self.config.get('SUPABASE_DB_PASSWORD')
        database = self.config.get('SUPABASE_DB', 'postgres')
        
        if not all([host, user, password]):
            raise ValueError("Faltan credenciales de Supabase para construir URL")
        
        # Verificar si el puerto es realmente de pooler
        if port == '5432':
            self.logger.warning("Puerto 5432 configurado pero se solicitó pooler. Cambiando a 6543")
            port = '6543'
        
        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.logger.info(f"URL de pooler construida para host: {host}:{port}")
        
        return url
    
    def _build_direct_url(self) -> str:
        """Construye URL para conexión directa (desarrollo)"""
        host = self.config.get('SUPABASE_HOST')
        port = self.config.get('SUPABASE_PORT', '5432')  # Por defecto directo
        user = self.config.get('SUPABASE_USER')
        password = self.config.get('SUPABASE_DB_PASSWORD')
        database = self.config.get('SUPABASE_DB', 'postgres')
        
        if not all([host, user, password]):
            raise ValueError("Faltan credenciales de Supabase para construir URL")
        
        # Verificar si el puerto es realmente directo
        if port == '6543':
            self.logger.warning("Puerto 6543 configurado pero se solicitó directo. Cambiando a 5432")
            port = '5432'
        
        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.logger.info(f"URL directa construida para host: {host}:{port}")
        
        return url
    
    def get_engine(self, **kwargs) -> Engine:
        """
        Obtiene o crea el engine de SQLAlchemy
        
        Args:
            **kwargs: Argumentos adicionales para create_engine
            
        Returns:
            Engine de SQLAlchemy
        """
        if self._engine is None:
            self._engine = self._create_engine(**kwargs)
        return self._engine
    
    def _create_engine(self, **kwargs) -> Engine:
        """Crea un nuevo engine de SQLAlchemy con configuración optimizada"""
        url = self.get_connection_url()
        
        # Configuración base del engine
        engine_config = {
            'pool_pre_ping': True,  # Verificar conexiones antes de usar
            'pool_recycle': 300,    # Reciclar conexiones cada 5 minutos
        }
        
        # Configuración específica según entorno
        if self.config.is_production():
            # En producción con pooler, usar NullPool
            engine_config.update({
                'poolclass': NullPool,
                'connect_args': {
                    'connect_timeout': 10,
                    'options': '-c statement_timeout=30000'  # 30 segundos
                }
            })
        else:
            # En desarrollo, usar pool normal
            engine_config.update({
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
            })
        
        # Combinar con kwargs proporcionados
        engine_config.update(kwargs)
        
        self.logger.info(f"Creando engine con configuración: {engine_config}")
        
        try:
            engine = create_engine(url, **engine_config)
            self.logger.info("Engine creado exitosamente")
            return engine
        except Exception as e:
            self.logger.error(f"Error creando engine: {e}")
            raise
    
    def validate_connection(self, connection_type: str = 'auto') -> Tuple[bool, str]:
        """
        Valida que la conexión funcione
        
        Args:
            connection_type: Tipo de conexión a validar
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            url = self.get_connection_url(connection_type)
            
            # Crear engine temporal para prueba
            test_engine = create_engine(url, poolclass=NullPool)
            
            with test_engine.connect() as conn:
                # Ejecutar consultas de prueba
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                
                result = conn.execute(text("SELECT current_database()"))
                db_name = result.fetchone()[0]
                
                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
                table_count = result.fetchone()[0]
                
            test_engine.dispose()
            
            message = f"Conexión exitosa. PostgreSQL {version.split()[1]}, Base de datos: {db_name}, Tablas: {table_count}"
            self.logger.info(message)
            
            return True, message
            
        except Exception as e:
            message = f"Error de conexión: {str(e)}"
            self.logger.error(message)
            return False, message
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de salud de todas las conexiones
        
        Returns:
            Diccionario con estado de salud
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.config.environment,
            'connections': {}
        }
        
        # Probar conexión actual
        success, message = self.validate_connection()
        status['connections']['current'] = {
            'healthy': success,
            'message': message,
            'type': 'pooler' if self.config.is_production() else 'direct'
        }
        
        # Si estamos en desarrollo, también probar pooler
        if self.config.is_development():
            success_pooler, message_pooler = self.validate_connection('pooler')
            status['connections']['pooler_test'] = {
                'healthy': success_pooler,
                'message': message_pooler,
                'type': 'pooler'
            }
        
        # Información adicional
        status['config'] = {
            'host': self.config.get('SUPABASE_HOST'),
            'port': self.config.get('SUPABASE_PORT'),
            'database': self.config.get('SUPABASE_DB', 'postgres'),
            'user': self.config.get('SUPABASE_USER')
        }
        
        return status
    
    def execute_query(self, query: str, params: Dict = None) -> Any:
        """
        Ejecuta una consulta SQL
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            
        Returns:
            Resultado de la consulta
        """
        engine = self.get_engine()
        
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            
            # Si es SELECT, retornar resultados
            if result.returns_rows:
                return result.fetchall()
            
            # Si es INSERT/UPDATE/DELETE, retornar rowcount
            return result.rowcount
    
    def test_supabase_features(self) -> Dict[str, bool]:
        """
        Prueba características específicas de Supabase
        
        Returns:
            Diccionario con el estado de cada característica
        """
        features = {}
        engine = self.get_engine()
        
        with engine.connect() as conn:
            # Verificar extensiones de Supabase
            try:
                result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pgjwt')"))
                extensions = [row[0] for row in result]
                features['uuid-ossp'] = 'uuid-ossp' in extensions
                features['pgcrypto'] = 'pgcrypto' in extensions
                features['pgjwt'] = 'pgjwt' in extensions
            except:
                features['extensions_check'] = False
            
            # Verificar RLS (Row Level Security)
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM pg_policies"))
                features['rls_enabled'] = result.fetchone()[0] > 0
            except:
                features['rls_enabled'] = False
            
            # Verificar realtime
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'realtime'"))
                features['realtime_enabled'] = result.fetchone()[0] > 0
            except:
                features['realtime_enabled'] = False
        
        return features
    
    def close(self):
        """Cierra el engine y libera recursos"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self.logger.info("Engine cerrado y recursos liberados")
