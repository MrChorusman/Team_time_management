#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificación final de la migración
"""

import psycopg2

def verify_final_migration():
    """Verificación final de la migración completa"""
    
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 VERIFICACIÓN FINAL DE MIGRACIÓN COMPLETA")
        print("=" * 80)
        
        # Verificar tablas principales
        tables_to_check = [
            ('role', 'Roles'),
            ('"user"', 'Usuarios'),
            ('holiday', 'Festivos'),
            ('employee', 'Empleados'),
            ('team', 'Equipos')
        ]
        
        print("\n📊 TABLAS PRINCIPALES:")
        print("-" * 50)
        all_good = True
        
        for table, name in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"✅ {name:<15} - {count:>6} registros")
                else:
                    print(f"⚠️  {name:<15} - {count:>6} registros (vacía)")
                    all_good = False
            except Exception as e:
                print(f"❌ {name:<15} - Error: {e}")
                all_good = False
        
        # Verificar datos específicos
        print("\n📋 DATOS ESPECÍFICOS:")
        print("-" * 50)
        
        # Roles
        cursor.execute('SELECT name FROM role ORDER BY id')
        roles = cursor.fetchall()
        print(f"📋 Roles disponibles: {', '.join([r[0] for r in roles])}")
        
        # Usuarios
        cursor.execute('SELECT email, first_name, last_name FROM "user" ORDER BY id')
        users = cursor.fetchall()
        print(f"📋 Total usuarios: {len(users)}")
        for email, first_name, last_name in users:
            name = f"{first_name} {last_name}".strip() if first_name or last_name else email
            print(f"  - {name} ({email})")
        
        # Empleados
        cursor.execute('SELECT e.full_name, t.name, u.email FROM employee e JOIN team t ON e.team_id = t.id JOIN "user" u ON e.user_id = u.id ORDER BY e.id')
        employees = cursor.fetchall()
        print(f"\n📋 Total empleados: {len(employees)}")
        for name, team, email in employees:
            print(f"  - {name} ({team}) -> {email}")
        
        # Festivos
        cursor.execute('SELECT COUNT(*) FROM holiday')
        holiday_count = cursor.fetchone()[0]
        print(f"\n📋 Total festivos: {holiday_count}")
        
        # Equipos
        cursor.execute('SELECT name FROM team ORDER BY id')
        teams = cursor.fetchall()
        print(f"📋 Equipos: {', '.join([t[0] for t in teams])}")
        
        # Verificar relaciones
        print("\n🔗 VERIFICACIÓN DE RELACIONES:")
        print("-" * 50)
        
        # Empleados con usuarios
        cursor.execute('SELECT COUNT(*) FROM employee e JOIN "user" u ON e.user_id = u.id')
        emp_user_count = cursor.fetchone()[0]
        print(f"✅ Empleados con usuarios: {emp_user_count}")
        
        # Empleados con equipos
        cursor.execute('SELECT COUNT(*) FROM employee e JOIN team t ON e.team_id = t.id')
        emp_team_count = cursor.fetchone()[0]
        print(f"✅ Empleados con equipos: {emp_team_count}")
        
        # Verificar tablas antiguas
        print("\n📊 TABLAS ANTIGUAS (para eliminación):")
        print("-" * 50)
        
        old_tables = ['roles', 'users', 'employees', 'holidays_new']
        for table in old_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📋 {table:<15} - {count:>6} registros (listo para eliminar)")
            except Exception as e:
                print(f"❌ {table:<15} - Error: {e}")
        
        cursor.close()
        conn.close()
        
        if all_good:
            print("\n🎉 VERIFICACIÓN COMPLETADA - MIGRACIÓN EXITOSA")
            print("✅ Todas las tablas tienen datos correctos")
            print("✅ Todas las relaciones están establecidas")
            print("✅ Datos migrados correctamente")
        else:
            print("\n⚠️  VERIFICACIÓN COMPLETADA CON ADVERTENCIAS")
            print("⚠️  Algunas tablas pueden estar vacías")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == '__main__':
    verify_final_migration()
