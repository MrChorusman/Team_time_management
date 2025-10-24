#!/usr/bin/env python3
"""
Script para configurar y ejecutar el entorno de desarrollo completo
"""

import requests
import psycopg2
import os
import subprocess
import time
from dotenv import load_dotenv

def test_supabase_connection():
    """Probar conexión a Supabase desarrollo"""
    
    print("🔍 PROBANDO CONEXIÓN A SUPABASE DESARROLLO")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    DEV_URL = os.environ.get('SUPABASE_URL')
    DEV_KEY = os.environ.get('SUPABASE_KEY')
    
    print(f"📍 URL: {DEV_URL}")
    print(f"🔑 Key: {DEV_KEY[:20]}...")
    
    headers = {
        'apikey': DEV_KEY,
        'Authorization': f"Bearer {DEV_KEY}",
        'Content-Type': 'application/json'
    }
    
    try:
        # Probar conexión API
        response = requests.get(f"{DEV_URL}/rest/v1/user", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ API funcionando! Usuarios encontrados: {len(users)}")
            
            # Mostrar usuarios
            for user in users:
                print(f"   👤 {user['email']} (ID: {user['id']})")
            
            return True
        else:
            print(f"❌ Error API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return False

def start_backend():
    """Ejecutar backend en entorno de desarrollo"""
    
    print("\n🚀 INICIANDO BACKEND EN ENTORNO DE DESARROLLO")
    print("=" * 50)
    
    try:
        # Cambiar al directorio del backend
        backend_dir = "/Users/thelittle/Team_time_management/Team_time_management/backend"
        
        # Ejecutar backend
        cmd = f"cd {backend_dir} && source venv/bin/activate && python main.py"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Esperando que el backend se inicie...")
        time.sleep(5)
        
        # Verificar si está ejecutándose
        try:
            import requests
            response = requests.get("http://localhost:5001/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend ejecutándose correctamente")
                return True
            else:
                print(f"⚠️  Backend respondiendo pero con problemas: {response.status_code}")
                return False
        except:
            print("❌ Backend no responde")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando backend: {e}")
        return False

def test_login_endpoint():
    """Probar endpoint de login"""
    
    print("\n🔐 PROBANDO ENDPOINT DE LOGIN")
    print("=" * 30)
    
    try:
        import requests
        
        # Datos de prueba
        login_data = {
            "email": "admin@example.com",
            "password": "test123"
        }
        
        print(f"📧 Email: {login_data['email']}")
        print(f"🔑 Password: {login_data['password']}")
        
        # Hacer request
        response = requests.post(
            "http://localhost:5001/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login exitoso!")
                return True
            else:
                print(f"❌ Login falló: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando login: {e}")
        return False

def main():
    """Función principal"""
    
    print("🎯 CONFIGURACIÓN COMPLETA DEL ENTORNO DE DESARROLLO")
    print("=" * 60)
    print(f"📅 Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Paso 1: Probar conexión a Supabase
    supabase_ok = test_supabase_connection()
    
    if not supabase_ok:
        print("\n❌ No se puede continuar sin conexión a Supabase")
        return False
    
    # Paso 2: Ejecutar backend
    backend_ok = start_backend()
    
    if not backend_ok:
        print("\n❌ No se puede continuar sin backend funcionando")
        return False
    
    # Paso 3: Probar login
    login_ok = test_login_endpoint()
    
    if login_ok:
        print("\n🎉 ¡ENTORNO DE DESARROLLO COMPLETAMENTE FUNCIONAL!")
        print("✅ Supabase desarrollo conectado")
        print("✅ Backend ejecutándose")
        print("✅ Login funcionando")
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Abrir browser en http://localhost:5173")
        print("   2. Probar login con admin@example.com / test123")
        print("   3. Desarrollar nuevas funcionalidades")
        return True
    else:
        print("\n⚠️  Entorno parcialmente funcional")
        print("✅ Supabase desarrollo conectado")
        print("✅ Backend ejecutándose")
        print("❌ Login con problemas")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


