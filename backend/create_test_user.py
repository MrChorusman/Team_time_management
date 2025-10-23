#!/usr/bin/env python3
"""
Script para crear un usuario de prueba
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar directamente los modelos
    from models.user import db, User, Role
    from models.employee import Employee  # Importar para resolver relaciones
    from flask_security.utils import hash_password
    from datetime import datetime
    
    # Configurar la base de datos directamente
    from config import Config
    from flask import Flask
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        print("🔍 Creando usuario de prueba...")
        
        # Crear el usuario de prueba
        test_email = "test@test.com"
        test_password = "123456"
        
        # Verificar si ya existe
        existing_user = User.query.filter_by(email=test_email).first()
        if existing_user:
            print(f"⚠️ Usuario {test_email} ya existe")
            print(f"   ID: {existing_user.id}")
            print(f"   Activo: {existing_user.active}")
            print(f"   Confirmado: {existing_user.confirmed_at is not None}")
        else:
            # Crear nuevo usuario
            user = User(
                email=test_email,
                password=hash_password(test_password),
                first_name="Test",
                last_name="User",
                active=True,
                confirmed_at=datetime.now()
            )
            
            # Asignar rol de viewer por defecto
            viewer_role = Role.query.filter_by(name='viewer').first()
            if viewer_role:
                user.roles.append(viewer_role)
            
            db.session.add(user)
            db.session.commit()
            
            print(f"✅ Usuario creado: {test_email}")
            print(f"   Contraseña: {test_password}")
            print(f"   ID: {user.id}")
        
        print("🎯 Ahora puedes probar el login con:")
        print(f"   Email: {test_email}")
        print(f"   Contraseña: {test_password}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
