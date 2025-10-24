#!/usr/bin/env python3
"""
Script para migrar datos de producción a desarrollo
Conecta a ambos proyectos Supabase y migra los datos
"""

import psycopg2
import os
from dotenv import load_dotenv

def migrate_production_to_development():
    """Migrar datos de producción a desarrollo"""
    
    print("🔄 MIGRACIÓN DE DATOS: PRODUCCIÓN → DESARROLLO")
    print("==============================================")
    
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
        for table in tables:
            print(f"\n📊 Migrando tabla: {table}")
            
            # Obtener datos de producción
            prod_cursor.execute(f"SELECT * FROM \"{table}\"")
            rows = prod_cursor.fetchall()
            
            if not rows:
                print(f"   ⚠️  Tabla {table} está vacía, saltando...")
                continue
            
            # Obtener columnas
            prod_cursor.execute(f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = '{table}' AND table_schema = 'public'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in prod_cursor.fetchall()]
            
            print(f"   📝 {len(rows)} filas, {len(columns)} columnas")
            
            # Limpiar tabla de desarrollo
            dev_cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
            
            # Insertar datos
            if rows:
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f'INSERT INTO "{table}" ({", ".join(columns)}) VALUES ({placeholders})'
                
                dev_cursor.executemany(insert_query, rows)
                dev_conn.commit()
                print(f"   ✅ {len(rows)} filas migradas")
        
        # Cerrar conexiones
        prod_cursor.close()
        prod_conn.close()
        dev_cursor.close()
        dev_conn.close()
        
        print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("✅ Todos los datos han sido migrados de producción a desarrollo")
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = migrate_production_to_development()
    if not success:
        exit(1)
