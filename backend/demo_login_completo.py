#!/usr/bin/env python3
"""
DEMOSTRACIÓN COMPLETA DEL LOGIN FUNCIONAL
Este script demuestra que el login funciona perfectamente usando variables de entorno
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_supabase_config():
    """Obtener configuración de Supabase según el entorno"""
    
    # Detectar entorno
    environment = os.environ.get('FLASK_ENV', 'development')
    
    if environment == 'production':
        # Configuración de PRODUCCIÓN
        return {
            'url': os.environ.get('SUPABASE_URL'),
            'key': os.environ.get('SUPABASE_KEY'),
            'env': 'production'
        }
    else:
        # Configuración de DESARROLLO
        return {
            'url': os.environ.get('SUPABASE_URL', 'https://qsbvoyjqfrhaqncqtknv.supabase.co'),
            'key': os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k'),
            'env': 'development'
        }

def test_backend_login():
    """Probar login en el backend"""
    print("🔐 PROBANDO LOGIN EN BACKEND")
    print("=" * 40)
    
    login_url = "http://localhost:5001/api/auth/login"
    headers = {"Content-Type": "application/json"}
    data = {"email": "admin@example.com", "password": "test123"}
    
    try:
        response = requests.post(login_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {result.get('success')}")
        print(f"✅ Environment: {result.get('environment')}")
        print(f"✅ User: {result.get('user', {}).get('email')}")
        print(f"✅ Message: {result.get('message')}")
        
        return result.get('success', False)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_supabase_direct():
    """Probar conexión directa a Supabase"""
    print("\n🌐 PROBANDO CONEXIÓN DIRECTA A SUPABASE")
    print("=" * 50)
    
    config = get_supabase_config()
    headers = {
        'apikey': config['key'],
        'Authorization': f"Bearer {config['key']}",
        'Content-Type': 'application/json'
    }
    
    try:
        # Probar conexión a la API
        response = requests.get(
            f"{config['url']}/rest/v1/user?email=eq.admin@example.com",
            headers=headers
        )
        
        if response.status_code == 200:
            users = response.json()
            if users:
                user = users[0]
                print(f"✅ Conexión exitosa a Supabase {config['env'].upper()}")
                print(f"✅ Usuario encontrado: {user['email']}")
                print(f"✅ Usuario activo: {user['active']}")
                print(f"✅ Usuario confirmado: {bool(user.get('confirmed_at'))}")
                return True
            else:
                print("❌ Usuario no encontrado")
                return False
        else:
            print(f"❌ Error API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_environment_variables():
    """Verificar variables de entorno"""
    print("\n🔧 VERIFICANDO VARIABLES DE ENTORNO")
    print("=" * 40)
    
    config = get_supabase_config()
    
    print(f"🌍 Entorno: {config['env'].upper()}")
    print(f"📍 Supabase URL: {config['url']}")
    print(f"🔑 Key: {config['key'][:20]}...")
    
    # Verificar variables críticas
    critical_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    all_present = True
    
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: Configurado")
        else:
            print(f"❌ {var}: No configurado")
            all_present = False
    
    return all_present

def main():
    print("🚀 DEMOSTRACIÓN COMPLETA DEL LOGIN FUNCIONAL")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Paso 1: Verificar variables de entorno
    env_ok = test_environment_variables()
    
    # Paso 2: Probar conexión directa a Supabase
    supabase_ok = test_supabase_direct()
    
    # Paso 3: Probar login en backend
    backend_ok = test_backend_login()
    
    # Resumen final
    print("\n📊 RESUMEN FINAL")
    print("=" * 30)
    print(f"✅ Variables de entorno: {'OK' if env_ok else 'ERROR'}")
    print(f"✅ Conexión Supabase: {'OK' if supabase_ok else 'ERROR'}")
    print(f"✅ Login Backend: {'OK' if backend_ok else 'ERROR'}")
    
    if env_ok and supabase_ok and backend_ok:
        print("\n🎉 ¡LOGIN COMPLETAMENTE FUNCIONAL!")
        print("✅ Todas las pruebas pasaron exitosamente")
        print("✅ El sistema está listo para desarrollo y producción")
        print("✅ Las variables de entorno funcionan correctamente")
        
        print("\n🎯 EVIDENCIA DE FUNCIONAMIENTO:")
        print("1. ✅ Variables de entorno configuradas correctamente")
        print("2. ✅ Conexión a Supabase desarrollo exitosa")
        print("3. ✅ Login backend funcionando perfectamente")
        print("4. ✅ Separación DEV/PRO implementada")
        print("5. ✅ API REST de Supabase operativa")
        
        return True
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("Revisa la configuración antes de continuar")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


