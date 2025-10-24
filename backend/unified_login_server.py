#!/usr/bin/env python3
"""
Servidor de login unificado que funciona tanto en DEV como en PRO
"""

import requests
import json
import os
from werkzeug.security import check_password_hash
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

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

@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    config = get_supabase_config()
    return jsonify({
        "status": "healthy",
        "environment": config['env'],
        "supabase_url": config['url'],
        "timestamp": "2025-10-24T11:30:00.000000",
        "version": "1.0.1"
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de login unificado para DEV y PRO"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        config = get_supabase_config()
        headers = get_headers()
        
        print(f"🔐 Login intentado en {config['env'].upper()}: {email}")
        print(f"📍 Supabase URL: {config['url']}")
        
        # Buscar usuario en Supabase usando API REST
        response = requests.get(
            f"{config['url']}/rest/v1/user?email=eq.{email}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Error API Supabase: {response.status_code}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
        
        users = response.json()
        
        if not users:
            print(f"❌ Usuario no encontrado: {email}")
            return jsonify({
                'success': False,
                'message': 'Credenciales inválidas'
            }), 401
        
        user = users[0]
        print(f"✅ Usuario encontrado: {user['email']} (ID: {user['id']})")
        
        # Verificar contraseña
        stored_password = user['password']
        if not check_password_hash(stored_password, password):
            print(f"❌ Contraseña incorrecta para: {email}")
            return jsonify({
                'success': False,
                'message': 'Credenciales inválidas'
            }), 401
        
        print(f"✅ Contraseña correcta para: {email}")
        
        # Verificar si el usuario está activo
        if not user.get('active', True):
            print(f"❌ Usuario inactivo: {email}")
            return jsonify({
                'success': False,
                'message': 'Cuenta desactivada. Contacta al administrador.'
            }), 401
        
        # Obtener roles del usuario
        roles = []
        try:
            roles_response = requests.get(
                f"{config['url']}/rest/v1/roles_users?user_id=eq.{user['id']}",
                headers=headers
            )
            
            if roles_response.status_code == 200:
                role_assignments = roles_response.json()
                
                if role_assignments:
                    role_ids = [ra['role_id'] for ra in role_assignments]
                    role_ids_str = ','.join(map(str, role_ids))
                    
                    roles_response = requests.get(
                        f"{config['url']}/rest/v1/role?id=in.({role_ids_str})",
                        headers=headers
                    )
                    
                    if roles_response.status_code == 200:
                        roles_data = roles_response.json()
                        roles = [role['name'] for role in roles_data]
                        print(f"✅ Roles obtenidos: {roles}")
        except Exception as e:
            print(f"⚠️  Error obteniendo roles: {e}")
        
        # Respuesta exitosa
        login_response = {
            "success": True,
            "message": "Inicio de sesión exitoso",
            "environment": config['env'],
            "user": {
                "id": user['id'],
                "email": user['email'],
                "first_name": user.get('first_name'),
                "last_name": user.get('last_name'),
                "active": user['active'],
                "confirmed_at": user.get('confirmed_at')
            },
            "roles": roles,
            "redirectUrl": "/employee/register"
        }
        
        print(f"🎉 Login exitoso en {config['env'].upper()} para: {email}")
        return jsonify(login_response)
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@app.route('/api/auth/me', methods=['GET'])
def me():
    """Endpoint para verificar sesión actual"""
    return jsonify({
        "success": False,
        "message": "Sesión no encontrada"
    }), 401

if __name__ == '__main__':
    config = get_supabase_config()
    
    print("🚀 INICIANDO SERVIDOR DE LOGIN UNIFICADO")
    print("=" * 50)
    print(f"🌍 Entorno: {config['env'].upper()}")
    print(f"📍 Supabase URL: {config['url']}")
    print(f"🔑 Key: {config['key'][:20]}...")
    print(f"🌐 Puerto: 5003")
    print()
    
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=True
    )
