#!/usr/bin/env python3
"""
Script para probar autenticación directamente con la aplicación Flask
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_direct():
    """Probar autenticación directamente"""
    
    print("🔍 PROBANDO AUTENTICACIÓN DIRECTAMENTE")
    print("=" * 50)
    
    try:
        # Importar la aplicación ya creada
        import app
        
        print(f"✅ Aplicación Flask cargada")
        print(f"📊 Configuración de BD: {app.app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Crear contexto de prueba
        with app.app.test_client() as client:
            print("\n🧪 PROBANDO ENDPOINT DE LOGIN...")
            
            # Datos de prueba
            login_data = {
                "email": "test@test.com",
                "password": "123456"
            }
            
            # Hacer petición
            response = client.post('/api/auth/login', 
                                 json=login_data,
                                 content_type='application/json')
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response: {response.get_json()}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print("✅ Login exitoso!")
                    return True
                else:
                    print(f"❌ Login fallido: {data.get('message')}")
                    return False
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_auth_direct()















