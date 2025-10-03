#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para probar conexión a Supabase
"""

import os
import sys

def test_supabase_connection():
    """Probar conexión a Supabase"""
    print "Probando conexion a Supabase..."
    
    # Variables de entorno
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    password = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print "URL:", url
    print "Host: aws-0-eu-west-1.pooler.supabase.com"
    print "Password configurado:", "SI" if password else "NO"
    
    # Construir URL de conexión
    db_url = "postgresql://postgres:{}@aws-0-eu-west-1.pooler.supabase.com:5432/postgres".format(password)
    print "URL de conexion generada correctamente"
    print "URL (enmascarada):", db_url.replace(password, "***")
    
    # Probar conexión con sqlalchemy
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url, echo=False)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print "Conexion exitosa a PostgreSQL"
            print "Version:", version
            
            # Probar consulta de información del esquema
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print "Base de datos:", db_name
            
            return True
            
    except Exception as e:
        print "Error de conexion:", str(e)
        return False

if __name__ == '__main__':
    test_supabase_connection()
