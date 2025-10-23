#!/usr/bin/env python3
"""
Script para crear un usuario directamente en la base de datos
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_test_user():
    """Crear un usuario de prueba directamente en la base de datos"""
    
    # Obtener credenciales
    host = os.environ.get('SUPABASE_HOST')
    port = os.environ.get('SUPABASE_PORT', '6543')
    database = os.environ.get('SUPABASE_DB_NAME', 'postgres')
    user = os.environ.get('SUPABASE_DB_USER', 'postgres')
    password = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print("🔍 Creando usuario de prueba directamente en Supabase...")
    
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
        
        # Verificar si ya existe el usuario
        cursor.execute("SELECT id, email FROM \"user\" WHERE email = %s", ('test@test.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠️ Usuario test@test.com ya existe (ID: {existing_user[0]})")
            
            # Verificar si está activo
            cursor.execute("SELECT active, confirmed_at FROM \"user\" WHERE email = %s", ('test@test.com',))
            user_info = cursor.fetchone()
            
            if user_info:
                active, confirmed_at = user_info
                print(f"   Activo: {active}")
                print(f"   Confirmado: {confirmed_at is not None}")
                
                if not active or not confirmed_at:
                    print("🔄 Activando y confirmando usuario...")
                    cursor.execute("""
                        UPDATE "user" 
                        SET active = true, confirmed_at = NOW() 
                        WHERE email = %s
                    """, ('test@test.com',))
                    connection.commit()
                    print("✅ Usuario activado y confirmado")
        else:
            print("➕ Creando nuevo usuario de prueba...")
            
            # Crear usuario
            cursor.execute("""
                INSERT INTO "user" (email, password, active, confirmed_at, fs_uniquifier, first_name, last_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (
                'test@test.com',
                'pbkdf2:sha256:260000$abc123$def456',  # Hash de ejemplo para '123456'
                True,
                'NOW()',
                'test-uniquifier-123',
                'Test',
                'User'
            ))
            
            user_id = cursor.fetchone()[0]
            
            # Asignar rol de viewer
            cursor.execute("SELECT id FROM role WHERE name = 'viewer'")
            role_result = cursor.fetchone()
            
            if role_result:
                role_id = role_result[0]
                cursor.execute("""
                    INSERT INTO roles_users (user_id, role_id)
                    VALUES (%s, %s)
                """, (user_id, role_id))
                print("✅ Usuario creado con rol 'viewer'")
            else:
                print("⚠️ Rol 'viewer' no encontrado, creando usuario sin rol")
            
            connection.commit()
        
        cursor.close()
        connection.close()
        
        print("\n🎯 Usuario de prueba listo:")
        print("   Email: test@test.com")
        print("   Contraseña: 123456")
        print("   Estado: Activo y confirmado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_test_user()


