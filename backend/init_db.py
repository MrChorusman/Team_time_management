#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Crea las tablas y datos iniciales necesarios para la aplicación
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app as app_module
from models.user import db
from models.user import User, Role
from models.employee import Employee
from models.team import Team
from models.holiday import Holiday
from services.holiday_service import HolidayService

def create_roles():
    """Crear los roles básicos del sistema"""
    roles = [
        {'name': 'admin', 'description': 'Administrador del sistema'},
        {'name': 'manager', 'description': 'Manager de equipo'},
        {'name': 'employee', 'description': 'Empleado'},
        {'name': 'viewer', 'description': 'Solo lectura'}
    ]
    
    for role_data in roles:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(
                name=role_data['name'],
                description=role_data['description']
            )
            db.session.add(role)
            print(f"✅ Rol creado: {role_data['name']}")
        else:
            print(f"ℹ️  Rol ya existe: {role_data['name']}")
    
    db.session.commit()

def create_admin_user():
    """Crear usuario administrador por defecto"""
    admin_role = Role.query.filter_by(name='admin').first()
    
    admin_user = User.query.filter_by(email='admin@teamtime.com').first()
    if not admin_user:
        admin_user = User(
            email='admin@teamtime.com',
            password=generate_password_hash('admin123'),
            active=True,
            confirmed_at=datetime.utcnow()
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        
        # Crear perfil de empleado para el admin
        admin_employee = Employee(
            user_id=admin_user.id,
            full_name='Administrador del Sistema',
            email='admin@teamtime.com',
            country='ES',
            region='Madrid',
            city='Madrid',
            hours_monday_thursday=8.0,
            hours_friday=6.0,
            start_date=datetime.utcnow().date(),
            approved='approved'
        )
        db.session.add(admin_employee)
        
        print("✅ Usuario administrador creado:")
        print("   Email: admin@teamtime.com")
        print("   Password: admin123")
    else:
        print("ℹ️  Usuario administrador ya existe")
    
    db.session.commit()

def create_sample_teams():
    """Crear equipos de ejemplo"""
    teams = [
        {
            'name': 'Frontend Development',
            'description': 'Equipo encargado del desarrollo de interfaces de usuario'
        },
        {
            'name': 'Backend Development', 
            'description': 'Desarrollo de APIs y servicios del servidor'
        },
        {
            'name': 'QA Testing',
            'description': 'Aseguramiento de calidad y testing'
        },
        {
            'name': 'UI/UX Design',
            'description': 'Diseño de interfaces y experiencia de usuario'
        },
        {
            'name': 'DevOps',
            'description': 'Infraestructura y operaciones'
        }
    ]
    
    for team_data in teams:
        team = Team.query.filter_by(name=team_data['name']).first()
        if not team:
            team = Team(
                name=team_data['name'],
                description=team_data['description']
            )
            db.session.add(team)
            print(f"✅ Equipo creado: {team_data['name']}")
        else:
            print(f"ℹ️  Equipo ya existe: {team_data['name']}")
    
    db.session.commit()

def sync_holidays():
    """Sincronizar festivos para España"""
    try:
        holiday_service = HolidayService()
        current_year = datetime.now().year
        
        # Sincronizar festivos para España
        holidays = holiday_service.sync_holidays_for_country('ES', current_year)
        print(f"✅ Sincronizados {len(holidays)} festivos para España {current_year}")
        
        # Sincronizar también para el próximo año
        next_year = current_year + 1
        holidays_next = holiday_service.sync_holidays_for_country('ES', next_year)
        print(f"✅ Sincronizados {len(holidays_next)} festivos para España {next_year}")
        
    except Exception as e:
        print(f"⚠️  Error sincronizando festivos: {e}")
        print("   Los festivos se pueden sincronizar más tarde desde la aplicación")

def main():
    """Función principal de inicialización"""
    print("🚀 Iniciando configuración de la base de datos...")
    
    # Obtener la aplicación Flask
    app = app_module.create_app()
    
    with app.app_context():
        try:
            # Crear todas las tablas
            print("📊 Creando tablas de la base de datos...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Crear roles
            print("\n👥 Configurando roles del sistema...")
            create_roles()
            
            # Crear usuario administrador
            print("\n🔐 Creando usuario administrador...")
            create_admin_user()
            
            # Crear equipos de ejemplo
            print("\n🏢 Creando equipos de ejemplo...")
            create_sample_teams()
            
            # Sincronizar festivos
            print("\n📅 Sincronizando festivos...")
            sync_holidays()
            
            print("\n🎉 ¡Inicialización completada exitosamente!")
            print("\n📋 Resumen:")
            print("   - Base de datos configurada")
            print("   - Roles del sistema creados")
            print("   - Usuario administrador: admin@teamtime.com / admin123")
            print("   - Equipos de ejemplo creados")
            print("   - Festivos sincronizados")
            print("\n🚀 La aplicación está lista para usar!")
            
        except Exception as e:
            print(f"❌ Error durante la inicialización: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    main()
