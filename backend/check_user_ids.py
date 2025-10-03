#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar IDs de usuarios disponibles
"""

import psycopg2

def check_user_ids():
    """Verificar IDs de usuarios disponibles"""
    
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📊 IDs DE USUARIOS EXISTENTES:")
        print("=" * 40)
        
        cursor.execute('SELECT id, email FROM "user" ORDER BY id')
        users = cursor.fetchall()
        
        for user_id, email in users:
            print(f"  ID: {user_id}, Email: {email}")
        
        print(f"\n📊 Total usuarios: {len(users)}")
        
        # Verificar secuencia
        cursor.execute('SELECT last_value FROM user_id_seq')
        last_seq = cursor.fetchone()[0]
        print(f"📊 Último valor de secuencia: {last_seq}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_user_ids()
