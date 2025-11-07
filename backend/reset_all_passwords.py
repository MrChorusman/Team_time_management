#!/usr/bin/env python3
"""Script para resetear contraseñas de todos los usuarios a password123"""
from werkzeug.security import generate_password_hash

# Generar hash para password123 con pbkdf2 (el método estándar de Flask)
password = "password123"
password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

print(f"Password para todos: {password}")
print(f"Hash: {password_hash}")
print()
print("=" * 80)
print("SQL para actualizar TODOS los usuarios en Supabase:")
print("=" * 80)

usuarios = [
    ("employee.test@example.com", "Fernando Garamendia - NO aprobado"),
    ("maria.manager@example.com", "María García - Manager"),
    ("carlos.empleado@example.com", "Carlos López - Empleado"),
    ("admin@test.com", "Admin Test"),
    ("admin@example.com", "Admin sin employee"),
    ("miguelchis@gmail.com", "Miguel (tu cuenta)")
]

for email, descripcion in usuarios:
    print(f"\n-- {descripcion}")
    print(f"UPDATE \"user\" SET password = '{password_hash}' WHERE email = '{email}';")

print("\n" + "=" * 80)
print("Después de ejecutar estos comandos, TODOS los usuarios tendrán:")
print(f"Contraseña: {password}")
print("=" * 80)

