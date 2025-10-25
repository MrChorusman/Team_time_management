#!/usr/bin/env python3
"""
Script para configurar el proyecto de desarrollo y migrar datos
"""

import requests
import psycopg2
import json
from datetime import datetime

def setup_development_project():
    """Configurar el proyecto de desarrollo usando API REST"""
    
    print("🔧 CONFIGURANDO PROYECTO DE DESARROLLO")
    print("=" * 40)
    
    # Credenciales del proyecto de desarrollo
    DEV_PROJECT_URL = "https://qsbvoyjqfrhaqncqtknv.supabase.co"
    DEV_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k"
    
    headers = {
        'apikey': DEV_ANON_KEY,
        'Authorization': f"Bearer {DEV_ANON_KEY}",
        'Content-Type': 'application/json'
    }
    
    print(f"📍 Proyecto: {DEV_PROJECT_URL}")
    
    # Verificar estado del proyecto
    try:
        print("🔍 Verificando estado del proyecto...")
        response = requests.get(f"{DEV_PROJECT_URL}/rest/v1/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Proyecto activo y funcionando")
        else:
            print(f"⚠️  Estado del proyecto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando proyecto: {e}")
        return False
    
    # Crear tablas usando SQL directo
    print("\n📋 Creando estructura de tablas...")
    
    # SQL para crear las tablas principales
    create_tables_sql = """
    -- Crear tabla de usuarios
    CREATE TABLE IF NOT EXISTS "user" (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(255) UNIQUE,
        password VARCHAR(255) NOT NULL,
        confirmed_at TIMESTAMP,
        fs_uniquifier VARCHAR(255) UNIQUE,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        last_login_at TIMESTAMP,
        current_login_at TIMESTAMP,
        last_login_ip VARCHAR(255),
        current_login_ip VARCHAR(255),
        login_count INTEGER,
        active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de roles
    CREATE TABLE IF NOT EXISTS "role" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        description VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de relación usuarios-roles
    CREATE TABLE IF NOT EXISTS "roles_users" (
        user_id INTEGER REFERENCES "user"(id),
        role_id INTEGER REFERENCES "role"(id),
        PRIMARY KEY (user_id, role_id)
    );
    
    -- Crear tabla de equipos
    CREATE TABLE IF NOT EXISTS "team" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de empleados
    CREATE TABLE IF NOT EXISTS "employee" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES "user"(id),
        full_name VARCHAR(255) NOT NULL,
        team_id INTEGER REFERENCES "team"(id),
        hours_monday_thursday DOUBLE PRECISION DEFAULT 8.0,
        hours_friday DOUBLE PRECISION DEFAULT 7.0,
        has_summer_schedule BOOLEAN DEFAULT false,
        hours_summer DOUBLE PRECISION,
        summer_months TEXT,
        annual_vacation_days INTEGER DEFAULT 22,
        annual_hld_hours INTEGER DEFAULT 40,
        country VARCHAR(255),
        region VARCHAR(255),
        city VARCHAR(255),
        active BOOLEAN DEFAULT true,
        approved BOOLEAN DEFAULT false,
        approved_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de actividades de calendario
    CREATE TABLE IF NOT EXISTS "calendar_activity" (
        id SERIAL PRIMARY KEY,
        employee_id INTEGER REFERENCES "employee"(id),
        date DATE NOT NULL,
        activity_type VARCHAR(255) NOT NULL,
        hours DOUBLE PRECISION,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de notificaciones
    CREATE TABLE IF NOT EXISTS "notification" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user"(id),
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        notification_type VARCHAR(255) NOT NULL,
        priority VARCHAR(255) DEFAULT 'medium',
        read BOOLEAN DEFAULT false,
        read_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de países
    CREATE TABLE IF NOT EXISTS "countries" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        code VARCHAR(255) UNIQUE NOT NULL,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de comunidades autónomas
    CREATE TABLE IF NOT EXISTS "autonomous_communities" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        country_id INTEGER REFERENCES "countries"(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de provincias
    CREATE TABLE IF NOT EXISTS "provinces" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        autonomous_community_id INTEGER REFERENCES "autonomous_communities"(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de ciudades
    CREATE TABLE IF NOT EXISTS "cities" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        autonomous_community_id INTEGER REFERENCES "autonomous_communities"(id),
        postal_code VARCHAR(255),
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de vacaciones
    CREATE TABLE IF NOT EXISTS "holiday" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        date DATE NOT NULL,
        country VARCHAR(255) NOT NULL,
        region VARCHAR(255),
        city VARCHAR(255),
        description TEXT,
        source VARCHAR(255),
        source_id VARCHAR(255),
        holiday_type VARCHAR(255) DEFAULT 'national',
        is_fixed BOOLEAN DEFAULT true,
        active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de entradas de calendario
    CREATE TABLE IF NOT EXISTS "calendar_entries" (
        id SERIAL PRIMARY KEY,
        employee_id INTEGER NOT NULL,
        date DATE NOT NULL,
        activity_type VARCHAR(255) NOT NULL,
        hours DOUBLE PRECISION,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    print("⚠️  IMPORTANTE: Necesitas ejecutar este SQL manualmente en Supabase")
    print("📍 Ve a: https://qsbvoyjqfrhaqncqtknv.supabase.co")
    print("🔧 Ve a SQL Editor y ejecuta el siguiente SQL:")
    print("\n" + "="*50)
    print(create_tables_sql)
    print("="*50)
    
    return True

def migrate_data_after_setup():
    """Migrar datos después de configurar las tablas"""
    
    print("\n🔄 MIGRACIÓN DE DATOS: PRODUCCIÓN → DESARROLLO")
    print("=" * 50)
    
    # Configuración de producción
    PROD_CONFIG = {
        'host': 'aws-0-eu-west-3.pooler.supabase.com',
        'port': '6543',
        'database': 'postgres',
        'user': 'postgres.xmaxohyxgsthligskjvg',
        'password': 'Littletosti29.'
    }
    
    # Configuración de desarrollo
    DEV_CONFIG = {
        'host': 'aws-0-eu-west-3.pooler.supabase.com',
        'port': '5432',  # Session Pooler para desarrollo
        'database': 'postgres',
        'user': 'postgres.qsbvoyjqfrhaqncqtknv',
        'password': 'Littletosti29.'
    }
    
    try:
        print("🔗 Conectando a producción...")
        prod_conn = psycopg2.connect(**PROD_CONFIG)
        prod_cursor = prod_conn.cursor()
        print("✅ Conectado a producción")
        
        print("🔗 Conectando a desarrollo...")
        dev_conn = psycopg2.connect(**DEV_CONFIG)
        dev_cursor = dev_conn.cursor()
        print("✅ Conectado a desarrollo")
        
        # Obtener estructura de tablas de producción
        print("\n📋 Obteniendo estructura de tablas...")
        prod_cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in prod_cursor.fetchall()]
        print(f"✅ Encontradas {len(tables)} tablas: {', '.join(tables)}")
        
        # Migrar datos de cada tabla
        migration_stats = {}
        
        for table in tables:
            print(f"\n📊 Migrando tabla: {table}")
            
            # Obtener datos de producción
            prod_cursor.execute(f"SELECT * FROM \"{table}\"")
            rows = prod_cursor.fetchall()
            
            if not rows:
                print(f"   ⚠️  Tabla {table} está vacía, saltando...")
                migration_stats[table] = 0
                continue
            
            # Obtener columnas
            prod_cursor.execute(f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = '{table}' AND table_schema = 'public'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in prod_cursor.fetchall()]
            
            print(f"   📝 {len(rows)} filas, {len(columns)} columnas")
            
            try:
                # Limpiar tabla de desarrollo
                dev_cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
                
                # Insertar datos
                if rows:
                    placeholders = ', '.join(['%s'] * len(columns))
                    insert_query = f'INSERT INTO "{table}" ({", ".join(columns)}) VALUES ({placeholders})'
                    
                    dev_cursor.executemany(insert_query, rows)
                    dev_conn.commit()
                    print(f"   ✅ {len(rows)} filas migradas")
                    migration_stats[table] = len(rows)
                    
            except Exception as e:
                print(f"   ❌ Error migrando {table}: {e}")
                migration_stats[table] = f"Error: {e}"
                dev_conn.rollback()
        
        # Cerrar conexiones
        prod_cursor.close()
        prod_conn.close()
        dev_cursor.close()
        dev_conn.close()
        
        # Mostrar resumen
        print("\n📊 RESUMEN DE MIGRACIÓN:")
        print("=" * 30)
        total_migrated = 0
        for table, count in migration_stats.items():
            if isinstance(count, int):
                print(f"   {table}: {count} filas")
                total_migrated += count
            else:
                print(f"   {table}: {count}")
        
        print(f"\n🎉 ¡MIGRACIÓN COMPLETADA!")
        print(f"✅ Total de filas migradas: {total_migrated}")
        print(f"✅ Proyecto de desarrollo actualizado con datos de producción")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    print("🚀 CONFIGURACIÓN Y MIGRACIÓN DEL PROYECTO DE DESARROLLO")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar si se solicita migración
    if len(sys.argv) > 1 and sys.argv[1] == '--migrate':
        print("🔄 MODO MIGRACIÓN: Migrando datos de producción a desarrollo")
        success = migrate_data_after_setup()
        
        if success:
            print("\n🎉 ¡MIGRACIÓN COMPLETADA!")
            print("✅ Proyecto de desarrollo listo para usar")
        else:
            print("\n❌ Error en la migración")
            exit(1)
    else:
        # Modo configuración (crear tablas)
        setup_success = setup_development_project()
        
        if setup_success:
            print("\n🎯 PRÓXIMOS PASOS:")
            print("   1. Ve a https://qsbvoyjqfrhaqncqtknv.supabase.co")
            print("   2. Ejecuta el SQL en SQL Editor")
            print("   3. Ejecuta este script nuevamente para migrar datos")
            print("\n   Comando: python setup_and_migrate.py --migrate")
        else:
            print("\n❌ Error configurando proyecto")
            exit(1)
