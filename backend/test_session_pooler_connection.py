#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la conexión con Supabase usando Session Pooler
Este script prueba la nueva configuración compatible con IPv4 para Render
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
load_dotenv()

def test_session_pooler_connection():
    """Prueba la conexión con Supabase usando Session Pooler"""
    
    print("🔍 Probando conexión con Supabase Session Pooler...")
    print("=" * 60)
    
    # Obtener variables de entorno
    db_host = os.environ.get('SUPABASE_HOST', 'aws-0-eu-west-3.pooler.supabase.com')
    db_port = os.environ.get('SUPABASE_PORT', '5432')
    db_name = os.environ.get('SUPABASE_DB', 'postgres')
    db_user = os.environ.get('SUPABASE_USER', 'postgres.xmaxohyxgsthligskjvg')
    db_password = os.environ.get('SUPABASE_DB_PASSWORD')
    
    print(f"📍 Host: {db_host}")
    print(f"🔌 Puerto: {db_port}")
    print(f"🗄️  Base de datos: {db_name}")
    print(f"👤 Usuario: {db_user}")
    print(f"🔑 Contraseña: {'***' if db_password else 'NO CONFIGURADA'}")
    print("-" * 60)
    
    if not db_password:
        print("❌ ERROR: SUPABASE_DB_PASSWORD no está configurado")
        return False
    
    try:
        # Construir URL de conexión
        connection_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(f"🔗 URL de conexión: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
        
        # Intentar conectar
        print("🔄 Conectando a Supabase...")
        conn = psycopg2.connect(connection_url)
        
        # Crear cursor
        cursor = conn.cursor()
        
        # Probar consulta básica
        print("📊 Ejecutando consulta de prueba...")
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Versión de PostgreSQL: {version}")
        
        # Probar consulta a tablas existentes
        print("📋 Verificando tablas existentes...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
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
        
        # Probar consulta a usuarios
        print("👥 Verificando usuarios...")
        cursor.execute("SELECT COUNT(*) FROM \"user\";")
        user_count = cursor.fetchone()[0]
        print(f"✅ Usuarios en la base de datos: {user_count}")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("=" * 60)
        print("🎉 ¡Conexión exitosa con Supabase Session Pooler!")
        print("✅ La configuración es compatible con IPv4 (Render)")
        return True
        
    except psycopg2.Error as e:
        print("=" * 60)
        print(f"❌ ERROR de conexión: {e}")
        print("🔍 Verifica que las variables de entorno estén configuradas correctamente")
        return False
    except Exception as e:
        print("=" * 60)
        print(f"❌ ERROR inesperado: {e}")
        return False

def test_environment_variables():
    """Verifica que todas las variables de entorno necesarias estén configuradas"""
    
    print("🔍 Verificando variables de entorno...")
    print("=" * 60)
    
    required_vars = {
        'SUPABASE_HOST': 'aws-0-eu-west-3.pooler.supabase.com',
        'SUPABASE_PORT': '5432',
        'SUPABASE_DB': 'postgres',
        'SUPABASE_USER': 'postgres.xmaxohyxgsthligskjvg',
        'SUPABASE_DB_PASSWORD': None,  # Debe estar configurado pero no lo mostramos
    }
    
    all_configured = True
    
    for var_name, expected_value in required_vars.items():
        actual_value = os.environ.get(var_name)
        
        if var_name == 'SUPABASE_DB_PASSWORD':
            if actual_value:
                print(f"✅ {var_name}: *** (configurado)")
            else:
                print(f"❌ {var_name}: NO CONFIGURADO")
                all_configured = False
        else:
            if actual_value == expected_value:
                print(f"✅ {var_name}: {actual_value}")
            else:
                print(f"⚠️  {var_name}: {actual_value} (esperado: {expected_value})")
    
    print("-" * 60)
    
    if all_configured:
        print("✅ Todas las variables de entorno están configuradas correctamente")
    else:
        print("❌ Algunas variables de entorno necesitan configuración")
    
    return all_configured

if __name__ == "__main__":
    print("🚀 PRUEBA DE CONEXIÓN SUPABASE SESSION POOLER")
    print("=" * 60)
    
    # Verificar variables de entorno
    env_ok = test_environment_variables()
    print()
    
    if env_ok:
        # Probar conexión
        connection_ok = test_session_pooler_connection()
        
        if connection_ok:
            print("\n🎯 RESULTADO: Configuración exitosa para Render")
            sys.exit(0)
        else:
            print("\n💥 RESULTADO: Error en la conexión")
            sys.exit(1)
    else:
        print("\n💥 RESULTADO: Variables de entorno no configuradas")
        sys.exit(1)
