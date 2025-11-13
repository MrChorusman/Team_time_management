#!/usr/bin/env python3
"""
Script de diagnóstico para el problema de login del admin
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("DIAGNÓSTICO DE LOGIN ADMIN")
print("=" * 80)
print()

# 1. Verificar variables de entorno
print("1. Verificando configuración...")
from dotenv import load_dotenv
load_dotenv('.env.development')

supabase_url = os.getenv('SUPABASE_URL', 'NOT SET')
print(f"   SUPABASE_URL: {supabase_url[:50]}..." if supabase_url != 'NOT SET' else f"   SUPABASE_URL: {supabase_url}")

# 2. Verificar conexión a la base de datos
print("\n2. Verificando conexión a la base de datos...")
try:
    from main import create_app
    from models.user import User, Role, db
    
    app = create_app()
    
    with app.app_context():
        # Intentar conectar
        try:
            db.session.execute(db.text('SELECT 1'))
            print("   ✅ Conexión a la base de datos: OK")
        except Exception as e:
            print(f"   ❌ Error de conexión a la base de datos: {e}")
            sys.exit(1)
        
        # 3. Verificar usuario admin
        print("\n3. Verificando usuario admin...")
        admin_email = 'admin@teamtime.com'
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if admin_user:
            print(f"   ✅ Usuario encontrado: {admin_email}")
            print(f"      - ID: {admin_user.id}")
            print(f"      - Activo: {admin_user.active}")
            print(f"      - Confirmado: {admin_user.confirmed_at is not None}")
            print(f"      - Password: {'✅ Configurado' if admin_user.password else '❌ No configurado'}")
            
            # Verificar roles
            roles = [role.name for role in admin_user.roles]
            print(f"      - Roles: {roles}")
            
            # Verificar problemas
            issues = []
            if 'admin' not in roles:
                issues.append("❌ No tiene rol de admin")
            if not admin_user.active:
                issues.append("❌ Usuario inactivo")
            if not admin_user.confirmed_at:
                issues.append("❌ Email no confirmado")
            if not admin_user.password:
                issues.append("❌ No tiene contraseña")
            
            if issues:
                print("\n   ⚠️  PROBLEMAS ENCONTRADOS:")
                for issue in issues:
                    print(f"      {issue}")
            else:
                print("\n   ✅ Usuario admin está correctamente configurado")
        else:
            print(f"   ❌ Usuario admin NO encontrado: {admin_email}")
            print("   Necesitas crear el usuario admin primero")
            
            # Verificar si existe el rol admin
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                print(f"   ✅ Rol 'admin' existe (ID: {admin_role.id})")
            else:
                print("   ❌ Rol 'admin' NO existe")
        
        # 4. Verificar otros usuarios admin posibles
        print("\n4. Buscando otros usuarios admin...")
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_users = User.query.join(User.roles).filter(Role.id == admin_role.id).all()
            print(f"   Encontrados {len(admin_users)} usuario(s) con rol admin:")
            for user in admin_users:
                print(f"      - {user.email} (ID: {user.id}, Activo: {user.active}, Confirmado: {user.confirmed_at is not None})")

except Exception as e:
    print(f"\n❌ Error durante el diagnóstico: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 80)
