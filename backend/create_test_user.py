#!/usr/bin/env python3
"""Script para crear usuario de prueba"""
from flask_security.utils import hash_password
from models import db, User, Role
from models.employee import Employee
from models.team import Team
from main import create_app
from datetime import datetime

def create_test_user():
    """Crear usuario de prueba"""
    app = create_app()
    
    with app.app_context():
        # Crear roles si no existen
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
        
        manager_role = Role.query.filter_by(name='manager').first()
        if not manager_role:
            manager_role = Role(name='manager', description='Gestor de equipos')
            db.session.add(manager_role)
        
        employee_role = Role.query.filter_by(name='employee').first()
        if not employee_role:
            employee_role = Role(name='employee', description='Empleado básico')
            db.session.add(employee_role)
        
        db.session.commit()
        
        # Crear equipo si no existe
        team = Team.query.filter_by(name='Frontend').first()
        if not team:
            team = Team(name='Frontend', description='Equipo de desarrollo frontend')
            db.session.add(team)
            db.session.commit()
        
        # Crear usuario admin si no existe
        admin_user = User.query.filter_by(email='admin@test.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@test.com',
                password=hash_password('admin123'),
                active=True,
                confirmed_at=datetime.utcnow()
            )
            admin_user.roles.append(admin_role)
            admin_user.roles.append(manager_role)
            db.session.add(admin_user)
            db.session.commit()
            
            # Crear empleado para el admin
            employee = Employee(
                user_id=admin_user.id,
                full_name='Admin Test',
                team_id=team.id,
                country='ES',
                region='Madrid',
                approved=True,
                active=True
            )
            db.session.add(employee)
            db.session.commit()
            
            print(f"✅ Usuario admin creado: admin@test.com / admin123")
        else:
            print(f"ℹ️  Usuario admin ya existe: admin@test.com")
        
        print(f"\n✅ Setup completado!")
        print(f"   - Roles creados: admin, manager, employee")
        print(f"   - Equipo: Frontend")
        print(f"   - Usuario: admin@test.com / admin123")

if __name__ == '__main__':
    create_test_user()
