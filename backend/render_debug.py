#!/usr/bin/env python3
"""
Script de diagnóstico específico para Render
Verifica las variables de entorno y la conexión a Supabase
"""

import os
import psycopg2
import sys
from datetime import datetime

def log(message):
    """Función de logging con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def main():
    log("🚀 INICIANDO DIAGNÓSTICO DE RENDER")
    log("=" * 50)
    
    # Verificar variables de entorno
    log("🔍 VERIFICANDO VARIABLES DE ENTORNO")
    log("-" * 30)
    
    env_vars = {
        'SUPABASE_HOST': os.environ.get('SUPABASE_HOST'),
        'SUPABASE_PORT': os.environ.get('SUPABASE_PORT'),
        'SUPABASE_DB': os.environ.get('SUPABASE_DB'),
        'SUPABASE_USER': os.environ.get('SUPABASE_USER'),
        'SUPABASE_DB_PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD'),
        'SUPABASE_URL': os.environ.get('SUPABASE_URL'),
        'SUPABASE_KEY': os.environ.get('SUPABASE_KEY')
    }
    
    for var_name, var_value in env_vars.items():
        if var_value:
            if 'PASSWORD' in var_name or 'KEY' in var_name:
                log(f"✅ {var_name}: {'*' * len(var_value)}")
            else:
                log(f"✅ {var_name}: {var_value}")
        else:
            log(f"❌ {var_name}: NO CONFIGURADA")
    
    # Verificar que todas las variables necesarias estén presentes
    required_vars = ['SUPABASE_HOST', 'SUPABASE_PORT', 'SUPABASE_DB', 'SUPABASE_USER', 'SUPABASE_DB_PASSWORD']
    missing_vars = [var for var in required_vars if not env_vars[var]]
    
    if missing_vars:
        log(f"❌ VARIABLES FALTANTES: {', '.join(missing_vars)}")
        sys.exit(1)
    
    log("✅ Todas las variables de entorno están configuradas")
    
    # Construir URL de conexión
    log("\n🔗 CONSTRUYENDO URL DE CONEXIÓN")
    log("-" * 30)
    
    host = env_vars['SUPABASE_HOST']
    port = env_vars['SUPABASE_PORT']
    db = env_vars['SUPABASE_DB']
    user = env_vars['SUPABASE_USER']
    password = env_vars['SUPABASE_DB_PASSWORD']
    
    connection_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    log(f"🔗 URL: {connection_url.replace(password, '***')}")
    
    # Probar conexión
    log("\n🔄 PROBANDO CONEXIÓN A SUPABASE")
    log("-" * 30)
    
    try:
        log("Conectando a Supabase...")
        conn = psycopg2.connect(connection_url)
        cursor = conn.cursor()
        
        log("✅ Conexión establecida exitosamente")
        
        # Verificar información de la conexión
        cursor.execute("SELECT current_user, current_database(), version();")
        current_user, current_db, version = cursor.fetchone()
        
        log(f"👤 Usuario actual: {current_user}")
        log(f"🗄️  Base de datos actual: {current_db}")
        log(f"📊 Versión PostgreSQL: {version}")
        
        # Verificar tablas
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        log(f"📋 Tablas en esquema público: {table_count}")
        
        # Probar consulta a usuarios
        cursor.execute('SELECT COUNT(*) FROM "user";')
        user_count = cursor.fetchone()[0]
        log(f"👥 Usuarios en la base de datos: {user_count}")
        
        cursor.close()
        conn.close()
        
        log("\n🎉 ¡DIAGNÓSTICO EXITOSO!")
        log("✅ La conexión a Supabase funciona correctamente")
        log("✅ Todas las configuraciones son válidas")
        
        return True
        
    except psycopg2.Error as e:
        log(f"\n❌ ERROR DE CONEXIÓN: {e}")
        log("\n🔍 INFORMACIÓN DEL ERROR:")
        log(f"   - Tipo: {type(e).__name__}")
        log(f"   - Mensaje: {str(e)}")
        
        # Análisis específico del error
        error_msg = str(e).lower()
        if "tenant or user not found" in error_msg:
            log("\n💡 ANÁLISIS DEL ERROR 'Tenant or user not found':")
            log("   - El pooler no puede encontrar el proyecto o usuario")
            log("   - Posibles causas:")
            log("     * Usuario incorrecto (debe ser postgres.PROJECT_ID)")
            log("     * Proyecto pausado o suspendido")
            log("     * Configuración del pooler incorrecta")
            log("     * Problema de sincronización en Render")
        elif "password authentication failed" in error_msg:
            log("\n💡 ANÁLISIS DEL ERROR 'Password authentication failed':")
            log("   - La contraseña es incorrecta")
            log("   - Verificar SUPABASE_DB_PASSWORD en Render")
        elif "connection refused" in error_msg:
            log("\n💡 ANÁLISIS DEL ERROR 'Connection refused':")
            log("   - No se puede conectar al servidor")
            log("   - Verificar SUPABASE_HOST y SUPABASE_PORT")
        
        return False
    
    except Exception as e:
        log(f"\n❌ ERROR INESPERADO: {e}")
        log(f"   - Tipo: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
