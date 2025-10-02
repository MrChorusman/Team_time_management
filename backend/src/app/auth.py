from flask import Blueprint, request, jsonify, current_app
from flask_security import login_user, logout_user, current_user, auth_required
from flask_security.utils import verify_password, hash_password
from werkzeug.security import check_password_hash
import logging

from models.user import User, Role, db

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
        
        if not user or not verify_password(password, user.password):
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
@auth_required()
def get_current_user():
    """Obtiene información del usuario actual"""
    try:
        employee_data = None
        if current_user.employee:
            employee_data = current_user.employee.to_dict(include_summary=True)
        
        return jsonify({
            'success': True,
            'user': current_user.to_dict(),
            'employee': employee_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo información del usuario'
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
    """Verifica si hay una sesión activa"""
    try:
        if current_user.is_authenticated:
            employee_data = None
            if current_user.employee:
                employee_data = current_user.employee.to_dict()
            
            return jsonify({
                'authenticated': True,
                'user': current_user.to_dict(),
                'employee': employee_data
            })
        else:
            return jsonify({
                'authenticated': False
            })
            
    except Exception as e:
        logger.error(f"Error verificando sesión: {e}")
        return jsonify({
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
