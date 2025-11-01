#!/usr/bin/env python3
"""
Script de prueba completa del sistema de autenticación
"""

import requests
import json
import sys

def test_complete_auth():
    """Probar el flujo completo de autenticación"""
    
    print("🧪 PRUEBA COMPLETA DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 60)
    
    base_url = "http://localhost:5001/api/auth-simple"
    
    # 1. Probar endpoint de test
    print("\n1️⃣ PROBANDO ENDPOINT DE TEST...")
    try:
        response = requests.get(f"{base_url}/test")
        if response.status_code == 200:
            print("✅ Endpoint de test funcionando")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Error en endpoint de test: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al endpoint: {e}")
        return False
    
    # 2. Probar login con usuario existente
    print("\n2️⃣ PROBANDO LOGIN CON USUARIO EXISTENTE...")
    try:
        login_data = {
            "email": "test@test.com",
            "password": "123456"
        }
        
        response = requests.post(f"{base_url}/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login exitoso")
                print(f"   Usuario: {data.get('user', {}).get('email')}")
                print(f"   ID: {data.get('user', {}).get('id')}")
                
                # Guardar cookies para las siguientes pruebas
                session = requests.Session()
                session.cookies.update(response.cookies)
                
            else:
                print(f"❌ Login fallido: {data.get('message')}")
                return False
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False
    
    # 3. Probar verificación de sesión
    print("\n3️⃣ PROBANDO VERIFICACIÓN DE SESIÓN...")
    try:
        response = session.get(f"{base_url}/check-session")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('authenticated'):
                print("✅ Sesión verificada correctamente")
                print(f"   Usuario autenticado: {data.get('user_email')}")
            else:
                print("❌ Sesión no verificada")
                return False
        else:
            print(f"❌ Error verificando sesión: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando sesión: {e}")
        return False
    
    # 4. Probar registro de nuevo usuario
    print("\n4️⃣ PROBANDO REGISTRO DE NUEVO USUARIO...")
    try:
        register_data = {
            "email": "nuevo@test.com",
            "password": "123456",
            "first_name": "Nuevo",
            "last_name": "Usuario"
        }
        
        response = requests.post(f"{base_url}/register", json=register_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Registro exitoso")
                print(f"   Nuevo usuario: {data.get('user', {}).get('email')}")
            else:
                print(f"❌ Registro fallido: {data.get('message')}")
                # No es crítico si el usuario ya existe
        else:
            print(f"⚠️ Registro falló (puede ser porque el usuario ya existe): {response.status_code}")
            data = response.json()
            if "ya existe" in data.get('message', '').lower():
                print("✅ Usuario ya existe (comportamiento esperado)")
            else:
                print(f"   Respuesta: {data}")
                
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return False
    
    # 5. Probar logout
    print("\n5️⃣ PROBANDO LOGOUT...")
    try:
        response = session.post(f"{base_url}/logout")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Logout exitoso")
            else:
                print(f"❌ Logout fallido: {data.get('message')}")
                return False
        else:
            print(f"❌ Error en logout: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en logout: {e}")
        return False
    
    # 6. Verificar que la sesión se cerró
    print("\n6️⃣ VERIFICANDO QUE LA SESIÓN SE CERRÓ...")
    try:
        response = session.get(f"{base_url}/check-session")
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('authenticated'):
                print("✅ Sesión cerrada correctamente")
            else:
                print("❌ La sesión no se cerró correctamente")
                return False
        else:
            print(f"❌ Error verificando sesión cerrada: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando sesión cerrada: {e}")
        return False
    
    print("\n🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
    print("✅ El sistema de autenticación está funcionando correctamente")
    return True

if __name__ == "__main__":
    success = test_complete_auth()
    sys.exit(0 if success else 1)













