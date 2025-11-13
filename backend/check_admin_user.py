#!/usr/bin/env python3
"""
Script para verificar el estado del usuario admin
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv('.env.development')

from main import create_app
from models.user import User, Role, db

app = create_app()

with app.app_context():
    # Buscar usuario admin
    admin_email = 'admin@teamtime.com'
    admin_user = User.query.filter_by(email=admin_email).first()
    
    if admin_user:
        print(f"✅ Usuario admin encontrado: {admin_email}")
        print(f"   - ID: {admin_user.id}")
        print(f"   - Email: {admin_user.email}")
        print(f"   - Activo: {admin_user.active}")
        print(f"   - Confirmado: {admin_user.confirmed_at is not None}")
        print(f"   - Password hash: {'✅ Configurado' if admin_user.password else '❌ No configurado'}")
        
        # Verificar roles
        roles = [role.name for role in admin_user.roles]
        print(f"   - Roles: {roles}")
        
        if 'admin' not in roles:
            print("   ⚠️  ADVERTENCIA: El usuario no tiene rol de admin")
        
        if not admin_user.active:
            print("   ⚠️  ADVERTENCIA: El usuario está inactivo")
        
        if not admin_user.confirmed_at:
            print("   ⚠️  ADVERTENCIA: El email no está confirmado")
        
        if not admin_user.password:
            print("   ⚠️  ADVERTENCIA: El usuario no tiene contraseña configurada")
    else:
        print(f"❌ Usuario admin NO encontrado: {admin_email}")
        print("   Necesitas crear el usuario admin primero")
