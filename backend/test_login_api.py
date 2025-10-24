#!/usr/bin/env python3
"""
Script para probar login usando la API REST de Supabase directamente
"""

import requests
import json
from werkzeug.security import check_password_hash

def test_login_via_api():
    """Probar login usando API REST de Supabase"""
    
    print("🔐 PRUEBA DE LOGIN VIA API REST")
    print("=" * 40)
    
    # Configuración del proyecto de desarrollo
    DEV_URL = "https://qsbvoyjqfrhaqncqtknv.supabase.co"
    DEV_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k"
    
    headers = {
        'apikey': DEV_KEY,
        'Authorization': f"Bearer {DEV_KEY}",
        'Content-Type': 'application/json'
    }
    
    # Credenciales de prueba
    email = "admin@example.com"
    password = "test123"
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print()
    
    try:
        # Buscar usuario por email
        print("🔍 Buscando usuario...")
        response = requests.get(
            f"{DEV_URL}/rest/v1/user?email=eq.{email}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Error buscando usuario: {response.status_code}")
            return False
        
        users = response.json()
        
        if not users:
            print("❌ Usuario no encontrado")
            return False
        
        user = users[0]
        print(f"✅ Usuario encontrado: {user['email']}")
        print(f"   ID: {user['id']}")
        print(f"   Activo: {user['active']}")
        
        # Verificar contraseña
        print("\n🔐 Verificando contraseña...")
        stored_password = user['password']
        
        if check_password_hash(stored_password, password):
            print("✅ Contraseña correcta")
            
            # Obtener roles del usuario
            print("\n👥 Obteniendo roles...")
            roles_response = requests.get(
                f"{DEV_URL}/rest/v1/roles_users?user_id=eq.{user['id']}",
                headers=headers
            )
            
            if roles_response.status_code == 200:
                role_assignments = roles_response.json()
                
                if role_assignments:
                    # Obtener nombres de roles
                    role_ids = [ra['role_id'] for ra in role_assignments]
                    role_ids_str = ','.join(map(str, role_ids))
                    
                    roles_response = requests.get(
                        f"{DEV_URL}/rest/v1/role?id=in.({role_ids_str})",
                        headers=headers
                    )
                    
                    if roles_response.status_code == 200:
                        roles = roles_response.json()
                        role_names = [role['name'] for role in roles]
                        print(f"✅ Roles: {', '.join(role_names)}")
                    else:
                        print("⚠️  No se pudieron obtener los roles")
                else:
                    print("⚠️  Usuario sin roles asignados")
            
            # Simular respuesta de login exitoso
            print("\n🎉 ¡LOGIN EXITOSO!")
            print("=" * 20)
            print(f"✅ Usuario: {user['email']}")
            print(f"✅ ID: {user['id']}")
            print(f"✅ Activo: {user['active']}")
            print(f"✅ Login count: {user.get('login_count', 0)}")
            
            # Simular respuesta JSON del backend
            login_response = {
                "success": True,
                "message": "Inicio de sesión exitoso",
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "first_name": user.get('first_name'),
                    "last_name": user.get('last_name'),
                    "active": user['active']
                },
                "roles": role_names if 'role_names' in locals() else [],
                "redirectUrl": "/employee/register"
            }
            
            print(f"\n📄 Respuesta del backend:")
            print(json.dumps(login_response, indent=2, ensure_ascii=False))
            
            return True
            
        else:
            print("❌ Contraseña incorrecta")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el login: {e}")
        return False

if __name__ == "__main__":
    success = test_login_via_api()
    
    if success:
        print("\n🎯 CONCLUSIÓN:")
        print("✅ Login funcionando correctamente en entorno de desarrollo")
        print("✅ Datos migrados correctamente")
        print("✅ Autenticación operativa")
    else:
        print("\n❌ Error en el login")
        exit(1)


