#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la secuencia de usuarios
"""

import psycopg2

def fix_user_sequence():
    """Corregir la secuencia de usuarios"""
    
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔧 CORRIGIENDO SECUENCIA DE USUARIOS")
        print("=" * 50)
        
        # Obtener el máximo ID actual
        cursor.execute('SELECT MAX(id) FROM "user"')
        max_id = cursor.fetchone()[0]
        
        print(f"📊 Máximo ID actual: {max_id}")
        
        # Actualizar la secuencia
        cursor.execute(f'SELECT setval(\'user_id_seq\', {max_id})')
        new_seq = cursor.fetchone()[0]
        
        print(f"✅ Secuencia actualizada a: {new_seq}")
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("🎉 Secuencia corregida")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    fix_user_sequence()
