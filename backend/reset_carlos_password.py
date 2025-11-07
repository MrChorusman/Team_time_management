#!/usr/bin/env python3
"""Script para resetear la contraseña de Carlos"""
from werkzeug.security import generate_password_hash

# Generar hash para password123
password = "password123"
password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

print(f"Password: {password}")
print(f"Hash: {password_hash}")
print()
print("SQL para actualizar en Supabase:")
print(f"UPDATE \"user\" SET password = '{password_hash}' WHERE email = 'carlos.empleado@example.com';")

