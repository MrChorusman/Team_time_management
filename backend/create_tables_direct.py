#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script directo para crear tablas en Supabase usando SQLAlchemy directamente
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def create_tables_direct():
    """Crear tablas directamente en Supabase"""
    print("Creando tablas directamente en Supabase...")
    
    # URL de conexión a Supabase
    database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    
    try:
        # Crear engine
        engine = create_engine(database_url, echo=True)
        
        # Probar conexión
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Conexion exitosa: {version}")
        
        # Crear tablas usando SQL DDL
        create_tables_sql = """
        -- Tabla de roles
        CREATE TABLE IF NOT EXISTS role (
            id SERIAL PRIMARY KEY,
            name VARCHAR(80) UNIQUE NOT NULL,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de usuarios
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            confirmed_at TIMESTAMP,
            fs_uniquifier VARCHAR(64) UNIQUE NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            last_login_at TIMESTAMP,
            current_login_at TIMESTAMP,
            last_login_ip VARCHAR(100),
            current_login_ip VARCHAR(100),
            login_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de relación usuarios-roles
        CREATE TABLE IF NOT EXISTS roles_users (
            user_id INTEGER REFERENCES "user"(id),
            role_id INTEGER REFERENCES role(id),
            PRIMARY KEY (user_id, role_id)
        );
        
        -- Tabla de equipos
        CREATE TABLE IF NOT EXISTS team (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de empleados
        CREATE TABLE IF NOT EXISTS employee (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id) UNIQUE NOT NULL,
            full_name VARCHAR(200) NOT NULL,
            team_id INTEGER REFERENCES team(id) NOT NULL,
            hours_monday_thursday FLOAT NOT NULL DEFAULT 8.0,
            hours_friday FLOAT NOT NULL DEFAULT 7.0,
            hours_summer FLOAT,
            has_summer_schedule BOOLEAN DEFAULT FALSE,
            summer_months TEXT,
            annual_vacation_days INTEGER NOT NULL DEFAULT 22,
            annual_hld_hours INTEGER NOT NULL DEFAULT 40,
            country VARCHAR(100) NOT NULL,
            region VARCHAR(100),
            city VARCHAR(100),
            active BOOLEAN DEFAULT TRUE,
            approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP
        );
        
        -- Tabla de festivos
        CREATE TABLE IF NOT EXISTS holiday (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            date DATE NOT NULL,
            country VARCHAR(100) NOT NULL,
            region VARCHAR(100),
            city VARCHAR(100),
            holiday_type VARCHAR(50) DEFAULT 'national',
            description TEXT,
            is_fixed BOOLEAN DEFAULT TRUE,
            source VARCHAR(100),
            source_id VARCHAR(100),
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de actividades de calendario
        CREATE TABLE IF NOT EXISTS calendar_activity (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER REFERENCES employee(id) NOT NULL,
            date DATE NOT NULL,
            activity_type VARCHAR(10) NOT NULL,
            hours FLOAT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de notificaciones
        CREATE TABLE IF NOT EXISTS notification (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id) NOT NULL,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            notification_type VARCHAR(50) NOT NULL,
            priority VARCHAR(20) DEFAULT 'medium',
            read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP
        );
        
        -- Crear índices para optimización
        CREATE INDEX IF NOT EXISTS idx_holiday_date_country ON holiday(date, country);
        CREATE INDEX IF NOT EXISTS idx_holiday_country_region ON holiday(country, region);
        CREATE INDEX IF NOT EXISTS idx_holiday_location ON holiday(country, region, city);
        CREATE INDEX IF NOT EXISTS idx_calendar_activity_employee_date ON calendar_activity(employee_id, date);
        CREATE INDEX IF NOT EXISTS idx_notification_user_created ON notification(user_id, created_at);
        """
        
        # Ejecutar SQL para crear tablas
        with engine.connect() as connection:
            # Dividir el SQL en statements individuales
            statements = create_tables_sql.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))
            connection.commit()
        
        print("Tablas creadas exitosamente en Supabase")
        
        # Verificar tablas creadas
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = result.fetchall()
            print("\nTablas creadas:")
            for table in tables:
                print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"Error creando tablas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    create_tables_direct()
