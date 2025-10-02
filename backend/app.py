import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore
from datetime import datetime
import logging

# Importar configuración
from config import config

# Importar modelos
from models.user import db, User, Role
from models.employee import Employee
from models.team import Team
from models.holiday import Holiday
from models.calendar_activity import CalendarActivity
from models.notification import Notification

# Importar servicios
from services.email_service import EmailService
from services.holiday_service import HolidayService
from services.notification_service import NotificationService

# Importar blueprints (rutas)
from app.auth import auth_bp
from app.employees import employees_bp
from app.teams import teams_bp
from app.calendar import calendar_bp
from app.holidays import holidays_bp
from app.notifications import notifications_bp
from app.reports import reports_bp
from app.admin import admin_bp

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    # Crear aplicación
    app = Flask(__name__)
    
    # Configuración
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar extensiones
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configurar Flask-Mail
    mail = Mail(app)
    
    # Configurar Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    
    # Configurar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Inicializar servicios
    email_service = EmailService()
    email_service.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(holidays_bp, url_prefix='/api/holidays')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Rutas principales
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Team Time Management API',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/api/health')
    def health_check():
        """Endpoint de salud del sistema"""
        try:
            # Verificar conexión a base de datos
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
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
        """Carga festivos automáticamente"""
        holiday_service = HolidayService()
        results = holiday_service.auto_load_missing_holidays()
        
        print(f"Festivos cargados: {results['total_holidays_loaded']}")
        print(f"Países procesados: {len(results['processed_countries'])}")
        
        if results['errors']:
            print("Errores encontrados:")
            for error in results['errors'][:5]:  # Mostrar solo los primeros 5
                print(f"  - {error}")
    
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
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False)
    )
