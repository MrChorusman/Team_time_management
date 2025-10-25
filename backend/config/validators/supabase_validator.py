"""
Validador de configuración de Supabase
"""
import os
import re
import logging
from typing import Tuple, List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SupabaseValidator:
    """Validador de configuración de Supabase"""
    
    # Patrones válidos para hosts de Supabase
    VALID_HOST_PATTERNS = [
        r'^db\.[a-z0-9]+\.supabase\.co$',  # Conexión directa
        r'^aws-\d+-[a-z]+-[a-z]+-\d+\.pooler\.supabase\.com$',  # Transaction Pooler
    ]
    
    # Puertos válidos
    VALID_PORTS = {
        'direct': ['5432', '6543'],  # 5432 es el estándar, 6543 también se usa
        'pooler': ['6543', '5432'],  # 6543 es para pooler, pero algunos usan 5432
    }
    
    # Proyectos de Supabase conocidos (extraídos del análisis)
    KNOWN_PROJECTS = {
        'qsbvoyjqfrhaqncqtknv': 'desarrollo',
        'xmaxohyxgsthligskjvg': 'producción'
    }
    
    @classmethod
    def validate_environment_config(cls, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida que la configuración tenga todos los campos necesarios
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            Tupla (es_válida, lista_de_errores)
        """
        errors = []
        
        # Campos requeridos
        required_fields = [
            'SUPABASE_HOST',
            'SUPABASE_USER',
            'SUPABASE_DB_PASSWORD',
            'SUPABASE_DB'
        ]
        
        # Verificar campos requeridos
        for field in required_fields:
            if not config.get(field):
                errors.append(f"Campo requerido faltante: {field}")
        
        # Si faltan campos básicos, no continuar
        if errors:
            return False, errors
        
        # Validaciones específicas
        host_errors = cls._validate_host(config.get('SUPABASE_HOST'))
        errors.extend(host_errors)
        
        port_errors = cls._validate_port(config.get('SUPABASE_PORT'), config.get('SUPABASE_HOST'))
        errors.extend(port_errors)
        
        user_errors = cls._validate_user(config.get('SUPABASE_USER'))
        errors.extend(user_errors)
        
        url_errors = cls._validate_urls(config)
        errors.extend(url_errors)
        
        return len(errors) == 0, errors
    
    @classmethod
    def _validate_host(cls, host: str) -> List[str]:
        """Valida el formato del host"""
        errors = []
        
        if not host:
            return ["Host vacío"]
        
        # Verificar si coincide con algún patrón válido
        valid = False
        for pattern in cls.VALID_HOST_PATTERNS:
            if re.match(pattern, host):
                valid = True
                break
        
        if not valid:
            errors.append(f"Host inválido: {host}. Debe ser db.*.supabase.co o aws-*.pooler.supabase.com")
        
        return errors
    
    @classmethod
    def _validate_port(cls, port: str, host: str) -> List[str]:
        """Valida el puerto según el tipo de host"""
        errors = []
        
        if not port:
            errors.append("Puerto no especificado")
            return errors
        
        # Determinar tipo de conexión por el host
        if host and 'pooler' in host:
            valid_ports = cls.VALID_PORTS['pooler']
            conn_type = 'pooler'
        else:
            valid_ports = cls.VALID_PORTS['direct']
            conn_type = 'direct'
        
        if port not in valid_ports:
            errors.append(f"Puerto {port} no es válido para conexión {conn_type}. Use: {', '.join(valid_ports)}")
        
        # Advertencias
        if conn_type == 'pooler' and port == '5432':
            logger.warning("Puerto 5432 con host pooler. Normalmente se usa 6543 para pooler")
        elif conn_type == 'direct' and port == '6543':
            logger.warning("Puerto 6543 con host directo. Normalmente se usa 5432 para conexión directa")
        
        return errors
    
    @classmethod
    def _validate_user(cls, user: str) -> List[str]:
        """Valida el formato del usuario"""
        errors = []
        
        if not user:
            return ["Usuario vacío"]
        
        # Patrón esperado: postgres o postgres.proyecto
        if not re.match(r'^postgres(\.[a-z0-9]+)?$', user):
            errors.append(f"Usuario inválido: {user}. Debe ser 'postgres' o 'postgres.proyecto'")
        
        # Extraer proyecto si existe
        if '.' in user:
            project = user.split('.')[1]
            if project not in cls.KNOWN_PROJECTS:
                logger.warning(f"Proyecto desconocido en usuario: {project}")
        
        return errors
    
    @classmethod
    def _validate_urls(cls, config: Dict[str, Any]) -> List[str]:
        """Valida las URLs de Supabase si están presentes"""
        errors = []
        
        # Validar SUPABASE_URL si existe
        supabase_url = config.get('SUPABASE_URL')
        if supabase_url:
            try:
                parsed = urlparse(supabase_url)
                if parsed.scheme != 'https':
                    errors.append(f"SUPABASE_URL debe usar HTTPS, encontrado: {parsed.scheme}")
                
                # Extraer proyecto de la URL
                if parsed.hostname:
                    project = parsed.hostname.split('.')[0]
                    if project not in cls.KNOWN_PROJECTS:
                        logger.warning(f"Proyecto desconocido en URL: {project}")
                        
            except Exception as e:
                errors.append(f"SUPABASE_URL inválida: {str(e)}")
        
        return errors
    
    @classmethod
    def validate_connection_string(cls, connection_string: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Valida una cadena de conexión PostgreSQL
        
        Args:
            connection_string: URL de conexión PostgreSQL
            
        Returns:
            Tupla (es_válida, detalles)
        """
        details = {
            'valid': False,
            'components': {},
            'errors': []
        }
        
        try:
            # Parsear URL
            parsed = urlparse(connection_string)
            
            if parsed.scheme != 'postgresql':
                details['errors'].append(f"Esquema inválido: {parsed.scheme}, debe ser 'postgresql'")
                return False, details
            
            # Extraer componentes
            details['components'] = {
                'scheme': parsed.scheme,
                'user': parsed.username,
                'password': '***' if parsed.password else None,
                'host': parsed.hostname,
                'port': parsed.port,
                'database': parsed.path.lstrip('/') if parsed.path else None
            }
            
            # Validar componentes
            if not parsed.hostname:
                details['errors'].append("Host faltante en la URL")
            else:
                host_errors = cls._validate_host(parsed.hostname)
                details['errors'].extend(host_errors)
            
            if not parsed.username:
                details['errors'].append("Usuario faltante en la URL")
            
            if not parsed.password:
                details['errors'].append("Contraseña faltante en la URL")
            
            if not parsed.port:
                details['errors'].append("Puerto faltante en la URL")
            else:
                port_errors = cls._validate_port(str(parsed.port), parsed.hostname)
                details['errors'].extend(port_errors)
            
            details['valid'] = len(details['errors']) == 0
            
        except Exception as e:
            details['errors'].append(f"Error parseando URL: {str(e)}")
        
        return details['valid'], details
    
    @classmethod
    def suggest_fixes(cls, config: Dict[str, Any]) -> List[str]:
        """
        Sugiere correcciones para problemas comunes
        
        Args:
            config: Configuración actual
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        host = config.get('SUPABASE_HOST', '')
        port = config.get('SUPABASE_PORT', '')
        
        # Sugerir cambio de puerto según host
        if 'pooler' in host and port == '5432':
            suggestions.append("Cambiar SUPABASE_PORT a 6543 para usar Transaction Pooler correctamente")
        elif 'db.' in host and port == '6543':
            suggestions.append("Cambiar SUPABASE_PORT a 5432 para conexión directa")
        
        # Sugerir host correcto según puerto
        if port == '6543' and 'db.' in host:
            suggestions.append("Para puerto 6543, use un host pooler: aws-*.pooler.supabase.com")
        elif port == '5432' and 'pooler' in host:
            suggestions.append("Para puerto 5432, use conexión directa: db.*.supabase.co")
        
        # Verificar consistencia entre URL y componentes
        supabase_url = config.get('SUPABASE_URL', '')
        if supabase_url:
            # Extraer proyecto de URL
            try:
                parsed = urlparse(supabase_url)
                if parsed.hostname:
                    url_project = parsed.hostname.split('.')[0]
                    
                    # Verificar si el usuario corresponde al proyecto
                    user = config.get('SUPABASE_USER', '')
                    if '.' in user:
                        user_project = user.split('.')[1]
                        if url_project != user_project:
                            suggestions.append(f"El proyecto en SUPABASE_URL ({url_project}) no coincide con el usuario ({user_project})")
            except:
                pass
        
        return suggestions
    
    @classmethod
    def get_connection_type(cls, config: Dict[str, Any]) -> str:
        """
        Determina el tipo de conexión basado en la configuración
        
        Args:
            config: Configuración
            
        Returns:
            'pooler', 'direct' o 'unknown'
        """
        host = config.get('SUPABASE_HOST', '')
        port = config.get('SUPABASE_PORT', '')
        
        if 'pooler' in host or port == '6543':
            return 'pooler'
        elif 'db.' in host or port == '5432':
            return 'direct'
        else:
            return 'unknown'
