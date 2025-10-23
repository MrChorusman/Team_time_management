#!/usr/bin/env python3
"""
Script simple para probar la aplicación Flask
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple():
    """Probar la aplicación de forma simple"""
    
    print("🔍 PROBANDO APLICACIÓN FLASK SIMPLE")
    print("=" * 40)
    
    try:
        # Importar directamente el archivo app.py
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        create_app = app_module.create_app
        
        print("✅ Función create_app importada correctamente")
        
        # Crear la aplicación
        app = create_app()
        
        print("✅ Aplicación creada correctamente")
        print(f"📊 Configuración de BD: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Probar contexto de aplicación
        with app.app_context():
            print("✅ Contexto de aplicación creado")
            
            # Probar importación de modelos
            from models.user import User, db
            
            print("✅ Modelos importados correctamente")
            
            # Probar consulta a la base de datos
            user_count = User.query.count()
            print(f"📊 Usuarios en BD: {user_count}")
            
            # Probar usuario específico
            test_user = User.query.filter_by(email='test@test.com').first()
            if test_user:
                print(f"✅ Usuario de prueba encontrado: {test_user.email}")
            else:
                print("❌ Usuario de prueba no encontrado")
        
        # Probar endpoint con test client
        with app.test_client() as client:
            print("\n🧪 PROBANDO ENDPOINT DE LOGIN...")
            
            response = client.post('/api/auth/login', 
                                 json={"email": "test@test.com", "password": "123456"},
                                 content_type='application/json')
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response: {response.get_json()}")
            
            if response.status_code == 200:
                print("✅ Endpoint funcionando correctamente")
                return True
            else:
                print(f"❌ Error en endpoint: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple()