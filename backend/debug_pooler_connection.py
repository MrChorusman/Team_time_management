#!/usr/bin/env python3
"""
Script de diagnóstico para conexión con Supabase Session Pooler
Prueba diferentes configuraciones para identificar el problema
"""

import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection(host, port, db, user, password, description):
    """Prueba una configuración específica de conexión"""
    print(f"\n🔍 PROBANDO: {description}")
    print("=" * 60)
    print(f"📍 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print(f"🗄️  Base de datos: {db}")
    print(f"👤 Usuario: {user}")
    print(f"🔑 Contraseña: {'*' * len(password) if password else 'NO CONFIGURADA'}")
    
    try:
        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        print(f"🔗 URL: {conn_string.replace(password, '***') if password else 'SIN CONTRASEÑA'}")
        
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Consulta básica
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL Version: {version}")
        
        # Verificar usuario actual
        cursor.execute("SELECT current_user, current_database();")
        current_user, current_db = cursor.fetchone()
        print(f"✅ Usuario actual: {current_user}")
        print(f"✅ Base de datos actual: {current_db}")
        
        # Verificar tablas
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        print(f"✅ Tablas en esquema público: {table_count}")
        
        cursor.close()
        conn.close()
        print("🎉 ¡CONEXIÓN EXITOSA!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 DIAGNÓSTICO DE CONEXIÓN SUPABASE SESSION POOLER")
    print("=" * 70)
    
    # Configuraciones a probar
    configs = [
        {
            "host": "aws-0-eu-west-3.pooler.supabase.com",
            "port": "5432",
            "db": "postgres",
            "user": "postgres.xmaxohyxgsthligskjvg",
            "password": "Littletosti29.",
            "description": "Session Pooler (Configuración Actual)"
        },
        {
            "host": "aws-0-eu-west-3.pooler.supabase.com",
            "port": "5432",
            "db": "postgres",
            "user": "postgres",
            "password": "Littletosti29.",
            "description": "Session Pooler (Usuario Simple)"
        },
        {
            "host": "aws-0-eu-west-3.pooler.supabase.com",
            "port": "6543",
            "db": "postgres",
            "user": "postgres.xmaxohyxgsthligskjvg",
            "password": "Littletosti29.",
            "description": "Transaction Pooler (Puerto 6543)"
        },
        {
            "host": "aws-0-eu-west-3.pooler.supabase.com",
            "port": "6543",
            "db": "postgres",
            "user": "postgres",
            "password": "Littletosti29.",
            "description": "Transaction Pooler (Usuario Simple)"
        }
    ]
    
    successful_configs = []
    
    for config in configs:
        success = test_connection(**config)
        if success:
            successful_configs.append(config)
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    if successful_configs:
        print(f"✅ Configuraciones exitosas: {len(successful_configs)}")
        for i, config in enumerate(successful_configs, 1):
            print(f"   {i}. {config['description']}")
            print(f"      Usuario: {config['user']}")
            print(f"      Puerto: {config['port']}")
    else:
        print("❌ Ninguna configuración funcionó")
        print("\n🔍 POSIBLES CAUSAS:")
        print("   - Contraseña incorrecta")
        print("   - Proyecto pausado o suspendido")
        print("   - Configuración del pooler incorrecta")
        print("   - Problemas de red o firewall")
    
    print("\n🎯 RECOMENDACIÓN:")
    if successful_configs:
        best_config = successful_configs[0]
        print(f"   Usar: {best_config['description']}")
        print(f"   Usuario: {best_config['user']}")
        print(f"   Puerto: {best_config['port']}")
    else:
        print("   Contactar soporte de Supabase")

if __name__ == "__main__":
    main()
