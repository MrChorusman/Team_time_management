#!/usr/bin/env python3
"""
Script para migrar datos de producción a desarrollo usando conexiones directas
"""

import psycopg2
import json
from datetime import datetime

def migrate_production_to_development():
    """Migrar datos de producción a desarrollo"""
    
    print("🔄 MIGRACIÓN DE DATOS: PRODUCCIÓN → DESARROLLO")
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
        'port': '6543',  # Transaction Pooler para desarrollo
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

def verify_migration():
    """Verificar que la migración fue exitosa"""
    
    print("\n🔍 VERIFICANDO MIGRACIÓN...")
    print("=" * 30)
    
    DEV_CONFIG = {
        'host': 'aws-0-eu-west-3.pooler.supabase.com',
        'port': '6543',
        'database': 'postgres',
        'user': 'postgres.qsbvoyjqfrhaqncqtknv',
        'password': 'Littletosti29.'
    }
    
    try:
        conn = psycopg2.connect(**DEV_CONFIG)
        cursor = conn.cursor()
        
        # Verificar tablas principales
        tables_to_check = ['user', 'role', 'team', 'employee']
        
        for table in tables_to_check:
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} registros")
        
        # Verificar usuario de prueba
        cursor.execute('SELECT email, active FROM "user" WHERE email = %s', ('admin@example.com',))
        user = cursor.fetchone()
        
        if user:
            print(f"   ✅ Usuario admin@example.com: {'Activo' if user[1] else 'Inactivo'}")
        else:
            print("   ⚠️  Usuario admin@example.com no encontrado")
        
        cursor.close()
        conn.close()
        
        print("✅ Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO MIGRACIÓN DE DATOS")
    print("=" * 40)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = migrate_production_to_development()
    
    if success:
        verify_migration()
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Probar login en entorno de desarrollo")
        print("   2. Verificar que todos los datos están correctos")
        print("   3. Usar entorno de desarrollo para testing")
    else:
        print("\n❌ La migración falló. Revisa los errores arriba.")
        exit(1)
