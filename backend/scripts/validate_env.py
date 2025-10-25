"""
Script de validación de variables de entorno
Verifica que todas las variables necesarias estén configuradas correctamente
"""

import os
import sys
import re
import psycopg2
import smtplib
from urllib.parse import urlparse
from datetime import datetime

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EnvironmentValidator:
    """Validador de variables de entorno"""
    
    def __init__(self):
        self.results = {
            'overall_status': 'unknown',
            'checks': [],
            'summary': {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def add_check(self, name, status, message, details=None, critical=True):
        """Añade un resultado de verificación"""
        check = {
            'name': name,
            'status': status,  # 'passed', 'failed', 'warning'
            'message': message,
            'details': details,
            'critical': critical
        }
        
        self.results['checks'].append(check)
        self.results['summary']['total_checks'] += 1
        
        if status == 'passed':
            self.results['summary']['passed'] += 1
        elif status == 'failed':
            self.results['summary']['failed'] += 1
        elif status == 'warning':
            self.results['summary']['warnings'] += 1
    
    def validate_flask_config(self):
        """Valida configuración básica de Flask"""
        print("🔧 Validando configuración de Flask...")
        
        # SECRET_KEY
        secret_key = os.environ.get('SECRET_KEY')
        if secret_key and len(secret_key) >= 32:
            self.add_check(
                'SECRET_KEY',
                'passed',
                'SECRET_KEY configurado correctamente',
                {'length': len(secret_key)}
            )
        else:
            self.add_check(
                'SECRET_KEY',
                'failed',
                'SECRET_KEY no configurado o muy corto (mínimo 32 caracteres)',
                {'current_length': len(secret_key) if secret_key else 0}
            )
        
        # SECURITY_PASSWORD_SALT
        password_salt = os.environ.get('SECURITY_PASSWORD_SALT')
        if password_salt and len(password_salt) >= 16:
            self.add_check(
                'SECURITY_PASSWORD_SALT',
                'passed',
                'SECURITY_PASSWORD_SALT configurado correctamente',
                {'length': len(password_salt)}
            )
        else:
            self.add_check(
                'SECURITY_PASSWORD_SALT',
                'failed',
                'SECURITY_PASSWORD_SALT no configurado o muy corto (mínimo 16 caracteres)',
                {'current_length': len(password_salt) if password_salt else 0}
            )
        
        # FLASK_ENV
        flask_env = os.environ.get('FLASK_ENV', 'development')
        if flask_env in ['development', 'production', 'testing']:
            self.add_check(
                'FLASK_ENV',
                'passed',
                f'FLASK_ENV configurado como {flask_env}',
                {'environment': flask_env}
            )
        else:
            self.add_check(
                'FLASK_ENV',
                'warning',
                f'FLASK_ENV tiene un valor inusual: {flask_env}',
                {'environment': flask_env}
            )
    
    def validate_database_config(self):
        """Valida configuración de base de datos"""
        print("🗄️ Validando configuración de base de datos...")
        
        required_vars = [
            'SUPABASE_HOST',
            'SUPABASE_PORT',
            'SUPABASE_DB',
            'SUPABASE_USER',
            'SUPABASE_DB_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.add_check(
                'Database Variables',
                'failed',
                f'Variables de base de datos faltantes: {", ".join(missing_vars)}',
                {'missing_variables': missing_vars}
            )
            return
        
        # Validar formato de variables
        host = os.environ.get('SUPABASE_HOST')
        port = os.environ.get('SUPABASE_PORT')
        
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                raise ValueError("Puerto fuera de rango")
            
            self.add_check(
                'Database Port',
                'passed',
                f'Puerto de base de datos válido: {port}',
                {'port': port_int}
            )
        except ValueError:
            self.add_check(
                'Database Port',
                'failed',
                f'Puerto de base de datos inválido: {port}',
                {'port': port}
            )
        
        # Probar conexión a base de datos
        try:
            connection_url = f"postgresql://{os.environ.get('SUPABASE_USER')}:{os.environ.get('SUPABASE_DB_PASSWORD')}@{host}:{port}/{os.environ.get('SUPABASE_DB')}"
            conn = psycopg2.connect(connection_url)
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            self.add_check(
                'Database Connection',
                'passed',
                'Conexión a base de datos exitosa',
                {'postgresql_version': version.split()[1]}
            )
        except Exception as e:
            self.add_check(
                'Database Connection',
                'failed',
                f'Error conectando a base de datos: {str(e)}',
                {'error': str(e)}
            )
    
    def validate_google_oauth_config(self):
        """Valida configuración de Google OAuth"""
        print("🔐 Validando configuración de Google OAuth...")
        
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            self.add_check(
                'Google OAuth Variables',
                'failed',
                'Variables de Google OAuth faltantes',
                {
                    'GOOGLE_CLIENT_ID': bool(client_id),
                    'GOOGLE_CLIENT_SECRET': bool(client_secret),
                    'GOOGLE_REDIRECT_URI': bool(redirect_uri)
                }
            )
            return
        
        # Validar formato de CLIENT_ID
        if client_id.endswith('.apps.googleusercontent.com'):
            self.add_check(
                'Google Client ID Format',
                'passed',
                'Formato de CLIENT_ID válido',
                {'client_id_prefix': client_id.split('.')[0]}
            )
        else:
            self.add_check(
                'Google Client ID Format',
                'failed',
                'Formato de CLIENT_ID inválido (debe terminar en .apps.googleusercontent.com)',
                {'client_id': client_id}
            )
        
        # Validar formato de REDIRECT_URI
        try:
            parsed_uri = urlparse(redirect_uri)
            if parsed_uri.scheme in ['http', 'https'] and parsed_uri.netloc:
                self.add_check(
                    'Google Redirect URI',
                    'passed',
                    'Formato de REDIRECT_URI válido',
                    {'scheme': parsed_uri.scheme, 'host': parsed_uri.netloc}
                )
            else:
                self.add_check(
                    'Google Redirect URI',
                    'failed',
                    'Formato de REDIRECT_URI inválido',
                    {'redirect_uri': redirect_uri}
                )
        except Exception as e:
            self.add_check(
                'Google Redirect URI',
                'failed',
                f'Error validando REDIRECT_URI: {str(e)}',
                {'redirect_uri': redirect_uri}
            )
    
    def validate_email_config(self):
        """Valida configuración de email"""
        print("📧 Validando configuración de email...")
        
        mail_server = os.environ.get('MAIL_SERVER')
        mail_port = os.environ.get('MAIL_PORT')
        mail_username = os.environ.get('MAIL_USERNAME')
        mail_password = os.environ.get('MAIL_PASSWORD')
        
        if not all([mail_server, mail_port, mail_username, mail_password]):
            self.add_check(
                'Email Variables',
                'warning',
                'Variables de email no configuradas (modo mock activado)',
                {
                    'MAIL_SERVER': bool(mail_server),
                    'MAIL_PORT': bool(mail_port),
                    'MAIL_USERNAME': bool(mail_username),
                    'MAIL_PASSWORD': bool(mail_password)
                },
                critical=False
            )
            return
        
        # Validar puerto de email
        try:
            port_int = int(mail_port)
            if port_int in [25, 465, 587, 2525]:
                self.add_check(
                    'Email Port',
                    'passed',
                    f'Puerto de email válido: {mail_port}',
                    {'port': port_int}
                )
            else:
                self.add_check(
                    'Email Port',
                    'warning',
                    f'Puerto de email inusual: {mail_port}',
                    {'port': port_int}
                )
        except ValueError:
            self.add_check(
                'Email Port',
                'failed',
                f'Puerto de email inválido: {mail_port}',
                {'port': mail_port}
            )
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, mail_username):
            self.add_check(
                'Email Username',
                'passed',
                'Formato de email válido',
                {'email': mail_username}
            )
        else:
            self.add_check(
                'Email Username',
                'failed',
                'Formato de email inválido',
                {'email': mail_username}
            )
        
        # Probar conexión SMTP (opcional)
        try:
            if mail_server == 'smtp.gmail.com':
                server = smtplib.SMTP(mail_server, int(mail_port))
                server.starttls()
                # No intentamos login para evitar problemas de seguridad
                server.quit()
                
                self.add_check(
                    'SMTP Connection',
                    'passed',
                    'Conexión SMTP exitosa',
                    {'server': mail_server, 'port': mail_port}
                )
            else:
                self.add_check(
                    'SMTP Connection',
                    'warning',
                    'Servidor SMTP no estándar, conexión no probada',
                    {'server': mail_server, 'port': mail_port}
                )
        except Exception as e:
            self.add_check(
                'SMTP Connection',
                'warning',
                f'No se pudo probar conexión SMTP: {str(e)}',
                {'error': str(e)},
                critical=False
            )
    
    def validate_logging_config(self):
        """Valida configuración de logging"""
        print("📝 Validando configuración de logging...")
        
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        if log_level.upper() in valid_levels:
            self.add_check(
                'Log Level',
                'passed',
                f'Nivel de logging válido: {log_level}',
                {'level': log_level.upper()}
            )
        else:
            self.add_check(
                'Log Level',
                'warning',
                f'Nivel de logging inusual: {log_level}',
                {'level': log_level, 'valid_levels': valid_levels}
            )
    
    def validate_cors_config(self):
        """Valida configuración de CORS"""
        print("🌐 Validando configuración de CORS...")
        
        cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')
        
        try:
            origins = cors_origins.split(',')
            valid_origins = []
            
            for origin in origins:
                origin = origin.strip()
                parsed = urlparse(origin)
                if parsed.scheme in ['http', 'https'] and parsed.netloc:
                    valid_origins.append(origin)
            
            if valid_origins:
                self.add_check(
                    'CORS Origins',
                    'passed',
                    f'{len(valid_origins)} orígenes CORS válidos',
                    {'origins': valid_origins}
                )
            else:
                self.add_check(
                    'CORS Origins',
                    'failed',
                    'No se encontraron orígenes CORS válidos',
                    {'cors_origins': cors_origins}
                )
        except Exception as e:
            self.add_check(
                'CORS Origins',
                'failed',
                f'Error validando CORS: {str(e)}',
                {'cors_origins': cors_origins}
            )
    
    def validate_environment_specific(self):
        """Valida configuraciones específicas del entorno"""
        print("🏗️ Validando configuraciones específicas del entorno...")
        
        flask_env = os.environ.get('FLASK_ENV', 'development')
        
        if flask_env == 'production':
            # En producción, verificar que no estemos en modo debug
            debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower()
            if debug_mode == 'false':
                self.add_check(
                    'Production Debug Mode',
                    'passed',
                    'Modo debug deshabilitado en producción',
                    {'debug': False}
                )
            else:
                self.add_check(
                    'Production Debug Mode',
                    'failed',
                    'Modo debug habilitado en producción (riesgo de seguridad)',
                    {'debug': debug_mode}
                )
            
            # Verificar que tengamos configuración completa
            google_configured = all([
                os.environ.get('GOOGLE_CLIENT_ID'),
                os.environ.get('GOOGLE_CLIENT_SECRET'),
                os.environ.get('GOOGLE_REDIRECT_URI')
            ])
            
            if google_configured:
                self.add_check(
                    'Production Google OAuth',
                    'passed',
                    'Google OAuth configurado para producción',
                    {'configured': True}
                )
            else:
                self.add_check(
                    'Production Google OAuth',
                    'failed',
                    'Google OAuth no configurado en producción',
                    {'configured': False}
                )
        
        elif flask_env == 'development':
            # En desarrollo, verificar que tengamos configuración básica
            self.add_check(
                'Development Environment',
                'passed',
                'Entorno de desarrollo detectado',
                {'environment': 'development'}
            )
    
    def generate_report(self):
        """Genera reporte de validación"""
        print("\n" + "="*60)
        print("📊 REPORTE DE VALIDACIÓN DE VARIABLES DE ENTORNO")
        print("="*60)
        
        # Determinar estado general
        critical_failures = sum(1 for check in self.results['checks'] 
                               if check['status'] == 'failed' and check['critical'])
        
        if critical_failures == 0:
            self.results['overall_status'] = 'healthy'
            status_emoji = "✅"
            status_text = "SALUDABLE"
        elif critical_failures <= 2:
            self.results['overall_status'] = 'degraded'
            status_emoji = "⚠️"
            status_text = "DEGRADADO"
        else:
            self.results['overall_status'] = 'unhealthy'
            status_emoji = "❌"
            status_text = "NO SALUDABLE"
        
        print(f"\n{status_emoji} Estado General: {status_text}")
        print(f"📈 Resumen: {self.results['summary']['passed']} ✓ | {self.results['summary']['failed']} ❌ | {self.results['summary']['warnings']} ⚠️")
        
        # Mostrar checks por categoría
        print(f"\n📋 Detalles de Verificaciones:")
        print("-" * 60)
        
        for check in self.results['checks']:
            status_emoji = "✅" if check['status'] == 'passed' else "❌" if check['status'] == 'failed' else "⚠️"
            criticality = " [CRÍTICO]" if check['critical'] else ""
            
            print(f"{status_emoji} {check['name']}{criticality}")
            print(f"   {check['message']}")
            
            if check['details']:
                for key, value in check['details'].items():
                    print(f"   • {key}: {value}")
            print()
        
        # Recomendaciones
        print("💡 Recomendaciones:")
        print("-" * 60)
        
        failed_checks = [check for check in self.results['checks'] if check['status'] == 'failed']
        warning_checks = [check for check in self.results['checks'] if check['status'] == 'warning']
        
        if failed_checks:
            print("🔧 Acciones requeridas:")
            for check in failed_checks:
                print(f"   • {check['name']}: {check['message']}")
        
        if warning_checks:
            print("\n⚠️ Mejoras recomendadas:")
            for check in warning_checks:
                print(f"   • {check['name']}: {check['message']}")
        
        if not failed_checks and not warning_checks:
            print("🎉 ¡Todas las verificaciones pasaron correctamente!")
        
        print(f"\n🕒 Validación completada: {self.results['timestamp']}")
        print("="*60)
        
        return self.results
    
    def run_all_validations(self):
        """Ejecuta todas las validaciones"""
        print("🔍 Iniciando validación de variables de entorno...")
        print("="*60)
        
        self.validate_flask_config()
        self.validate_database_config()
        self.validate_google_oauth_config()
        self.validate_email_config()
        self.validate_logging_config()
        self.validate_cors_config()
        self.validate_environment_specific()
        
        return self.generate_report()

def main():
    """Función principal"""
    validator = EnvironmentValidator()
    results = validator.run_all_validations()
    
    # Código de salida basado en el estado
    if results['overall_status'] == 'healthy':
        sys.exit(0)
    elif results['overall_status'] == 'degraded':
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == '__main__':
    main()
