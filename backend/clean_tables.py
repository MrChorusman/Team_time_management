#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar tablas antes de migración
"""

import psycopg2

def clean_tables():
    """Limpiar tablas para empezar migración limpia"""
    
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🧹 LIMPIANDO TABLAS PARA MIGRACIÓN")
        print("=" * 50)
        
        # Limpiar employee
        cursor.execute("DELETE FROM employee")
        print("✅ Tabla employee limpiada")
        
        # Limpiar usuarios creados automáticamente
        cursor.execute("DELETE FROM \"user\" WHERE email LIKE '%@company.com'")
        print("✅ Usuarios automáticos eliminados")
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("🎉 Limpieza completada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    clean_tables()
