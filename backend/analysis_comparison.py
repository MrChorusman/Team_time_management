#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis comparativo: Documentación vs Supabase vs Código vs Lo que creé
"""

def analyze_tables():
    """Análisis completo de las tablas"""
    
    print("=" * 80)
    print("📊 ANÁLISIS COMPARATIVO DE TABLAS")
    print("=" * 80)
    
    # Tablas según documentación (ANALISIS_COMPLETO_CONTROL_HORARIO)
    documented_tables = {
        'holidays_new': 'Días festivos nuevos (589 registros)',
        'cities': 'Ciudades (201 registros)',
        'countries': 'Países (188 registros)', 
        'autonomous_communities': 'Comunidades autónomas (74 registros)',
        'holidays': 'Días festivos (63 registros)',
        'provinces': 'Provincias (52 registros)',
        'roles': 'Roles de usuario (5 registros)',
        'employees': 'Empleados (4 registros)',
        'roles_users': 'Relación usuarios-roles (4 registros)',
        'users': 'Usuarios del sistema (4 registros)',
        'calendar_entries': 'Entradas de calendario (0 registros)'
    }
    
    # Tablas existentes en Supabase (según verificación)
    existing_tables = {
        'autonomous_communities': '74 registros',
        'calendar_activity': '0 registros', 
        'calendar_entries': '0 registros',
        'cities': '201 registros',
        'countries': '188 registros',
        'employee': '0 registros',
        'employees': '4 registros',
        'holiday': '0 registros',
        'holidays_new': '589 registros',
        'notification': '0 registros',
        'provinces': '52 registros',
        'role': '0 registros',
        'roles': '5 registros',
        'roles_users': '4 registros',
        'team': '0 registros',
        'user': '1 registros',
        'users': '5 registros'
    }
    
    # Tablas según modelos del código
    code_models = {
        'user': 'User model (user.py)',
        'role': 'Role model (user.py)', 
        'roles_users': 'Tabla de asociación (user.py)',
        'employee': 'Employee model (employee.py)',
        'team': 'Team model (team.py)',
        'calendar_activity': 'CalendarActivity model (calendar_activity.py)',
        'holiday': 'Holiday model (holiday.py)',
        'notification': 'Notification model (notification.py)'
    }
    
    # Tablas que creé en el script de migración
    created_tables = {
        'role': 'Tabla de roles',
        'user': 'Tabla de usuarios', 
        'roles_users': 'Tabla de relación usuarios-roles',
        'team': 'Tabla de equipos',
        'employee': 'Tabla de empleados',
        'holiday': 'Tabla de festivos',
        'calendar_activity': 'Tabla de actividades de calendario',
        'notification': 'Tabla de notificaciones'
    }
    
    print("\n1️⃣ TABLAS SEGÚN DOCUMENTACIÓN:")
    print("-" * 40)
    for table, desc in documented_tables.items():
        print(f"  {table:<25} - {desc}")
    
    print("\n2️⃣ TABLAS EXISTENTES EN SUPABASE:")
    print("-" * 40)
    for table, desc in existing_tables.items():
        print(f"  {table:<25} - {desc}")
    
    print("\n3️⃣ TABLAS SEGÚN MODELOS DEL CÓDIGO:")
    print("-" * 40)
    for table, desc in code_models.items():
        print(f"  {table:<25} - {desc}")
    
    print("\n4️⃣ TABLAS QUE CREÉ EN LA MIGRACIÓN:")
    print("-" * 40)
    for table, desc in created_tables.items():
        print(f"  {table:<25} - {desc}")
    
    # Análisis de diferencias
    print("\n" + "=" * 80)
    print("🔍 ANÁLISIS DE DIFERENCIAS")
    print("=" * 80)
    
    # Tablas que están en documentación pero no en Supabase
    documented_not_in_supabase = set(documented_tables.keys()) - set(existing_tables.keys())
    if documented_not_in_supabase:
        print(f"\n❌ TABLAS EN DOCUMENTACIÓN PERO NO EN SUPABASE:")
        for table in documented_not_in_supabase:
            print(f"  - {table}")
    
    # Tablas que están en Supabase pero no en documentación
    supabase_not_in_documented = set(existing_tables.keys()) - set(documented_tables.keys())
    if supabase_not_in_documented:
        print(f"\n⚠️  TABLAS EN SUPABASE PERO NO EN DOCUMENTACIÓN:")
        for table in supabase_not_in_documented:
            print(f"  - {table}")
    
    # Tablas que están en código pero no en Supabase
    code_not_in_supabase = set(code_models.keys()) - set(existing_tables.keys())
    if code_not_in_supabase:
        print(f"\n❌ TABLAS EN CÓDIGO PERO NO EN SUPABASE:")
        for table in code_not_in_supabase:
            print(f"  - {table}")
    
    # Tablas que creé innecesariamente
    created_unnecessarily = set(created_tables.keys()) & set(existing_tables.keys())
    if created_unnecessarily:
        print(f"\n🔄 TABLAS QUE CREÉ INNECESARIAMENTE (ya existían):")
        for table in created_unnecessarily:
            print(f"  - {table}")
    
    # Análisis de nomenclatura
    print("\n" + "=" * 80)
    print("📝 ANÁLISIS DE NOMENCLATURA")
    print("=" * 80)
    
    naming_conflicts = {
        'users vs user': 'Documentación dice "users", código dice "user"',
        'employees vs employee': 'Documentación dice "employees", código dice "employee", Supabase tiene ambos',
        'roles vs role': 'Documentación dice "roles", código dice "role", Supabase tiene ambos',
        'holidays vs holiday': 'Documentación dice "holidays", código dice "holiday", Supabase tiene ambos',
        'calendar_entries vs calendar_activity': 'Documentación dice "calendar_entries", código dice "calendar_activity", Supabase tiene ambos'
    }
    
    for conflict, description in naming_conflicts.items():
        print(f"\n⚠️  {conflict}:")
        print(f"    {description}")
    
    # Propuesta de solución
    print("\n" + "=" * 80)
    print("💡 PROPUESTA DE SOLUCIÓN")
    print("=" * 80)
    
    print("\n1️⃣ PROBLEMAS IDENTIFICADOS:")
    print("   ❌ Creé tablas que ya existían en Supabase")
    print("   ❌ Inconsistencia en nombres de tablas entre documentación y código")
    print("   ❌ Supabase tiene tanto versiones singulares como plurales")
    print("   ❌ No revisé la documentación antes de crear las tablas")
    
    print("\n2️⃣ SOLUCIONES PROPUESTAS:")
    print("   ✅ Eliminar las tablas duplicadas que creé")
    print("   ✅ Usar las tablas existentes en Supabase")
    print("   ✅ Estandarizar nomenclatura según el código")
    print("   ✅ Actualizar la configuración para usar las tablas correctas")
    
    print("\n3️⃣ TABLAS A USAR (según código):")
    correct_tables = {
        'user': 'Usar tabla "user" (no "users")',
        'role': 'Usar tabla "role" (no "roles")', 
        'employee': 'Usar tabla "employee" (no "employees")',
        'team': 'Usar tabla "team"',
        'holiday': 'Usar tabla "holiday" (no "holidays")',
        'calendar_activity': 'Usar tabla "calendar_activity" (no "calendar_entries")',
        'notification': 'Usar tabla "notification"'
    }
    
    for table, instruction in correct_tables.items():
        print(f"   ✅ {table:<20} - {instruction}")
    
    print("\n4️⃣ ACCIONES INMEDIATAS:")
    print("   1. Eliminar tablas duplicadas creadas")
    print("   2. Verificar que los modelos usen las tablas correctas")
    print("   3. Actualizar configuración de Supabase")
    print("   4. Probar conexión con tablas existentes")

if __name__ == '__main__':
    analyze_tables()
