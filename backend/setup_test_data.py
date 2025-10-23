#!/usr/bin/env python3
"""
Script para configurar datos de prueba para el escenario de testing
1. Borrar datos de las tablas user y employee
2. Crear usuario Admin con datos específicos
"""

import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

load_dotenv()

def get_db_connection():
    """Conectar a la base de datos Supabase"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('SUPABASE_HOST'),
            port=os.environ.get('SUPABASE_PORT', '6543'),
            database=os.environ.get('SUPABASE_DB_NAME', 'postgres'),
            user=os.environ.get('SUPABASE_DB_USER', 'postgres'),
            password=os.environ.get('SUPABASE_DB_PASSWORD')
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def clean_test_data():
    """Limpiar datos de prueba"""
    print("🧹 Limpiando datos de prueba...")
    
    conn = get_db_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Eliminar empleados
        cursor.execute("DELETE FROM employee")
        deleted_employees = cursor.rowcount
        print(f"   ✅ Eliminados {deleted_employees} empleados")
        
        # Eliminar usuarios (excepto algunos que podrían ser necesarios)
        cursor.execute("""
            DELETE FROM "user" 
            WHERE email NOT IN ('miguelchis@gmail.com', 'admin@example.com')
        """)
        deleted_users = cursor.rowcount
        print(f"   ✅ Eliminados {deleted_users} usuarios")
        
        # Resetear secuencias
        cursor.execute("ALTER SEQUENCE employee_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE \"user_id_seq\" RESTART WITH 1")
        print("   ✅ Secuencias reiniciadas")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Limpieza completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def create_admin_user():
    """Crear usuario administrador"""
    print("👤 Creando usuario administrador...")
    
    conn = get_db_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM \"user\" WHERE email = %s", ('miguelchis@gmail.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("   ⚠️  Usuario miguelchis@gmail.com ya existe, actualizando...")
            user_id = existing_user[0]
            
            # Actualizar datos del usuario
            hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256', salt_length=16)
            cursor.execute("""
                UPDATE "user" 
                SET password = %s, first_name = %s, last_name = %s, active = %s, confirmed_at = %s, updated_at = NOW()
                WHERE id = %s
            """, (hashed_password, 'Miguel', 'Chimeno', True, datetime.now(), user_id))
            
        else:
            # Crear nuevo usuario
            hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256', salt_length=16)
            cursor.execute("""
                INSERT INTO "user" (email, password, active, confirmed_at, fs_uniquifier, first_name, last_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (
                'miguelchis@gmail.com',
                hashed_password,
                True,
                datetime.now(),  # Email confirmado
                str(uuid.uuid4()),
                'Miguel',
                'Chimeno'
            ))
            
            user_id = cursor.fetchone()[0]
            print(f"   ✅ Usuario creado con ID: {user_id}")
        
        # Obtener ID del rol admin
        cursor.execute("SELECT id FROM role WHERE name = 'admin'")
        admin_role = cursor.fetchone()
        
        if not admin_role:
            print("   ❌ Rol 'admin' no encontrado en la base de datos")
            cursor.close()
            conn.close()
            return False
        
        admin_role_id = admin_role[0]
        
        # Asignar rol admin al usuario
        cursor.execute("DELETE FROM roles_users WHERE user_id = %s", (user_id,))
        cursor.execute("INSERT INTO roles_users (user_id, role_id) VALUES (%s, %s)", (user_id, admin_role_id))
        print("   ✅ Rol admin asignado")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Usuario administrador creado/actualizado exitosamente")
        print("   📧 Email: miguelchis@gmail.com")
        print("   🔑 Contraseña: admin123")
        print("   👑 Rol: Administrador")
        print("   ✅ Email verificado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def verify_setup():
    """Verificar que la configuración es correcta"""
    print("🔍 Verificando configuración...")
    
    conn = get_db_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verificar usuario admin
        cursor.execute("""
            SELECT u.id, u.email, u.first_name, u.last_name, u.active, u.confirmed_at,
                   r.name as role_name
            FROM "user" u
            JOIN roles_users ru ON u.id = ru.user_id
            JOIN role r ON ru.role_id = r.id
            WHERE u.email = 'miguelchis@gmail.com'
        """)
        
        admin_data = cursor.fetchall()
        
        if admin_data:
            print("   ✅ Usuario admin encontrado:")
            for row in admin_data:
                print(f"      ID: {row[0]}, Email: {row[1]}, Nombre: {row[2]} {row[3]}")
                print(f"      Activo: {row[4]}, Confirmado: {row[5]}, Rol: {row[6]}")
        else:
            print("   ❌ Usuario admin no encontrado")
            return False
        
        # Verificar equipos disponibles
        cursor.execute("SELECT COUNT(*) FROM team")
        team_count = cursor.fetchone()[0]
        print(f"   📊 Equipos disponibles: {team_count}")
        
        if team_count > 0:
            cursor.execute("SELECT name FROM team ORDER BY name")
            teams = cursor.fetchall()
            print("   📋 Lista de equipos:")
            for team in teams:
                print(f"      - {team[0]}")
        
        cursor.close()
        conn.close()
        
        print("✅ Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        if conn:
            conn.close()
        return False

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DE DATOS DE PRUEBA")
    print("=" * 50)
    
    # Paso 1: Limpiar datos
    if not clean_test_data():
        print("❌ Error en limpieza de datos")
        return
    
    # Paso 2: Crear usuario admin
    if not create_admin_user():
        print("❌ Error creando usuario admin")
        return
    
    # Paso 3: Verificar configuración
    if not verify_setup():
        print("❌ Error en verificación")
        return
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print("📋 RESUMEN:")
    print("   ✅ Datos de prueba limpiados")
    print("   ✅ Usuario admin creado: miguelchis@gmail.com")
    print("   ✅ Contraseña: admin123")
    print("   ✅ Email verificado")
    print("   ✅ Rol administrador asignado")
    print("\n🚀 LISTO PARA LA PRUEBA:")
    print("   1. Iniciar sesión con miguelchis@gmail.com / admin123")
    print("   2. Acceder directamente a la aplicación (sin formulario de empleado)")
    print("   3. Crear equipos desde la pantalla de Admin")

if __name__ == "__main__":
    main()



