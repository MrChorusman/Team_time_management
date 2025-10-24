#!/usr/bin/env python3
"""
Script para migrar datos usando la API REST de Supabase
"""

import requests
import json
from datetime import datetime

def migrate_via_api():
    """Migrar datos usando la API REST de Supabase"""
    
    print("🔄 MIGRACIÓN DE DATOS VIA API REST")
    print("=" * 40)
    
    # Configuración de producción
    PROD_URL = "https://xmaxohyxgsthligskjvg.supabase.co"
    PROD_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtYXhvaHl4Z3N0aGxpZ3NranZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk2NjI2NDgsImV4cCI6MjA2NTIzODY0OH0.O7D9MVMxCyg10dRLnJGZStamR4IOltRLx5wK5aENqB4"
    
    # Configuración de desarrollo
    DEV_URL = "https://qsbvoyjqfrhaqncqtknv.supabase.co"
    DEV_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k"
    
    # Headers para producción
    prod_headers = {
        'apikey': PROD_KEY,
        'Authorization': f"Bearer {PROD_KEY}",
        'Content-Type': 'application/json'
    }
    
    # Headers para desarrollo
    dev_headers = {
        'apikey': DEV_KEY,
        'Authorization': f"Bearer {DEV_KEY}",
        'Content-Type': 'application/json'
    }
    
    # Tablas a migrar (en orden de dependencias)
    tables_to_migrate = [
        'countries',
        'autonomous_communities', 
        'provinces',
        'cities',
        'role',
        'user',
        'roles_users',
        'team',
        'employee',
        'holiday',
        'calendar_activity',
        'notification',
        'calendar_entries'
    ]
    
    migration_stats = {}
    
    for table in tables_to_migrate:
        print(f"\n📊 Migrando tabla: {table}")
        
        try:
            # Obtener datos de producción
            print(f"   🔍 Obteniendo datos de producción...")
            prod_response = requests.get(
                f"{PROD_URL}/rest/v1/{table}",
                headers=prod_headers
            )
            
            if prod_response.status_code != 200:
                print(f"   ⚠️  Error obteniendo datos de producción: {prod_response.status_code}")
                migration_stats[table] = f"Error: {prod_response.status_code}"
                continue
            
            data = prod_response.json()
            
            if not data:
                print(f"   ⚠️  Tabla {table} está vacía, saltando...")
                migration_stats[table] = 0
                continue
            
            print(f"   📝 {len(data)} registros encontrados")
            
            # Limpiar tabla de desarrollo
            print(f"   🧹 Limpiando tabla de desarrollo...")
            dev_response = requests.delete(
                f"{DEV_URL}/rest/v1/{table}",
                headers=dev_headers
            )
            
            # Insertar datos en desarrollo
            print(f"   📥 Insertando datos en desarrollo...")
            dev_response = requests.post(
                f"{DEV_URL}/rest/v1/{table}",
                headers=dev_headers,
                json=data
            )
            
            if dev_response.status_code in [200, 201]:
                print(f"   ✅ {len(data)} registros migrados")
                migration_stats[table] = len(data)
            else:
                print(f"   ❌ Error insertando datos: {dev_response.status_code}")
                print(f"   📄 Respuesta: {dev_response.text}")
                migration_stats[table] = f"Error: {dev_response.status_code}"
                
        except Exception as e:
            print(f"   ❌ Error migrando {table}: {e}")
            migration_stats[table] = f"Error: {e}"
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE MIGRACIÓN:")
    print("=" * 30)
    total_migrated = 0
    for table, count in migration_stats.items():
        if isinstance(count, int):
            print(f"   {table}: {count} registros")
            total_migrated += count
        else:
            print(f"   {table}: {count}")
    
    print(f"\n🎉 ¡MIGRACIÓN COMPLETADA!")
    print(f"✅ Total de registros migrados: {total_migrated}")
    print(f"✅ Proyecto de desarrollo actualizado con datos de producción")
    
    return True

if __name__ == "__main__":
    print("🚀 MIGRACIÓN DE DATOS VIA API REST")
    print("=" * 40)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = migrate_via_api()
    
    if success:
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Verificar datos en Supabase desarrollo")
        print("   2. Probar login en entorno de desarrollo")
        print("   3. Usar entorno de desarrollo para testing")
    else:
        print("\n❌ Error en la migración")
        exit(1)


