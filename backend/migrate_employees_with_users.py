#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar empleados creando usuarios automáticamente
"""

import psycopg2
import uuid
from datetime import datetime

def migrate_employees_with_users():
    """Migrar empleados creando usuarios automáticamente"""
    
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔄 MIGRANDO EMPLEADOS CON USUARIOS AUTOMÁTICOS")
        print("=" * 60)
        
        # Obtener empleados sin usuarios
        cursor.execute("SELECT id, team_name, full_name FROM employees")
        employees = cursor.fetchall()
        
        print(f"📊 Empleados a migrar: {len(employees)}")
        
        employee_user_map = {}
        
        for emp_id, team_name, full_name in employees:
            print(f"\n👤 Procesando: {full_name}")
            
            # Crear email automático basado en el nombre
            name_parts = full_name.lower().split()
            if len(name_parts) >= 2:
                email = f"{name_parts[0]}.{name_parts[-1]}@company.com"
            else:
                email = f"{name_parts[0]}@company.com"
            
            # Verificar si el email ya existe
            cursor.execute('SELECT COUNT(*) FROM "user" WHERE email = %s', (email,))
            if cursor.fetchone()[0] > 0:
                # Si existe, agregar número
                counter = 1
                base_email = email
                while True:
                    email = f"{base_email.split('@')[0]}{counter}@{base_email.split('@')[1]}"
                    cursor.execute('SELECT COUNT(*) FROM "user" WHERE email = %s', (email,))
                    if cursor.fetchone()[0] == 0:
                        break
                    counter += 1
            
            # Crear usuario
            fs_uniquifier = uuid.uuid4().hex
            password_hash = "$2b$12$dummy.hash.for.employees"  # Hash dummy, se debe cambiar
            
            cursor.execute("""
                INSERT INTO "user" (
                    email, password, active, fs_uniquifier, first_name, last_name,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                email, password_hash, True, fs_uniquifier,
                full_name.split()[0] if len(full_name.split()) > 0 else full_name,
                full_name.split()[-1] if len(full_name.split()) > 1 else '',
                datetime.now(), datetime.now()
            ))
            
            user_id = cursor.fetchone()[0]
            employee_user_map[emp_id] = user_id
            
            print(f"  ✅ Usuario creado: {email} (ID: {user_id})")
        
        # Ahora migrar empleados con sus user_id
        print(f"\n🔄 Migrando empleados con user_id...")
        
        # Crear equipos si no existen
        cursor.execute("SELECT DISTINCT team_name FROM employees")
        teams = cursor.fetchall()
        
        team_map = {}
        for team_name, in teams:
            cursor.execute("""
                INSERT INTO team (name, description) 
                VALUES (%s, 'Migrado automáticamente')
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """, (team_name,))
            
            result = cursor.fetchone()
            if result:
                team_id = result[0]
            else:
                cursor.execute("SELECT id FROM team WHERE name = %s", (team_name,))
                team_id = cursor.fetchone()[0]
            
            team_map[team_name] = team_id
        
        # Obtener información geográfica
        country_map = {}
        region_map = {}
        city_map = {}
        
        try:
            cursor.execute("SELECT id, name FROM countries")
            country_map = dict(cursor.fetchall())
            
            cursor.execute("SELECT id, name FROM autonomous_communities")
            region_map = dict(cursor.fetchall())
            
            cursor.execute("SELECT id, name FROM cities")
            city_map = dict(cursor.fetchall())
            
        except Exception as e:
            print(f"⚠️  Error obteniendo datos geográficos: {e}")
        
        # Migrar empleados
        for emp_id, team_name, full_name in employees:
            cursor.execute("""
                INSERT INTO employee (
                    id, user_id, full_name, team_id, hours_monday_thursday, hours_friday,
                    annual_vacation_days, annual_hld_hours, country, region, city,
                    active, approved, created_at, updated_at
                )
                SELECT 
                    e.id, %s as user_id, e.full_name, %s as team_id,
                    e.hours_mon_thu as hours_monday_thursday,
                    e.hours_fri as hours_friday,
                    e.vacation_days as annual_vacation_days,
                    e.free_hours as annual_hld_hours,
                    COALESCE(c.name, e.autonomous_community) as country,
                    COALESCE(ac.name, NULL) as region,
                    COALESCE(ci.name, e.local_city) as city,
                    true as active, false as approved,
                    e.created_at, e.updated_at
                FROM employees e
                LEFT JOIN countries c ON e.country_id = c.id
                LEFT JOIN autonomous_communities ac ON e.autonomous_community_id = ac.id
                LEFT JOIN cities ci ON e.city_id = ci.id
                WHERE e.id = %s
            """, (employee_user_map[emp_id], team_map[team_name], emp_id))
            
            print(f"  ✅ Empleado migrado: {full_name} -> Usuario ID {employee_user_map[emp_id]}")
        
        conn.commit()
        
        # Verificar migración
        cursor.execute("SELECT COUNT(*) FROM employee")
        count_after = cursor.fetchone()[0]
        print(f"\n✅ Verificación: {count_after} empleados en tabla employee")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 MIGRACIÓN DE EMPLEADOS COMPLETADA")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    migrate_employees_with_users()
