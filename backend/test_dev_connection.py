#!/usr/bin/env python3
"""Script para probar conexión al proyecto de desarrollo"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

print("🔍 PROBANDO CONEXIÓN AL PROYECTO DE DESARROLLO")
print("==============================================")

# Obtener variables de entorno
SUPABASE_DEV_HOST = os.environ.get('SUPABASE_DEV_HOST')
SUPABASE_DEV_PORT = os.environ.get('SUPABASE_DEV_PORT')
SUPABASE_DEV_DB = os.environ.get('SUPABASE_DEV_DB')
SUPABASE_DEV_USER = os.environ.get('SUPABASE_DEV_USER')
SUPABASE_DEV_DB_PASSWORD = os.environ.get('SUPABASE_DEV_DB_PASSWORD')

print(f"📍 Host: {SUPABASE_DEV_HOST}")
print(f"🔌 Puerto: {SUPABASE_DEV_PORT}")
print(f"🗄️  Base de datos: {SUPABASE_DEV_DB}")
print(f"👤 Usuario: {SUPABASE_DEV_USER}")
print(f"🔑 Contraseña: {'***' if SUPABASE_DEV_DB_PASSWORD else 'NO CONFIGURADO'}")

try:
    DATABASE_URL = f"postgresql://{SUPABASE_DEV_USER}:{SUPABASE_DEV_DB_PASSWORD}@{SUPABASE_DEV_HOST}:{SUPABASE_DEV_PORT}/{SUPABASE_DEV_DB}"
    print(f"\n🔗 Conectando a Supabase desarrollo...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()[0]
    print(f"✅ Versión de PostgreSQL: {db_version}")
    
    # Verificar tablas existentes
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"✅ Tablas encontradas ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("⚠️  No se encontraron tablas en el esquema público")
    
    cursor.close()
    conn.close()
    print("\n🎉 ¡CONEXIÓN EXITOSA AL PROYECTO DE DESARROLLO!")
    
except Exception as e:
    print(f"❌ ERROR de conexión: {e}")
