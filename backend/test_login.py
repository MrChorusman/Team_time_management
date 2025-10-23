#!/usr/bin/env python3
"""
Script para probar el login directamente
"""

import requests
import json

def test_login():
    """Probar el endpoint de login"""
    
    url = "http://localhost:5000/api/auth/login"
    
    # Datos de prueba
    test_data = {
        "email": "test@test.com",
        "password": "123456"
    }
    
    try:
        print("🔍 Probando login...")
        print(f"📧 Email: {test_data['email']}")
        print(f"🔒 Contraseña: {test_data['password']}")
        
        response = requests.post(url, json=test_data)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login exitoso!")
                print(f"👤 Usuario: {data.get('user', {}).get('email')}")
                return True
            else:
                print(f"❌ Login fallido: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el backend esté ejecutándose en puerto 5000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_register():
    """Probar el endpoint de registro"""
    
    url = "http://localhost:5000/api/auth/register"
    
    # Datos de prueba
    test_data = {
        "email": "test@test.com",
        "password": "123456",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        print("🔍 Probando registro...")
        print(f"📧 Email: {test_data['email']}")
        
        response = requests.post(url, json=test_data)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Registro exitoso!")
                return True
            else:
                print(f"⚠️ Registro fallido: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING AUTENTICACIÓN")
    print("=" * 50)
    
    # Probar registro primero
    print("\n1️⃣ PROBANDO REGISTRO:")
    register_success = test_register()
    
    # Probar login
    print("\n2️⃣ PROBANDO LOGIN:")
    login_success = test_login()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS:")
    print(f"   Registro: {'✅ OK' if register_success else '❌ KO'}")
    print(f"   Login: {'✅ OK' if login_success else '❌ KO'}")
    
    if login_success:
        print("\n🎉 ¡La autenticación está funcionando!")
        print("💡 Ahora puedes probar en el frontend")
    else:
        print("\n⚠️ Hay problemas con la autenticación")
        print("💡 Revisa los logs del backend")

