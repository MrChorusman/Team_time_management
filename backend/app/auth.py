from flask import Blueprint, request, jsonify, current_app, redirect, session
from flask_security import login_user, logout_user, current_user, auth_required
from flask_security.utils import hash_password
from werkzeug.security import check_password_hash
import logging

from models.user import User, Role, db
from services.google_oauth_service import GoogleOAuthService

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de inicio de sesión"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({
                'success': False,
                'message': 'Credenciales inválidas'
            }), 401
        
        if not user.active:
            return jsonify({
                'success': False,
                'message': 'Cuenta desactivada. Contacta al administrador.'
            }), 401
        
        if not user.confirmed_at:
            return jsonify({
                'success': False,
                'message': 'Debes confirmar tu email antes de iniciar sesión.',
                'requires_confirmation': True
            }), 401
        
        # Iniciar sesión
        login_user(user, remember=True)
        
        # Obtener información del empleado si existe
        employee_data = None
        if user.employee:
            employee_data = user.employee.to_dict()
        
        logger.info(f"Usuario {email} inició sesión exitosamente")
        
        return jsonify({
            'success': True,
            'message': 'Inicio de sesión exitoso',
            'user': user.to_dict(),
            'employee': employee_data,
            'redirect_url': '/dashboard' if user.employee and user.employee.approved else '/employee/register'
        })
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint de registro de usuario"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Validaciones básicas
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Ya existe una cuenta con este email'
            }), 409
        
        # Crear nuevo usuario
        viewer_role = Role.query.filter_by(name='viewer').first()
        if not viewer_role:
            return jsonify({
                'success': False,
                'message': 'Error de configuración del sistema'
            }), 500
        
        new_user = User(
            email=email,
            password=hash_password(password),
            active=True,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        new_user.roles.append(viewer_role)
        
        db.session.add(new_user)
        db.session.commit()
        
        # TODO: Enviar email de confirmación
        # Por ahora, confirmar automáticamente para desarrollo
        new_user.confirmed_at = db.func.now()
        db.session.commit()
        
        logger.info(f"Nuevo usuario registrado: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Registro exitoso. Ya puedes iniciar sesión.',
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en registro: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@auth_required()
def logout():
    """Endpoint de cierre de sesión"""
    try:
        user_email = current_user.email
        logout_user()
        
        logger.info(f"Usuario {user_email} cerró sesión")
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return jsonify({
            'success': False,
            'message': 'Error cerrando sesión'
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Obtiene información del usuario actual.
    NO requiere @auth_required() para poder devolver respuesta apropiada cuando no hay sesión.
    """
    try:
        if current_user.is_authenticated:
            employee_data = None
            if hasattr(current_user, 'employee') and current_user.employee:
                employee_data = current_user.employee.to_dict(include_summary=True)
            
            user_dict = current_user.to_dict()
            
            return jsonify({
                'success': True,
                'user': user_dict,
                'employee': employee_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No hay sesión activa'
            }), 401
            
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        return jsonify({
            'success': False,
            'message': 'Error verificando sesión'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@auth_required()
def change_password():
    """Cambia la contraseña del usuario actual"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Contraseña actual y nueva contraseña son requeridas'
            }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verificar contraseña actual
        if not verify_password(current_password, current_user.password):
            return jsonify({
                'success': False,
                'message': 'Contraseña actual incorrecta'
            }), 401
        
        # Validar nueva contraseña
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'La nueva contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Actualizar contraseña
        current_user.password = hash_password(new_password)
        db.session.commit()
        
        logger.info(f"Usuario {current_user.email} cambió su contraseña")
        
        return jsonify({
            'success': True,
            'message': 'Contraseña actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cambiando contraseña: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando contraseña'
        }), 500

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """
    DEPRECATED: Usar /auth/me en su lugar.
    Verifica si hay una sesión activa (mantenido por compatibilidad)
    """
    try:
        if current_user.is_authenticated:
            employee_data = None
            if current_user.employee:
                employee_data = current_user.employee.to_dict()
            
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': current_user.to_dict(),
                'employee': employee_data
            })
        else:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'No hay sesión activa'
            }), 401
            
    except Exception as e:
        logger.error(f"Error verificando sesión: {e}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': 'Error verificando sesión'
        }), 500

@auth_bp.route('/roles', methods=['GET'])
@auth_required()
def get_roles():
    """Obtiene la lista de roles disponibles (solo para admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        roles = Role.query.all()
        
        return jsonify({
            'success': True,
            'roles': [
                {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description
                }
                for role in roles
            ]
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo roles: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo roles'
        }), 500

# ===========================================
# GOOGLE OAUTH ENDPOINTS
# ===========================================

@auth_bp.route('/google/url', methods=['GET'])
def google_auth_url():
    """Obtiene la URL de autorización de Google"""
    try:
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        if not google_oauth.is_configured():
            return jsonify({
                'success': False,
                'message': 'Google OAuth no está configurado'
            }), 400
        
        auth_url = google_oauth.get_auth_url()
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        })
        
    except Exception as e:
        logger.error(f"Error generando URL de Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error generando URL de autorización'
        }), 500

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Maneja el callback de Google OAuth"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code or not state:
            return jsonify({
                'success': False,
                'message': 'Código de autorización o estado faltante'
            }), 400
        
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        success, message, user_data = google_oauth.handle_callback(code, state)
        
        if success and user_data:
            # Buscar el usuario en la base de datos
            user = User.query.filter_by(email=user_data['email']).first()
            
            if user:
                # Iniciar sesión
                login_user(user, remember=True)
                
                # Obtener información del empleado si existe
                employee_data = None
                if user.employee:
                    employee_data = user.employee.to_dict()
                
                logger.info(f"Usuario {user.email} inició sesión con Google OAuth")
                
                return jsonify({
                    'success': True,
                    'message': 'Autenticación con Google exitosa',
                    'user': user.to_dict(),
                    'employee': employee_data,
                    'redirect_url': '/dashboard' if user.employee and user.employee.approved else '/employee/register'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado después de la autenticación'
                }), 404
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error en callback de Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error en autenticación con Google'
        }), 500

@auth_bp.route('/google/config', methods=['GET'])
def google_config():
    """Obtiene la configuración de Google OAuth (solo para verificar si está configurado)"""
    try:
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        return jsonify({
            'success': True,
            'configured': google_oauth.is_configured(),
            'client_id': current_app.config.get('GOOGLE_CLIENT_ID', '').split('.')[0] + '...' if current_app.config.get('GOOGLE_CLIENT_ID') else None,
            'redirect_uri': current_app.config.get('GOOGLE_REDIRECT_URI')
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración de Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo configuración'
        }), 500

@auth_bp.route('/google/disconnect', methods=['POST'])
@auth_required()
def google_disconnect():
    """Desconecta la cuenta de Google del usuario actual"""
    try:
        # En una implementación completa, aquí se revocaría el token
        # y se eliminarían los datos de Google del usuario
        
        logger.info(f"Usuario {current_user.email} desconectó su cuenta de Google")
        
        return jsonify({
            'success': True,
            'message': 'Cuenta de Google desconectada exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error desconectando Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error desconectando cuenta de Google'
        }), 500
