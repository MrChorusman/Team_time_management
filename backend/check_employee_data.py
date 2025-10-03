#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar datos de empleados y usuarios
"""

import psycopg2

def check_employee_data():
    """Verificar datos de empleados y usuarios"""
    
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📊 DATOS EN TABLA employees:")
        print("=" * 50)
        cursor.execute("SELECT id, team_name, full_name FROM employees")
        employees = cursor.fetchall()
        for emp_id, team, name in employees:
            print(f"  ID: {emp_id}, Equipo: {team}, Nombre: {name}")
        
        print("\n📊 DATOS EN TABLA users:")
        print("=" * 50)
        cursor.execute("SELECT id, email, full_name FROM users")
        users = cursor.fetchall()
        for user_id, email, name in users:
            print(f"  ID: {user_id}, Email: {email}, Nombre: {name}")
        
        print("\n📊 DATOS EN TABLA user (nueva):")
        print("=" * 50)
        cursor.execute('SELECT id, email, first_name, last_name FROM "user"')
        new_users = cursor.fetchall()
        for user_id, email, first_name, last_name in new_users:
            full_name = f"{first_name} {last_name}" if first_name and last_name else email
            print(f"  ID: {user_id}, Email: {email}, Nombre: {full_name}")
        
        # Intentar hacer matching por nombres
        print("\n🔍 MATCHING EMPLEADOS CON USUARIOS:")
        print("=" * 50)
        
        for emp_id, emp_team, emp_name in employees:
            # Buscar usuario con nombre similar
            cursor.execute('''
                SELECT id, email, first_name, last_name 
                FROM "user" 
                WHERE first_name ILIKE %s OR last_name ILIKE %s
                OR (first_name || ' ' || last_name) ILIKE %s
            ''', (f'%{emp_name.split()[0]}%', f'%{emp_name.split()[-1]}%', f'%{emp_name}%'))
            
            matches = cursor.fetchall()
            if matches:
                for user_id, email, first_name, last_name in matches:
                    full_name = f"{first_name} {last_name}" if first_name and last_name else email
                    print(f"  ✅ {emp_name} -> {full_name} (ID: {user_id})")
            else:
                print(f"  ❌ {emp_name} -> No encontrado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_employee_data()
