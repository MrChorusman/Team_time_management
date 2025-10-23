#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from models.user import User, db
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Probando conexión a la base de datos...")
        
        # Probar conexión básica
        result = db.session.execute(db.text('SELECT 1')).scalar()
        print(f"✅ Conexión básica: {result}")
        
        # Contar usuarios
        user_count = User.query.count()
        print(f"📊 Total de usuarios: {user_count}")
        
        # Listar usuarios
        users = User.query.limit(5).all()
        print(f"👥 Primeros 5 usuarios:")
        for user in users:
            print(f"  - {user.email} (ID: {user.id}, Activo: {user.active})")
        
        print("✅ Base de datos funcionando correctamente")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
