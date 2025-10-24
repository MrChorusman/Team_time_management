from flask import Blueprint, request, jsonify, current_app, redirect, session
from flask_security import login_user, logout_user, current_user, auth_required
from flask_security.utils import hash_password
from werkzeug.security import check_password_hash
import logging
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from models.user import User, Role, db
from services.google_oauth_service import GoogleOAuthService

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def get_supabase_config():
    """Obtener configuración de Supabase según el entorno"""
    
    # Detectar entorno
    environment = os.environ.get('FLASK_ENV', 'development')
    
    if environment == 'production':
        # Configuración de PRODUCCIÓN
        return {
            'url': os.environ.get('SUPABASE_URL'),
            'key': os.environ.get('SUPABASE_KEY'),
            'env': 'production'
        }
    else:
        # Configuración de DESARROLLO
        return {
            'url': os.environ.get('SUPABASE_URL', 'https://qsbvoyjqfrhaqncqtknv.supabase.co'),
            'key': os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k'),
            'env': 'development'
        }

def get_headers():
    """Obtener headers para Supabase"""
    config = get_supabase_config()
    return {
        'apikey': config['key'],
        'Authorization': f"Bearer {config['key']}",
        'Content-Type': 'application/json'
    }

@auth_bp.route('/test-db', methods=['GET'])
def test_db():
    """Endpoint de prueba para verificar conexión a base de datos"""
    try:
        # Probar consulta simple
        user_count = User.query.count()
        return jsonify({
            'success': True,
            'message': 'Conexión a base de datos exitosa',
            'user_count': user_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en base de datos: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de inicio de sesión usando SQLAlchemy directamente"""
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
        
        # Por ahora, no usar Flask-Security para evitar problemas
        # login_user(user, remember=True)
        
        logger.info(f"🎉 Login exitoso para: {email}")
        return jsonify(login_response)
        
    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/me', methods=['GET'])
def me():
    """Endpoint para verificar sesión actual"""
    try:
        # Por ahora, como no tenemos sistema de sesiones implementado,
        # devolvemos que no hay sesión activa
        # TODO: Implementar sistema de sesiones con JWT o cookies
        return jsonify({
            "success": False,
            "message": "Sesión no encontrada"
        }), 401
    except Exception as e:
        logger.error(f"Error en /me: {e}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint de cierre de sesión"""
    try:
        logout_user()
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        })
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return jsonify({
            'success': False,
            'message': 'Error al cerrar sesión'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint de registro de usuarios"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Verificar si el usuario ya existe
        config = get_supabase_config()
        headers = get_headers()
        
        response = requests.get(
            f"{config['url']}/rest/v1/user?email=eq.{email}",
            headers=headers
        )
        
        if response.status_code == 200 and response.json():
            return jsonify({
                'success': False,
                'message': 'El email ya está registrado'
            }), 400
        
        # Crear nuevo usuario
        hashed_password = hash_password(password)
        
        new_user = {
            'email': email,
            'password': hashed_password,
            'first_name': first_name,
            'last_name': last_name,
            'active': True,
            'confirmed_at': None  # Requiere confirmación
        }
        
        response = requests.post(
            f"{config['url']}/rest/v1/user",
            headers=headers,
            json=new_user
        )
        
        if response.status_code == 201:
            return jsonify({
                'success': True,
                'message': 'Usuario registrado exitosamente. Revisa tu email para confirmar la cuenta.'
            })
        else:
            logger.error(f"Error creando usuario: {response.status_code}")
            return jsonify({
                'success': False,
                'message': 'Error al crear el usuario'
            }), 500
            
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """Endpoint de autenticación con Google"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token de Google requerido'
            }), 400
        
        # Usar el servicio de Google OAuth
        google_service = GoogleOAuthService()
        user_info = google_service.get_user_info_from_token(token)
        
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Token de Google inválido'
            }), 401
        
        # Buscar o crear usuario
        config = get_supabase_config()
        headers = get_headers()
        
        response = requests.get(
            f"{config['url']}/rest/v1/user?email=eq.{user_info['email']}",
            headers=headers
        )
        
        if response.status_code == 200:
            users = response.json()
            if users:
                user = users[0]
            else:
                # Crear nuevo usuario
                new_user = {
                    'email': user_info['email'],
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                    'active': True,
                    'confirmed_at': user_info.get('email_verified', False)
                }
                
                response = requests.post(
                    f"{config['url']}/rest/v1/user",
                    headers=headers,
                    json=new_user
                )
                
                if response.status_code == 201:
                    user = response.json()[0]
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Error al crear usuario'
                    }), 500
        
        return jsonify({
            'success': True,
            'message': 'Autenticación con Google exitosa',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'active': user['active'],
                'confirmed_at': user.get('confirmed_at')
            },
            'redirectUrl': '/dashboard'
        })
        
    except Exception as e:
        logger.error(f"Error en autenticación Google: {e}")
        return jsonify({
            'success': False,
            'message': 'Error en autenticación con Google'
        }), 500
