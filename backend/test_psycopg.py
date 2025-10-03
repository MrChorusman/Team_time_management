#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar conexión a Supabase con psycopg2
"""

import os

def test_connection():
    """Probar conexión a Supabase"""
    print("Probando conexion a Supabase con psycopg2...")
    
    # Variables de entorno
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    password = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print("URL:", url)
    print("Host: aws-0-eu-west-3.pooler.supabase.com")
    print("Password configurado:", "SI" if password else "NO")
    
    # Probar conexión con psycopg2
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="aws-0-eu-west-3.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.xmaxohyxgsthligskjvg",
            password=password
        )
        
        print("Conexion exitosa a PostgreSQL")
        
        # Probar consulta simple
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print("Version:", version)
        
        # Probar consulta de información del esquema
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]
        print("Base de datos:", db_name)
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print("Error de conexion:", str(e))
        return False

if __name__ == '__main__':
    test_connection()
