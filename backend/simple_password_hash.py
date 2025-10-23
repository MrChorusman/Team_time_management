#!/usr/bin/env python3
"""
Script simple para generar hash de contraseña usando Werkzeug
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Cargar variables de entorno
load_dotenv()

def generate_and_update_password():
    """Generar hash de contraseña y actualizar en la base de datos"""
    
    # Generar hash para la contraseña '123456'
    password = '123456'
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    print(f"🔐 Hash generado para contraseña '{password}':")
    print(f"   {hashed_password}")
    
    # Obtener credenciales
    host = os.environ.get('SUPABASE_HOST')
    port = os.environ.get('SUPABASE_PORT', '6543')
    database = os.environ.get('SUPABASE_DB_NAME', 'postgres')
    user = os.environ.get('SUPABASE_DB_USER', 'postgres')
    password_db = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print("\n🔍 Actualizando contraseña en la base de datos...")
    
    try:
        # Conectar a la base de datos
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password_db
        )
        
        cursor = connection.cursor()
        
        # Actualizar la contraseña del usuario
        cursor.execute("""
            UPDATE "user" 
            SET password = %s 
            WHERE email = %s
        """, (hashed_password, 'test@test.com'))
        
        if cursor.rowcount > 0:
            print("✅ Contraseña actualizada correctamente en la base de datos")
        else:
            print("⚠️ No se encontró el usuario para actualizar")
        
        # Verificar el usuario
        cursor.execute("""
            SELECT email, active, confirmed_at 
            FROM "user" 
            WHERE email = %s
        """, ('test@test.com',))
        
        user_info = cursor.fetchone()
        if user_info:
            email, active, confirmed_at = user_info
            print(f"👤 Usuario verificado:")
            print(f"   Email: {email}")
            print(f"   Activo: {active}")
            print(f"   Confirmado: {confirmed_at is not None}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n🎯 Usuario de prueba listo:")
        print("   Email: test@test.com")
        print("   Contraseña: 123456")
        print("   Hash: Generado con Werkzeug")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    generate_and_update_password()


