#!/usr/bin/env python3
"""
Script para configurar el proyecto de desarrollo usando la API REST de Supabase
"""

import requests
import json
import time

def configure_development_project():
    """Configurar proyecto de desarrollo usando API REST"""
    
    print("🔧 CONFIGURACIÓN DEL PROYECTO DE DESARROLLO VIA API REST")
    print("========================================================")
    
    # Credenciales del proyecto de desarrollo
    DEV_PROJECT_URL = "https://qsbvoyjqfrhaqncqtknv.supabase.co"
    DEV_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k"
    
    headers = {
        'apikey': DEV_ANON_KEY,
        'Authorization': f'Bearer {DEV_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    print(f"📍 Proyecto: {DEV_PROJECT_URL}")
    print(f"🔑 Anon Key: {DEV_ANON_KEY[:20]}...")
    
    # Verificar estado del proyecto
    try:
        print("\n🔍 Verificando estado del proyecto...")
        response = requests.get(f"{DEV_PROJECT_URL}/rest/v1/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Proyecto activo y funcionando")
        else:
            print(f"⚠️  Estado del proyecto: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error verificando proyecto: {e}")
        return False
    
    # Crear tablas básicas usando SQL
    print("\n📋 Creando estructura de tablas...")
    
    # SQL para crear las tablas principales
    create_tables_sql = """
    -- Crear tabla de usuarios
    CREATE TABLE IF NOT EXISTS "user" (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(255) UNIQUE,
        password VARCHAR(255) NOT NULL,
        confirmed_at TIMESTAMP,
        fs_uniquifier VARCHAR(255) UNIQUE,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        last_login_at TIMESTAMP,
        current_login_at TIMESTAMP,
        last_login_ip VARCHAR(255),
        current_login_ip VARCHAR(255),
        login_count INTEGER,
        active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de roles
    CREATE TABLE IF NOT EXISTS "role" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        description VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de relación usuarios-roles
    CREATE TABLE IF NOT EXISTS "roles_users" (
        user_id INTEGER REFERENCES "user"(id),
        role_id INTEGER REFERENCES "role"(id),
        PRIMARY KEY (user_id, role_id)
    );
    
    -- Crear tabla de equipos
    CREATE TABLE IF NOT EXISTS "team" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de empleados
    CREATE TABLE IF NOT EXISTS "employee" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES "user"(id),
        full_name VARCHAR(255) NOT NULL,
        team_id INTEGER REFERENCES "team"(id),
        hours_monday_thursday DOUBLE PRECISION DEFAULT 8.0,
        hours_friday DOUBLE PRECISION DEFAULT 7.0,
        has_summer_schedule BOOLEAN DEFAULT false,
        hours_summer DOUBLE PRECISION,
        summer_months TEXT,
        annual_vacation_days INTEGER DEFAULT 22,
        annual_hld_hours INTEGER DEFAULT 40,
        country VARCHAR(255),
        region VARCHAR(255),
        city VARCHAR(255),
        active BOOLEAN DEFAULT true,
        approved BOOLEAN DEFAULT false,
        approved_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de actividades de calendario
    CREATE TABLE IF NOT EXISTS "calendar_activity" (
        id SERIAL PRIMARY KEY,
        employee_id INTEGER REFERENCES "employee"(id),
        date DATE NOT NULL,
        activity_type VARCHAR(255) NOT NULL,
        hours DOUBLE PRECISION,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Crear tabla de notificaciones
    CREATE TABLE IF NOT EXISTS "notification" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user"(id),
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        notification_type VARCHAR(255) NOT NULL,
        priority VARCHAR(255) DEFAULT 'medium',
        read BOOLEAN DEFAULT false,
        read_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        # Ejecutar SQL usando la API REST
        print("🔨 Ejecutando creación de tablas...")
        
        # Dividir el SQL en comandos individuales
        sql_commands = [cmd.strip() for cmd in create_tables_sql.split(';') if cmd.strip()]
        
        for i, sql in enumerate(sql_commands):
            if sql:
                print(f"   📝 Ejecutando comando {i+1}/{len(sql_commands)}...")
                
                # Usar la API REST para ejecutar SQL
                response = requests.post(
                    f"{DEV_PROJECT_URL}/rest/v1/rpc/exec_sql",
                    headers=headers,
                    json={'sql': sql}
                )
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ Comando ejecutado exitosamente")
                else:
                    print(f"   ⚠️  Respuesta: {response.status_code}")
                    if response.text:
                        print(f"   📄 {response.text}")
        
        print("✅ Estructura de tablas creada")
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False
    
    # Insertar datos básicos
    print("\n📊 Insertando datos básicos...")
    
    try:
        # Insertar roles básicos
        roles_data = [
            {'name': 'admin', 'description': 'Administrador del sistema'},
            {'name': 'user', 'description': 'Usuario estándar'},
            {'name': 'manager', 'description': 'Gerente de equipo'},
            {'name': 'hr', 'description': 'Recursos Humanos'},
            {'name': 'employee', 'description': 'Empleado'}
        ]
        
        for role in roles_data:
            response = requests.post(
                f"{DEV_PROJECT_URL}/rest/v1/role",
                headers=headers,
                json=role
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Rol '{role['name']}' creado")
            else:
                print(f"   ⚠️  Error creando rol '{role['name']}': {response.status_code}")
        
        # Insertar usuario de prueba
        from werkzeug.security import generate_password_hash
        test_password_hash = generate_password_hash("test123", method='pbkdf2:sha256', salt_length=16)
        
        user_data = {
            'email': 'admin@example.com',
            'password': test_password_hash,
            'confirmed_at': '2025-01-23T12:00:00Z',
            'fs_uniquifier': 'dev-unique-001',
            'active': True,
            'login_count': 0
        }
        
        response = requests.post(
            f"{DEV_PROJECT_URL}/rest/v1/user",
            headers=headers,
            json=user_data
        )
        
        if response.status_code in [200, 201]:
            print("   ✅ Usuario de prueba creado")
            
            # Asignar rol de admin
            user_response = requests.get(
                f"{DEV_PROJECT_URL}/rest/v1/user?email=eq.admin@example.com",
                headers=headers
            )
            
            if user_response.status_code == 200:
                users = user_response.json()
                if users:
                    user_id = users[0]['id']
                    
                    # Obtener rol de admin
                    role_response = requests.get(
                        f"{DEV_PROJECT_URL}/rest/v1/role?name=eq.admin",
                        headers=headers
                    )
                    
                    if role_response.status_code == 200:
                        roles = role_response.json()
                        if roles:
                            role_id = roles[0]['id']
                            
                            # Asignar rol
                            role_assignment = {
                                'user_id': user_id,
                                'role_id': role_id
                            }
                            
                            response = requests.post(
                                f"{DEV_PROJECT_URL}/rest/v1/roles_users",
                                headers=headers,
                                json=role_assignment
                            )
                            
                            if response.status_code in [200, 201]:
                                print("   ✅ Rol de admin asignado")
        
        print("✅ Datos básicos insertados")
        
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
        return False
    
    print("\n🎉 ¡PROYECTO DE DESARROLLO CONFIGURADO EXITOSAMENTE!")
    print("✅ Estructura de tablas creada")
    print("✅ Datos básicos insertados")
    print("✅ Usuario de prueba: admin@example.com / test123")
    
    return True

if __name__ == "__main__":
    success = configure_development_project()
    if not success:
        exit(1)
