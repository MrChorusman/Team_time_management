#!/usr/bin/env python3
"""
Script para crear el usuario administrador inicial de producción.
Este usuario será entregado al cliente para la primera configuración del sistema.
"""
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

# Generar credenciales para el admin inicial
email = "admin@teamtime.com"
password = "Admin2025!"  # El cliente DEBE cambiar esta contraseña en el primer login
fs_uniquifier = uuid.uuid4().hex

# Generar hash de contraseña
password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

print("=" * 80)
print("USUARIO ADMINISTRADOR INICIAL PARA ENTREGA AL CLIENTE")
print("=" * 80)
print()
print("📧 Email:", email)
print("🔐 Contraseña temporal:", password)
print("⚠️  IMPORTANTE: El cliente DEBE cambiar esta contraseña en el primer acceso")
print()
print("=" * 80)
print("SQL PARA INSERTAR EN SUPABASE:")
print("=" * 80)
print()

# SQL para insertar el usuario
print(f"""
-- Paso 1: Crear usuario administrador inicial
INSERT INTO "user" (
  email, 
  password, 
  username, 
  active, 
  confirmed_at, 
  fs_uniquifier,
  first_name,
  last_name,
  created_at,
  updated_at
) VALUES (
  '{email}',
  '{password_hash}',
  'admin',
  true,
  NOW(),
  '{fs_uniquifier}',
  'Administrador',
  'Sistema',
  NOW(),
  NOW()
);
""")

print("""
-- Paso 2: Asignar rol de admin al usuario
-- Nota: Primero obtener el ID del usuario recién creado
INSERT INTO roles_users (user_id, role_id)
VALUES (
  (SELECT id FROM "user" WHERE email = 'admin@teamtime.com'),
  (SELECT id FROM role WHERE name = 'admin')
);
""")

print("=" * 80)
print("CREDENCIALES PARA ENTREGAR AL CLIENTE")
print("=" * 80)
print()
print(f"URL: https://team-time-management.vercel.app")
print(f"Email: {email}")
print(f"Contraseña: {password}")
print()
print("⚠️  INSTRUCCIONES PARA EL CLIENTE:")
print("1. Acceder con estas credenciales")
print("2. Ir a 'Mi Perfil' y cambiar la contraseña INMEDIATAMENTE")
print("3. Crear equipos de la organización")
print("4. Aprobar/rechazar nuevos registros de empleados")
print("5. Gestionar permisos y configuración del sistema")
print()
print("=" * 80)

