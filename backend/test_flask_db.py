#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos desde Flask
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Crear la aplicación Flask
    import app as app_module
    from models.user import db, User
    
    create_app = app_module.create_app
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Probando conexión a la base de datos desde Flask...")
        print(f"📊 DATABASE_URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Probar conexión básica
        try:
            result = db.session.execute(db.text('SELECT 1')).scalar()
            print(f"✅ Conexión básica: {result}")
        except Exception as e:
            print(f"❌ Error de conexión básica: {e}")
            exit(1)
        
        # Contar usuarios
        try:
            user_count = User.query.count()
            print(f"📊 Total de usuarios: {user_count}")
            
            if user_count > 0:
                # Listar usuarios
                users = User.query.limit(5).all()
                print(f"👥 Primeros 5 usuarios:")
                for user in users:
                    print(f"  - {user.email} (ID: {user.id}, Activo: {user.active})")
                    
                # Probar login específico
                test_user = User.query.filter_by(email='test@test.com').first()
                if test_user:
                    print(f"✅ Usuario de prueba encontrado: {test_user.email}")
                    print(f"   Activo: {test_user.active}")
                    print(f"   Confirmado: {test_user.confirmed_at is not None}")
                    print(f"   Roles: {[role.name for role in test_user.roles]}")
                else:
                    print("❌ Usuario de prueba no encontrado")
            else:
                print("ℹ️ No hay usuarios en la base de datos")
                
        except Exception as e:
            print(f"❌ Error consultando usuarios: {e}")
            import traceback
            traceback.print_exc()
        
        print("✅ Base de datos funcionando correctamente desde Flask")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
