#!/usr/bin/env python3
"""
Script para crear un endpoint de login funcional usando API REST de Supabase
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
CORS(app)

# Configuración de Supabase desarrollo
DEV_URL = os.environ.get('SUPABASE_URL', 'https://qsbvoyjqfrhaqncqtknv.supabase.co')
DEV_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k')

headers = {
    'apikey': DEV_KEY,
    'Authorization': f"Bearer {DEV_KEY}",
    'Content-Type': 'application/json'
}

@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return jsonify({
        "status": "healthy",
        "environment": "development",
        "supabase_url": DEV_URL,
        "timestamp": "2025-10-24T11:30:00.000000",
        "version": "1.0.1"
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de login usando API REST de Supabase"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        print(f"🔐 Intentando login para: {email}")
        
        # Buscar usuario en Supabase usando API REST
        response = requests.get(
            f"{DEV_URL}/rest/v1/user?email=eq.{email}",
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
                f"{DEV_URL}/rest/v1/roles_users?user_id=eq.{user['id']}",
                headers=headers
            )
            
            if roles_response.status_code == 200:
                role_assignments = roles_response.json()
                
                if role_assignments:
                    role_ids = [ra['role_id'] for ra in role_assignments]
                    role_ids_str = ','.join(map(str, role_ids))
                    
                    roles_response = requests.get(
                        f"{DEV_URL}/rest/v1/role?id=in.({role_ids_str})",
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
        
        print(f"🎉 Login exitoso para: {email}")
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
    print("🚀 INICIANDO SERVIDOR DE LOGIN FUNCIONAL")
    print("=" * 50)
    print(f"📍 Supabase URL: {DEV_URL}")
    print(f"🔑 Key: {DEV_KEY[:20]}...")
    print(f"🌐 Puerto: 5002")
    print()
    
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True
    )
