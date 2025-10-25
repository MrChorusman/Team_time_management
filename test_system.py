#!/usr/bin/env python3
"""
Script simple para crear un usuario admin de prueba
"""

import os
import sys
import requests
import json
from datetime import datetime

# URL del backend
BACKEND_URL = "https://team-time-management.onrender.com"

def create_test_admin():
    """Crea un usuario admin de prueba usando el endpoint de registro"""
    
    print("🔧 Creando usuario admin de prueba...")
    
    # Datos del usuario admin
    admin_data = {
        "email": "admin@test.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "Test",
        "confirm_password": "admin123"
    }
    
    try:
        # Intentar registro
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Usuario admin creado exitosamente")
            return True
        else:
            print(f"❌ Error creando usuario: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_login():
    """Prueba el login con el usuario creado"""
    
    print("\n🔐 Probando login...")
    
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login exitoso")
                return data.get('access_token')
            else:
                print(f"❌ Error en login: {data.get('message')}")
                return None
        else:
            print(f"❌ Error HTTP: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_employee_creation(token):
    """Prueba crear un empleado"""
    
    print("\n👤 Probando creación de empleado...")
    
    employee_data = {
        "full_name": "Ana García Test",
        "team_id": 1,  # Asumimos que existe un equipo con ID 1
        "daily_hours": 8.0,
        "weekly_hours": 40.0,
        "vacation_days": 22,
        "country": "ES",
        "city": "Madrid"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/employees",
            json=employee_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Empleado creado exitosamente")
            return True
        else:
            print(f"❌ Error creando empleado: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del sistema Team Time Management")
    print("=" * 60)
    
    # Crear usuario admin
    if create_test_admin():
        # Probar login
        token = test_login()
        if token:
            # Probar creación de empleado
            test_employee_creation(token)
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    main()
