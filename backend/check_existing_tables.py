#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las tablas existentes en Supabase
"""

import psycopg2

def check_existing_tables():
    """Verificar tablas existentes en Supabase"""
    print("Verificando tablas existentes en Supabase...")
    
    try:
        conn = psycopg2.connect(
            host='aws-0-eu-west-3.pooler.supabase.com',
            port='6543',
            database='postgres',
            user='postgres.xmaxohyxgsthligskjvg',
            password='Littletosti29.'
        )
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("""
            SELECT table_name, 
                   pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print("\nTABLAS EXISTENTES EN SUPABASE:")
        print("=" * 60)
        for table, size in tables:
            print(f"{table:<30} {size}")
        
        # Contar registros en cada tabla
        print("\nREGISTROS POR TABLA:")
        print("=" * 60)
        for table, _ in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<30} {count:>10} registros")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_existing_tables()
