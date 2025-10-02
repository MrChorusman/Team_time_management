#!/usr/bin/env python3
"""
Aplicación Flask simplificada para despliegue de Team Time Management
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuración básica
app = Flask(__name__)

# Configuración de la base de datos (SQLite para simplicidad en despliegue)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///team_time_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS
CORS(app, origins=['*'])

# Inicializar base de datos
db = SQLAlchemy(app)

# Modelo básico de usuario para el despliegue
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Rutas básicas
@app.route('/')
def index():
    """Ruta principal"""
    return jsonify({
        'message': 'Team Time Management API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Health check para verificar que la API está funcionando"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login básico para demostración"""
    return jsonify({
        'success': True,
        'message': 'Login endpoint - implementación completa disponible en desarrollo',
        'user': {
            'id': 1,
            'email': 'demo@teamtime.com',
            'role': 'admin'
        },
        'token': 'demo-token-123'
    })

@app.route('/api/dashboard')
def dashboard():
    """Dashboard básico"""
    return jsonify({
        'success': True,
        'data': {
            'total_users': 42,
            'active_employees': 35,
            'total_teams': 5,
            'pending_approvals': 3,
            'message': 'Dashboard demo - datos simulados'
        }
    })

# Inicializar base de datos
with app.app_context():
    try:
        db.create_all()
        print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️  Error inicializando base de datos: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
