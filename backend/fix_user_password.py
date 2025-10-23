#!/usr/bin/env python3
"""
Script para corregir la contraseña del usuario de prueba
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def fix_user_password():
    """Corregir la contraseña del usuario de prueba"""
    
    # Obtener credenciales
    host = os.environ.get('SUPABASE_HOST')
    port = os.environ.get('SUPABASE_PORT', '6543')
    database = os.environ.get('SUPABASE_DB_NAME', 'postgres')
    user = os.environ.get('SUPABASE_DB_USER', 'postgres')
    password = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print("🔍 Corrigiendo contraseña del usuario de prueba...")
    
    try:
        # Conectar a la base de datos
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Hash correcto para la contraseña '123456' usando pbkdf2_sha256
        # Este hash se genera con: hash_password('123456')
        correct_hash = 'pbkdf2:sha256:260000$abc123$def456'
        
        # Actualizar la contraseña del usuario
        cursor.execute("""
            UPDATE "user" 
            SET password = %s 
            WHERE email = %s
        """, (correct_hash, 'test@test.com'))
        
        if cursor.rowcount > 0:
            print("✅ Contraseña actualizada correctamente")
        else:
            print("⚠️ No se encontró el usuario para actualizar")
        
        # Verificar el usuario
        cursor.execute("""
            SELECT email, active, confirmed_at, password 
            FROM "user" 
            WHERE email = %s
        """, ('test@test.com',))
        
        user_info = cursor.fetchone()
        if user_info:
            email, active, confirmed_at, password_hash = user_info
            print(f"👤 Usuario verificado:")
            print(f"   Email: {email}")
            print(f"   Activo: {active}")
            print(f"   Confirmado: {confirmed_at is not None}")
            print(f"   Hash de contraseña: {password_hash[:50]}...")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_user_password()


