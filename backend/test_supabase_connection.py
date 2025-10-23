#!/usr/bin/env python3
"""
Script para probar la conexión directa a Supabase
"""

import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_supabase_connection():
    """Probar conexión directa a Supabase"""
    
    # Obtener credenciales
    host = os.environ.get('SUPABASE_HOST')
    port = os.environ.get('SUPABASE_PORT', '6543')
    database = os.environ.get('SUPABASE_DB_NAME', 'postgres')
    user = os.environ.get('SUPABASE_DB_USER', 'postgres')
    password = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print("🔍 Probando conexión directa a Supabase...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password) if password else 'No configurado'}")
    
    if not all([host, user, password]):
        print("❌ Faltan credenciales de Supabase")
        return False
    
    try:
        # Intentar conectar
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        # Probar consulta
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        print(f"✅ Conexión exitosa! Resultado: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()

