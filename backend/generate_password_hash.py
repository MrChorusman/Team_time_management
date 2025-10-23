#!/usr/bin/env python3
"""
Script para generar el hash correcto de la contraseña
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Crear la aplicación Flask
    import app as app_module
    from flask_security.utils import hash_password
    
    app = app_module.create_app()
    
    with app.app_context():
        # Generar hash para la contraseña '123456'
        password = '123456'
        hashed_password = hash_password(password)
    
    print(f"🔐 Hash generado para contraseña '{password}':")
    print(f"   {hashed_password}")
    
    # Ahora actualizar en la base de datos
    import psycopg2
    
    # Obtener credenciales
    host = os.environ.get('SUPABASE_HOST')
    port = os.environ.get('SUPABASE_PORT', '6543')
    database = os.environ.get('SUPABASE_DB_NAME', 'postgres')
    user = os.environ.get('SUPABASE_DB_USER', 'postgres')
    password_db = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print("\n🔍 Actualizando contraseña en la base de datos...")
    
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
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("\n🎯 Usuario de prueba listo:")
    print("   Email: test@test.com")
    print("   Contraseña: 123456")
    print("   Hash: Generado correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
