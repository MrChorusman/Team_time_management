#!/usr/bin/env python3
"""Script para actualizar contraseña usando Werkzeug"""
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Generar hash con método compatible con Python 3.8
password_hash = generate_password_hash("test123", method='pbkdf2:sha256', salt_length=16)
print(f"Nuevo hash generado")

# Verificar localmente que funciona
if check_password_hash(password_hash, "test123"):
    print("✅ Hash verificado localmente")
    
    # Actualizar en Supabase
    try:
        conn = psycopg2.connect(
            host=os.environ.get('SUPABASE_HOST'),
            port=os.environ.get('SUPABASE_PORT'),
            database=os.environ.get('SUPABASE_DB'),
            user=os.environ.get('SUPABASE_USER'),
            password=os.environ.get('SUPABASE_DB_PASSWORD')
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE "user" 
            SET password = %s 
            WHERE email = 'admin@example.com'
            RETURNING id, email
        """, (password_hash,))
        
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if result:
            print(f"✅ Contraseña actualizada para: {result[1]}")
            print(f"\n📋 Credenciales:")
            print(f"   Email: admin@example.com")
            print(f"   Password: test123")
        else:
            print("❌ No se encontró el usuario")
            
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Error verificando hash localmente")

