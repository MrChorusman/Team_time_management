#!/usr/bin/env python3
"""
Script rápido para probar la base de datos
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar la aplicación ya creada
    import app
    from models.user import User, db
    
    with app.app.app_context():
        print("🔍 Probando conexión a la base de datos...")
        
        # Probar conexión básica
        result = db.session.execute(db.text('SELECT 1')).scalar()
        print(f"✅ Conexión básica: {result}")
        
        # Contar usuarios
        user_count = User.query.count()
        print(f"📊 Total de usuarios: {user_count}")
        
        if user_count > 0:
            # Listar usuarios
            users = User.query.limit(5).all()
            print(f"👥 Primeros 5 usuarios:")
            for user in users:
                print(f"  - {user.email} (ID: {user.id}, Activo: {user.active})")
        else:
            print("ℹ️ No hay usuarios en la base de datos")
            print("💡 Necesitas crear usuarios para probar el login")
        
        print("✅ Base de datos funcionando correctamente")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

