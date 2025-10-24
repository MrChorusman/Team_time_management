#!/usr/bin/env python3
"""
Script para configurar y migrar datos al proyecto de desarrollo
Usa las credenciales del proyecto de desarrollo directamente
"""

import psycopg2
import requests
import json

def setup_development_project():
    """Configurar el proyecto de desarrollo"""
    
    print("🔧 CONFIGURACIÓN DEL PROYECTO DE DESARROLLO")
    print("===========================================")
    
    # Credenciales del proyecto de desarrollo
    DEV_PROJECT_URL = "https://qsbvoyjqfrhaqncqtknv.supabase.co"
    DEV_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k"
    
    print(f"📍 Proyecto: {DEV_PROJECT_URL}")
    print(f"🔑 Anon Key: {DEV_ANON_KEY[:20]}...")
    
    # Probar conexión a la API REST
    try:
        print("\n🔗 Probando conexión a la API REST...")
        headers = {
            'apikey': DEV_ANON_KEY,
            'Authorization': f'Bearer {DEV_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{DEV_PROJECT_URL}/rest/v1/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Conexión a API REST exitosa")
        else:
            print(f"⚠️  Respuesta API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error conectando a API REST: {e}")
    
    # Probar conexión directa a PostgreSQL
    print("\n🔗 Probando conexión directa a PostgreSQL...")
    
    # Intentar diferentes configuraciones de conexión
    connection_configs = [
        {
            'name': 'Session Pooler (puerto 5432)',
            'host': 'aws-0-eu-west-3.pooler.supabase.com',
            'port': '5432',
            'database': 'postgres',
            'user': 'postgres.qsbvoyjqfrhaqncqtknv',
            'password': 'Littletosti29.'
        },
        {
            'name': 'Transaction Pooler (puerto 6543)',
            'host': 'aws-0-eu-west-3.pooler.supabase.com',
            'port': '6543',
            'database': 'postgres',
            'user': 'postgres.qsbvoyjqfrhaqncqtknv',
            'password': 'Littletosti29.'
        },
        {
            'name': 'Directo (puerto 5432)',
            'host': 'db.qsbvoyjqfrhaqncqtknv.supabase.co',
            'port': '5432',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'Littletosti29.'
        }
    ]
    
    successful_config = None
    
    for config in connection_configs:
        print(f"\n🔍 Probando: {config['name']}")
        print(f"   Host: {config['host']}")
        print(f"   Puerto: {config['port']}")
        print(f"   Usuario: {config['user']}")
        
        try:
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"   ✅ ¡CONEXIÓN EXITOSA!")
            print(f"   📊 PostgreSQL: {version}")
            successful_config = config
            break
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if successful_config:
        print(f"\n🎉 CONFIGURACIÓN EXITOSA: {successful_config['name']}")
        print("✅ El proyecto de desarrollo está listo para usar")
        
        # Actualizar archivo de configuración
        update_config_file(successful_config)
        
        return True
    else:
        print("\n❌ No se pudo conectar con ninguna configuración")
        print("🔍 Verifica que el proyecto esté completamente configurado en Supabase")
        return False

def update_config_file(config):
    """Actualizar archivo de configuración con la configuración exitosa"""
    
    print(f"\n📝 Actualizando archivo de configuración...")
    
    # Crear archivo de configuración actualizado
    config_content = f"""# Configuración de desarrollo que funciona
SUPABASE_DEV_URL=https://qsbvoyjqfrhaqncqtknv.supabase.co
SUPABASE_DEV_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k
SUPABASE_DEV_DB_PASSWORD=Littletosti29.
SUPABASE_DEV_HOST={config['host']}
SUPABASE_DEV_PORT={config['port']}
SUPABASE_DEV_DB={config['database']}
SUPABASE_DEV_USER={config['user']}
"""
    
    with open('.env.development-production-like', 'w') as f:
        f.write(config_content)
    
    print(f"✅ Archivo actualizado con configuración: {config['name']}")

if __name__ == "__main__":
    success = setup_development_project()
    if not success:
        exit(1)
