#!/usr/bin/env python
"""Script para probar si SQLAlchemy puede ver los usuarios"""
import sys
import os

# Configurar el path
sys.path.insert(0, os.path.dirname(__file__))

# Cargar configuración antes de importar los modelos
import config as config_module
config = config_module.config
os.environ.update({
    'SUPABASE_HOST': config.get('SUPABASE_HOST', ''),
    'SUPABASE_PORT': str(config.get('SUPABASE_PORT', '')),
    'SUPABASE_DB': config.get('SUPABASE_DB', ''),
    'SUPABASE_USER': config.get('SUPABASE_USER', ''),
    'SUPABASE_PASSWORD': config.get('SUPABASE_PASSWORD', ''),
})

# Importar Flask y modelos
from flask import Flask
from models import db, User

# Crear app
app = Flask(__name__)
# Cargar configuración desde la clase DevelopmentConfig
app.config.from_object(config['development'])
print(f"Environment: development")
print(f"Config class: {config['development'].__name__}")

# Inicializar db
db.init_app(app)

# Probar consulta
with app.app_context():
    print("\n=== PROBANDO CONEXIÓN SQLALCHEMY ===")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    
    try:
        # Contar usuarios
        user_count = User.query.count()
        print(f"\n✅ Total de usuarios encontrados: {user_count}")
        
        # Listar usuarios
        users = User.query.all()
        print("\n📋 Lista de usuarios:")
        for user in users:
            print(f"  - ID: {user.id}, Email: {user.email}, Active: {user.active}")
        
        # Buscar test@test.com específicamente
        test_user = User.query.filter_by(email='test@test.com').first()
        if test_user:
            print(f"\n✅ Usuario test@test.com encontrado:")
            print(f"   ID: {test_user.id}")
            print(f"   Email: {test_user.email}")
            print(f"   Active: {test_user.active}")
            print(f"   Has Password: {'Yes' if test_user.password else 'No'}")
            print(f"   Has fs_uniquifier: {'Yes' if test_user.fs_uniquifier else 'No'}")
        else:
            print(f"\n❌ Usuario test@test.com NO encontrado")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

