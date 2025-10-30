from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_security import login_user, login_required, current_user
from models.user import User
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test', methods=['GET'])
def test():
    """Endpoint de prueba simple"""
    return jsonify({
        'success': True,
        'message': 'Auth blueprint funcionando'
    })

@auth_bp.route('/test-password', methods=['POST'])
def test_password():
    """Endpoint de prueba para verificar contraseña"""
    try:
        data = request.get_json()
        email = data.get('email', 'test@test.com')
        password = data.get('password', 'test123')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            })
        
        password_check = check_password_hash(user.password, password)
        
        return jsonify({
            'success': True,
            'user_found': True,
            'password_match': password_check,
            'user_id': user.id,
            'user_email': user.email,
            'user_active': user.active,
            'user_confirmed': bool(user.confirmed_at)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de inicio de sesión simplificado"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        logger.info(f"🔐 Login intentado: {email}")
        
        # Buscar usuario usando SQLAlchemy directamente
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"❌ Usuario no encontrado: {email}")
            return jsonify({
                'success': False,
                'message': 'Credenciales inválidas'
            }), 401
        
        logger.info(f"✅ Usuario encontrado: {user.email} (ID: {user.id})")
        
        # Verificar contraseña
        if not check_password_hash(user.password, password):
            logger.warning(f"❌ Contraseña incorrecta para: {email}")
            return jsonify({
                'success': False,
                'message': 'Credenciales inválidas'
            }), 401
        
        logger.info(f"✅ Contraseña correcta para: {email}")
        
        # Verificar si el usuario está activo
        if not user.active:
            logger.warning(f"❌ Usuario inactivo: {email}")
            return jsonify({
                'success': False,
                'message': 'Cuenta desactivada. Contacta al administrador.'
            }), 401
        
        # Verificar si el usuario está confirmado
        if not user.confirmed_at:
            logger.warning(f"❌ Usuario no confirmado: {email}")
            return jsonify({
                'success': False,
                'message': 'Debes confirmar tu email antes de iniciar sesión.',
                'requires_confirmation': True
            }), 401
        
        # Obtener roles del usuario usando SQLAlchemy
        roles = []
        try:
            roles = [role.name for role in user.roles]
            logger.info(f"✅ Roles obtenidos: {roles}")
        except Exception as e:
            logger.warning(f"⚠️  Error obteniendo roles: {e}")
        
        # IMPORTANTE: Establecer la sesión del usuario con Flask-Security
        login_user(user, remember=True)
        logger.info(f"✅ Sesión establecida para: {email}")
        
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
        
        logger.info(f"🎉 Login exitoso para: {email}")
        return jsonify(login_response)
        
    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Obtener información del usuario actual autenticado"""
    try:
        if not current_user.is_authenticated:
            logger.warning("❌ Usuario no autenticado intentando acceder a /me")
            return jsonify({
                'success': False,
                'message': 'No autenticado'
            }), 401
        
        # Obtener roles del usuario
        roles = []
        try:
            roles = [role.name for role in current_user.roles]
        except Exception as e:
            logger.warning(f"⚠️  Error obteniendo roles: {e}")
        
        user_data = {
            "success": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "active": current_user.active,
                "confirmed_at": current_user.confirmed_at.isoformat() if current_user.confirmed_at else None
            },
            "roles": roles
        }
        
        logger.info(f"✅ Información de usuario actual obtenida: {current_user.email}")
        return jsonify(user_data)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuario actual: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500