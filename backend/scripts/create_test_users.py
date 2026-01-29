#!/usr/bin/env python3
"""
Script para crear usuarios de prueba (admin y empleado) en producción
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask_security.utils import hash_password
from models import db, User, Role
from models.employee import Employee
from models.team import Team
from main import create_app
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
load_dotenv('.env.production')

def create_test_users():
    """Crear usuarios de prueba: admin y empleado"""
    app = create_app('production')
    
    with app.app_context():
        print("🚀 Creando usuarios de prueba...")
        print("=" * 60)
        
        # Crear roles si no existen
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            print("✅ Rol 'admin' creado")
        else:
            print("ℹ️  Rol 'admin' ya existe")
        
        employee_role = Role.query.filter_by(name='employee').first()
        if not employee_role:
            employee_role = Role(name='employee', description='Empleado básico')
            db.session.add(employee_role)
            print("✅ Rol 'employee' creado")
        else:
            print("ℹ️  Rol 'employee' ya existe")
        
        db.session.commit()
        
        # Crear equipo de prueba si no existe
        test_team = Team.query.filter_by(name='Equipo de Prueba').first()
        if not test_team:
            test_team = Team(name='Equipo de Prueba', description='Equipo para pruebas de regresión')
            db.session.add(test_team)
            db.session.commit()
            print("✅ Equipo 'Equipo de Prueba' creado")
        else:
            print("ℹ️  Equipo 'Equipo de Prueba' ya existe")
        
        # ===== CREAR USUARIO ADMIN =====
        admin_email = 'admin.test@example.com'
        admin_password = 'AdminTest123!'
        
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                password=hash_password(admin_password),
                active=True,
                confirmed_at=datetime.utcnow()
            )
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print(f"\n✅ Usuario ADMIN creado:")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            
            # Crear perfil de empleado para el admin
            admin_employee = Employee.query.filter_by(user_id=admin_user.id).first()
            if not admin_employee:
                admin_employee = Employee(
                    user_id=admin_user.id,
                    full_name='Admin Test User',
                    team_id=test_team.id,
                    country='ES',
                    region='Madrid',
                    city='Madrid',
                    hours_monday_thursday=7.0,
                    hours_friday=6.0,
                    annual_vacation_days=22,
                    approved=True,
                    active=True
                )
                db.session.add(admin_employee)
                db.session.commit()
                print(f"   ✅ Perfil de empleado creado para admin")
        else:
            print(f"\nℹ️  Usuario ADMIN ya existe: {admin_email}")
            # Actualizar contraseña por si acaso
            admin_user.password = hash_password(admin_password)
            db.session.commit()
            print(f"   ✅ Contraseña actualizada")
        
        # ===== CREAR USUARIO EMPLEADO =====
        employee_email = 'employee.test@example.com'
        employee_password = 'EmployeeTest123!'
        
        employee_user = User.query.filter_by(email=employee_email).first()
        if not employee_user:
            employee_user = User(
                email=employee_email,
                password=hash_password(employee_password),
                active=True,
                confirmed_at=datetime.utcnow()
            )
            employee_user.roles.append(employee_role)
            db.session.add(employee_user)
            db.session.commit()
            print(f"\n✅ Usuario EMPLEADO creado:")
            print(f"   Email: {employee_email}")
            print(f"   Password: {employee_password}")
            
            # Crear perfil de empleado
            employee_employee = Employee.query.filter_by(user_id=employee_user.id).first()
            if not employee_employee:
                employee_employee = Employee(
                    user_id=employee_user.id,
                    full_name='Employee Test User',
                    team_id=test_team.id,
                    country='ES',
                    region='Barcelona',
                    city='Barcelona',
                    hours_monday_thursday=7.0,
                    hours_friday=6.0,
                    annual_vacation_days=22,
                    approved=True,
                    active=True
                )
                db.session.add(employee_employee)
                db.session.commit()
                print(f"   ✅ Perfil de empleado creado")
        else:
            print(f"\nℹ️  Usuario EMPLEADO ya existe: {employee_email}")
            # Actualizar contraseña por si acaso
            employee_user.password = hash_password(employee_password)
            db.session.commit()
            print(f"   ✅ Contraseña actualizada")
        
        print("\n" + "=" * 60)
        print("✅ Usuarios de prueba creados exitosamente")
        print("=" * 60)
        print("\n📋 CREDENCIALES:")
        print(f"\n👤 ADMIN:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"\n👤 EMPLEADO:")
        print(f"   Email: {employee_email}")
        print(f"   Password: {employee_password}")
        print("\n⚠️  IMPORTANTE: Guarda estas credenciales de forma segura")

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"\n❌ Error creando usuarios de prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
