import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore
from datetime import datetime
import logging

# Importar configuración desde app_config (evita conflicto con directorio config/)
import app_config as config_module
config = config_module.config

# Importar modelos
from models import db, User, Role
from models.employee import Employee
from models.team import Team
from models.holiday import Holiday
from models.calendar_activity import CalendarActivity
from models.notification import Notification
from models.location import Country, AutonomousCommunity, Province, City

# Importar servicios
from services.email_service import EmailService
from services.holiday_service import HolidayService
from services.notification_service import NotificationService

# Importar configuración de logging
from logging_config import setup_logging, get_logger

# Importar blueprints (rutas)
from app.auth import auth_bp
from auth_simple import auth_simple_bp
from app.employees import employees_bp
from app.teams import teams_bp
from app.calendar import calendar_bp
from app.holidays import holidays_bp
from app.notifications import notifications_bp
from app.reports import reports_bp
from app.admin import admin_bp
from app.locations import locations_bp
from app.invitations import invitations_bp
from app.forecast import forecast_bp
from app.projects import projects_bp

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    # Crear aplicación
    app = Flask(__name__)
    
    # Configuración - Detectar automáticamente el entorno
    if config_name is None:
        # Si hay RENDER o SUPABASE_HOST, asumir producción
        if os.environ.get('RENDER') or os.environ.get('SUPABASE_HOST'):
            config_name = 'production'
        else:
            config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Log de configuración cargada
    logger = get_logger('config')
    logger.info(f"Configuración cargada: {config_name}")
    logger.info(f"Base de datos: {app.config.get('SQLALCHEMY_DATABASE_URI', 'No configurada')[:50]}...")
    
    # Configurar logging estructurado
    setup_logging(app)
    
    # Inicializar extensiones
    db.init_app(app)
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Configuración de sesiones para cross-domain (Vercel → Render)
    is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER')
    app.config['SESSION_COOKIE_SECURE'] = is_production  # Solo HTTPS en producción
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # No accesible desde JavaScript
    app.config['SESSION_COOKIE_SAMESITE'] = 'None' if is_production else 'Lax'  # Cross-domain en producción
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Permitir cross-domain
    
    # Configurar Flask-Mail
    mail = Mail(app)
    
    # Configurar Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    
    # Configurar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Auto-migraciones mínimas y seguras (idempotentes)
    with app.app_context():
        try:
            from sqlalchemy import inspect, text
            engine = db.get_engine()
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('notification')]
            if 'data' not in columns:
                # Crear columna 'data' para notificaciones (JSON/JSONB según dialecto)
                dialect = engine.url.get_dialect().name
                if dialect == 'postgresql':
                    engine.execute(text("ALTER TABLE notification ADD COLUMN data JSONB"))
                else:
                    # Fallback genérico
                    engine.execute(text("ALTER TABLE notification ADD COLUMN data JSON"))
                get_logger('migrations').info("Columna 'notification.data' creada automáticamente")

            # Verificar columna manager_id en team
            team_columns = [col['name'] for col in inspector.get_columns('team')]
            if 'manager_id' not in team_columns:
                engine.execute(text("ALTER TABLE team ADD COLUMN manager_id INTEGER"))
                # Intentar crear FK si existe tabla employee
                try:
                    engine.execute(text("ALTER TABLE team ADD CONSTRAINT fk_team_manager_id FOREIGN KEY (manager_id) REFERENCES employee(id)"))
                except Exception as _:
                    pass
                get_logger('migrations').info("Columna 'team.manager_id' creada automáticamente")
        except Exception as e:
            # No bloquear el arranque si falla; se registrará para diagnóstico
            get_logger('migrations').error(f"Auto-migración fallida: {e}")

    # Inicializar servicios
    # Importar el singleton global y inicializarlo
    from services.email_service import email_service
    email_service.init_app(app)
    
    # Guardar email_service en app para acceso global
    app.email_service = email_service
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(auth_simple_bp, url_prefix='/api/auth-simple')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(holidays_bp, url_prefix='/api/holidays')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')
    app.register_blueprint(invitations_bp)
    app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    
    # Dashboard stats endpoint
    from app.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # Employee invitations ahora están en employees_bp
    
    # Rutas principales
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Team Time Management API',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # DEBUG: Endpoint temporal para verificar config SMTP
    @app.route('/api/debug/email-config', methods=['GET'])
    def debug_email_config():
        import os
        
        mock_mode = os.environ.get('MOCK_EMAIL_MODE', 'NOT SET')
        mail_username = os.environ.get('MAIL_USERNAME')
        mail_password = os.environ.get('MAIL_PASSWORD')
        
        email_configured = all([mail_username, mail_password])
        mock_mode_bool = mock_mode.lower() in ['true', 'on', '1'] if mock_mode != 'NOT SET' else False
        should_use_mock = mock_mode_bool or not email_configured
        
        return jsonify({
            'MOCK_EMAIL_MODE': mock_mode,
            'MOCK_EMAIL_MODE_bool': mock_mode_bool,
            'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'NOT SET'),
            'MAIL_PORT': os.environ.get('MAIL_PORT', 'NOT SET'),
            'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'NOT SET'),
            'MAIL_USERNAME': 'SET' if mail_username else 'NOT SET',
            'MAIL_PASSWORD': 'SET (hidden)' if mail_password else 'NOT SET',
            'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'NOT SET'),
            'email_configured': email_configured,
            'should_use_mock_email': should_use_mock,
            'app_config_should_use_mock_email': app.config.get('should_use_mock_email')
        }), 200
    
    # DEBUG: Test SendGrid Web API
    @app.route('/api/debug/test-sendgrid-api', methods=['GET'])
    def test_sendgrid_api():
        """Test completo de SendGrid Web API"""
        import os
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'steps': []
        }
        
        try:
            # Paso 1: Verificar que sendgrid esté instalado
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail as SendGridMail, Email, To, Content
                results['steps'].append({'step': 'import_sendgrid', 'status': 'ok'})
            except ImportError as e:
                results['steps'].append({'step': 'import_sendgrid', 'status': 'error', 'error': str(e)})
                results['overall_status'] = 'import_error'
                return jsonify(results), 500
            
            # Paso 2: Verificar API key
            api_key = os.environ.get('MAIL_PASSWORD')
            if not api_key:
                results['steps'].append({'step': 'api_key', 'status': 'error', 'error': 'MAIL_PASSWORD no configurada'})
                results['overall_status'] = 'config_error'
                return jsonify(results), 500
            
            if not api_key.startswith('SG.'):
                results['steps'].append({'step': 'api_key', 'status': 'error', 'error': 'MAIL_PASSWORD no es una API key de SendGrid'})
                results['overall_status'] = 'config_error'
                return jsonify(results), 500
            
            results['steps'].append({'step': 'api_key', 'status': 'ok', 'key_preview': api_key[:10] + '...'})
            
            # Paso 3: Crear mensaje
            from_email = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@teamtime.com')
            to_email = 'miguelchis@gmail.com'
            
            message = SendGridMail(
                from_email=Email(from_email),
                to_emails=To(to_email),
                subject='Test desde Team Time Management',
                plain_text_content=Content("text/plain", "Este es un email de prueba"),
                html_content=Content("text/html", "<p>Este es un email de prueba</p>")
            )
            results['steps'].append({'step': 'create_message', 'status': 'ok', 'from': from_email, 'to': to_email})
            
            # Paso 4: Enviar
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            results['steps'].append({
                'step': 'send_email',
                'status': 'ok',
                'status_code': response.status_code,
                'body': response.body,
                'headers': dict(response.headers)
            })
            
            results['overall_status'] = 'success'
            results['message'] = f'Email enviado con status {response.status_code}'
            
            return jsonify(results), 200
            
        except Exception as e:
            import traceback
            results['overall_status'] = 'error'
            results['error'] = str(e)
            results['traceback'] = traceback.format_exc()
            return jsonify(results), 500
    
    # DEBUG: Test conexión SMTP rápido
    @app.route('/api/debug/test-smtp', methods=['GET'])
    def test_smtp_connection():
        import smtplib
        import os
        import time
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'tests': []
        }
        
        try:
            # Test 1: Conectar a SendGrid
            start = time.time()
            server = smtplib.SMTP(os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net'), 
                                 int(os.environ.get('MAIL_PORT', 587)), 
                                 timeout=10)
            elapsed = time.time() - start
            results['tests'].append({'step': 'connect', 'status': 'ok', 'time_ms': int(elapsed * 1000)})
            
            # Test 2: STARTTLS
            start = time.time()
            server.starttls()
            elapsed = time.time() - start
            results['tests'].append({'step': 'starttls', 'status': 'ok', 'time_ms': int(elapsed * 1000)})
            
            # Test 3: Login
            start = time.time()
            server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
            elapsed = time.time() - start
            results['tests'].append({'step': 'login', 'status': 'ok', 'time_ms': int(elapsed * 1000)})
            
            server.quit()
            results['overall_status'] = 'success'
            results['message'] = 'Conexión SMTP exitosa'
            
        except smtplib.SMTPException as e:
            results['overall_status'] = 'smtp_error'
            results['error'] = str(e)
        except Exception as e:
            results['overall_status'] = 'error'
            results['error'] = str(e)
        
        return jsonify(results), 200
    
    @app.route('/api/auth/login-main', methods=['POST'])
    def login_main():
        """Endpoint de login directamente en main.py para pruebas"""
        try:
            from flask import request
            from werkzeug.security import check_password_hash
            from models.user import User
            
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({
                    'success': False,
                    'message': 'Email y contraseña son requeridos'
                }), 400
            
            email = data['email'].lower().strip()
            password = data['password']
            
            # Buscar usuario usando SQLAlchemy directamente
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Credenciales inválidas'
                }), 401
            
            # Verificar contraseña
            if not check_password_hash(user.password, password):
                return jsonify({
                    'success': False,
                    'message': 'Credenciales inválidas'
                }), 401
            
            # Verificar si el usuario está activo
            if not user.active:
                return jsonify({
                    'success': False,
                    'message': 'Cuenta desactivada. Contacta al administrador.'
                }), 401
            
            # Verificar si el usuario está confirmado
            if not user.confirmed_at:
                return jsonify({
                    'success': False,
                    'message': 'Debes confirmar tu email antes de iniciar sesión.',
                    'requires_confirmation': True
                }), 401
            
            # Obtener roles del usuario usando SQLAlchemy
            roles = []
            try:
                roles = [role.name for role in user.roles]
            except Exception as e:
                pass
            
            # Respuesta exitosa
            login_response = {
                "success": True,
                "message": "Inicio de sesión exitoso",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "active": user.active,
                    "confirmed_at": user.confirmed_at.isoformat() if user.confirmed_at else None
                },
                "roles": roles,
                "redirectUrl": "/dashboard"
            }
            
            return jsonify(login_response)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @app.route('/api/auth-simple/test-main', methods=['GET'])
    def test_auth_simple_main():
        """Endpoint de prueba para auth-simple en main.py"""
        return jsonify({
            'success': True,
            'message': 'Auth-simple endpoint en main.py funcionando'
        })
    
    @app.route('/api/auth/test-main', methods=['GET'])
    def test_auth_main():
        """Endpoint de prueba en main.py"""
        return jsonify({
            'success': True,
            'message': 'Endpoint de prueba en main.py funcionando'
        })
    
    @app.route('/api/health')
    def health_check():
        """Endpoint de salud del sistema con diagnóstico detallado"""
        import os
        import psycopg2
        try:
            import psutil
            HAS_PSUTIL = True
        except ImportError:
            HAS_PSUTIL = False
        import app_config as config_module
        config = config_module.config
        
        logger = get_logger('health')
        
        # Información básica del sistema
        health_info = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.1',
            'environment': os.environ.get('FLASK_ENV', 'unknown'),
            'diagnostics': {}
        }
        
        # Verificar variables de entorno (detectar desarrollo vs producción)
        env_mode = os.environ.get('FLASK_ENV', 'unknown')
        is_dev = env_mode == 'development'
        
        if is_dev:
            # En desarrollo, usar variables SUPABASE_DEV_*
            env_vars = {
                'SUPABASE_HOST': os.environ.get('SUPABASE_DEV_HOST'),
                'SUPABASE_PORT': os.environ.get('SUPABASE_DEV_PORT'),
                'SUPABASE_DB': os.environ.get('SUPABASE_DEV_DB'),
                'SUPABASE_USER': os.environ.get('SUPABASE_DEV_USER'),
                'SUPABASE_DB_PASSWORD': '***' if os.environ.get('SUPABASE_DEV_DB_PASSWORD') else None
            }
        else:
            # En producción, usar variables SUPABASE_*
            env_vars = {
                'SUPABASE_HOST': os.environ.get('SUPABASE_HOST'),
                'SUPABASE_PORT': os.environ.get('SUPABASE_PORT'),
                'SUPABASE_DB': os.environ.get('SUPABASE_DB'),
                'SUPABASE_USER': os.environ.get('SUPABASE_USER'),
                'SUPABASE_DB_PASSWORD': '***' if os.environ.get('SUPABASE_DB_PASSWORD') else None
            }
        
        health_info['diagnostics']['environment_variables'] = env_vars
        
        # Verificar conexión SQLAlchemy
        try:
            db.session.execute(db.text('SELECT 1'))
            health_info['diagnostics']['sqlalchemy'] = 'healthy'
        except Exception as e:
            health_info['diagnostics']['sqlalchemy'] = f'error: {str(e)}'
        
        # Verificar conexión directa con psycopg2
        try:
            # Detectar entorno y leer variables correctas
            if is_dev:
                host = os.environ.get('SUPABASE_DEV_HOST')
                port = os.environ.get('SUPABASE_DEV_PORT')
                db_name = os.environ.get('SUPABASE_DEV_DB')
                user = os.environ.get('SUPABASE_DEV_USER')
                password = os.environ.get('SUPABASE_DEV_DB_PASSWORD')
            else:
                host = os.environ.get('SUPABASE_HOST')
                port = os.environ.get('SUPABASE_PORT')
                db_name = os.environ.get('SUPABASE_DB')
                user = os.environ.get('SUPABASE_USER')
                password = os.environ.get('SUPABASE_DB_PASSWORD')
            
            if all([host, port, db_name, user, password]):
                connection_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
                conn = psycopg2.connect(connection_url)
                cursor = conn.cursor()
                cursor.execute("SELECT current_user, current_database(), version();")
                current_user, current_db, version = cursor.fetchone()
                cursor.close()
                conn.close()
                
                health_info['diagnostics']['psycopg2'] = {
                    'status': 'healthy',
                    'current_user': current_user,
                    'current_database': current_db,
                    'postgresql_version': version
                }
            else:
                health_info['diagnostics']['psycopg2'] = 'error: Missing environment variables'
                
        except Exception as e:
            health_info['diagnostics']['psycopg2'] = f'error: {str(e)}'
        
        # Verificar servicios externos
        try:
            # Verificar Google OAuth
            google_oauth_status = 'configured' if app.config.get('google_oauth_configured') else 'not_configured'
            health_info['diagnostics']['google_oauth'] = {
                'status': google_oauth_status,
                'mock_mode': app.config.get('google_oauth_mock_mode', False)
            }
            
            # Verificar configuración de email
            email_status = 'configured' if app.config.get('email_configured') else 'not_configured'
            health_info['diagnostics']['email'] = {
                'status': email_status,
                'mock_mode': app.config.get('should_use_mock_email', False)
            }
            
        except Exception as e:
            health_info['diagnostics']['external_services'] = f'error: {str(e)}'
        
        # Verificar recursos del sistema
        try:
            if HAS_PSUTIL:
                # Uso de memoria
                memory = psutil.virtual_memory()
                health_info['diagnostics']['system_resources'] = {
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent_used': memory.percent
                    },
                    'cpu_percent': psutil.cpu_percent(interval=1)
                }
            else:
                health_info['diagnostics']['system_resources'] = 'not available (psutil not installed)'
        except Exception as e:
            health_info['diagnostics']['system_resources'] = f'error: {str(e)}'
        
        # Verificar configuración de logging
        try:
            log_level = app.config.get('LOG_LEVEL', 'INFO')
            health_info['diagnostics']['logging'] = {
                'level': log_level,
                'configured': True
            }
        except Exception as e:
            health_info['diagnostics']['logging'] = f'error: {str(e)}'
        
        # Determinar estado general
        critical_services = ['sqlalchemy', 'psycopg2']
        healthy_services = 0
        
        for service in critical_services:
            if service in health_info['diagnostics']:
                if service == 'sqlalchemy' and health_info['diagnostics'][service] == 'healthy':
                    healthy_services += 1
                elif service == 'psycopg2' and isinstance(health_info['diagnostics'][service], dict) and health_info['diagnostics'][service].get('status') == 'healthy':
                    healthy_services += 1
        
        if healthy_services == len(critical_services):
            health_info['status'] = 'healthy'
        elif healthy_services > 0:
            health_info['status'] = 'degraded'
        
        # Log del health check
        logger.info("Health check ejecutado", 
                   status=health_info['status'],
                   healthy_services=healthy_services,
                   total_services=len(critical_services))
        
        return jsonify(health_info)
    
    @app.route('/api/info')
    def app_info():
        """Información de la aplicación"""
        return jsonify({
            'name': 'Team Time Management',
            'version': '1.0.0',
            'description': 'Sistema completo de gestión de horarios empresariales',
            'features': [
                'Gestión global de empleados',
                'Sistema automático de festivos',
                'Calendario interactivo',
                'Notificaciones inteligentes',
                'Reportes y análisis',
                'Exportación de datos'
            ],
            'supported_countries': len(HolidayService.SUPPORTED_COUNTRIES),
            'api_endpoints': {
                'auth': '/api/auth',
                'employees': '/api/employees',
                'teams': '/api/teams',
                'calendar': '/api/calendar',
                'holidays': '/api/holidays',
                'notifications': '/api/notifications',
                'reports': '/api/reports',
                'admin': '/api/admin'
            }
        })
    
    # Manejadores de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint no encontrado',
            'message': 'La ruta solicitada no existe',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ha ocurrido un error inesperado',
            'status_code': 500
        }), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Acceso denegado',
            'message': 'No tienes permisos para acceder a este recurso',
            'status_code': 403
        }), 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'No autorizado',
            'message': 'Debes iniciar sesión para acceder a este recurso',
            'status_code': 401
        }), 401
    
    # Comandos CLI personalizados
    @app.cli.command()
    def init_db():
        """Inicializa la base de datos"""
        db.create_all()
        
        # Crear roles por defecto
        if not Role.query.first():
            roles = [
                Role(name='admin', description='Administrador del sistema'),
                Role(name='manager', description='Gestor de equipo'),
                Role(name='employee', description='Empleado estándar'),
                Role(name='viewer', description='Usuario temporal')
            ]
            
            for role in roles:
                db.session.add(role)
            
            db.session.commit()
            print("Roles creados exitosamente")
        
        print("Base de datos inicializada")
    
    @app.cli.command()
    def create_admin():
        """Crea un usuario administrador"""
        from flask_security.utils import hash_password
        
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("Error: Rol admin no encontrado. Ejecuta 'flask init-db' primero.")
            return
        
        # Verificar si ya existe un admin
        existing_admin = User.query.filter(User.roles.contains(admin_role)).first()
        if existing_admin:
            print(f"Ya existe un administrador: {existing_admin.email}")
            return
        
        email = input("Email del administrador: ")
        password = input("Contraseña: ")
        
        admin_user = User(
            email=email,
            password=hash_password(password),
            active=True,
            confirmed_at=datetime.utcnow()
        )
        
        admin_user.roles.append(admin_role)
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Administrador creado: {email}")
    
    @app.cli.command()
    def load_holidays():
        """Carga festivos automáticamente (deprecated - usar update-holidays)"""
        holiday_service = HolidayService()
        results = holiday_service.auto_load_missing_holidays()
        
        print(f"Festivos cargados: {results['total_holidays_loaded']}")
        print(f"Países procesados: {len(results['processed_countries'])}")
        
        if results['errors']:
            print("Errores encontrados:")
            for error in results['errors'][:5]:  # Mostrar solo los primeros 5
                print(f"  - {error}")
    
    # Registrar comando de actualización de festivos
    from commands.update_holidays import init_app as init_update_holidays_cmd
    init_update_holidays_cmd(app)
    
    @app.cli.command()
    def process_notifications():
        """Procesa la cola de notificaciones pendientes"""
        results = NotificationService.process_notification_queue()
        
        print(f"Notificaciones procesadas: {results['processed']}")
        print(f"Emails enviados: {results['sent']}")
        print(f"Errores: {results['failed']}")
        
        if results['errors']:
            print("Errores encontrados:")
            for error in results['errors'][:3]:
                print(f"  - {error}")
    
    # Contexto de aplicación
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Role': Role,
            'Employee': Employee,
            'Team': Team,
            'Holiday': Holiday,
            'CalendarActivity': CalendarActivity,
            'Notification': Notification,
            'HolidayService': HolidayService,
            'NotificationService': NotificationService
        }
    
    return app

# Crear aplicación
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )
