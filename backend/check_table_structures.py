#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura de las tablas
"""

import psycopg2

def check_table_structure():
    """Verificar estructura de tablas"""
    
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        tables_to_check = ['roles', 'role', 'users', 'user', 'employees', 'employee', 'holidays_new', 'holiday']
        
        for table in tables_to_check:
            print(f"\n📋 ESTRUCTURA DE TABLA: {table}")
            print("=" * 50)
            
            try:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """, (table,))
                
                columns = cursor.fetchall()
                
                if columns:
                    for col_name, data_type, nullable, default in columns:
                        nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                        default_str = f" DEFAULT {default}" if default else ""
                        print(f"  {col_name:<25} {data_type:<20} {nullable_str}{default_str}")
                else:
                    print("  ❌ Tabla no encontrada")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == '__main__':
    check_table_structure()
