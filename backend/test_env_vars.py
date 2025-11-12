#!/usr/bin/env python3
"""Script temporal para verificar variables de entorno SMTP"""
import os

print("=== VERIFICACIÓN DE VARIABLES SMTP ===")
print(f"MOCK_EMAIL_MODE: {os.environ.get('MOCK_EMAIL_MODE', 'NOT SET')}")
print(f"MAIL_SERVER: {os.environ.get('MAIL_SERVER', 'NOT SET')}")
print(f"MAIL_PORT: {os.environ.get('MAIL_PORT', 'NOT SET')}")
print(f"MAIL_USE_TLS: {os.environ.get('MAIL_USE_TLS', 'NOT SET')}")
print(f"MAIL_USERNAME: {'SET' if os.environ.get('MAIL_USERNAME') else 'NOT SET'}")
print(f"MAIL_PASSWORD: {'SET (hidden)' if os.environ.get('MAIL_PASSWORD') else 'NOT SET'}")
print(f"MAIL_DEFAULT_SENDER: {os.environ.get('MAIL_DEFAULT_SENDER', 'NOT SET')}")
print("=====================================")

# Simular la lógica de app_config
MOCK_EMAIL_MODE = os.environ.get('MOCK_EMAIL_MODE', 'false').lower() in ['true', 'on', '1']
email_configured = all([
    os.environ.get('MAIL_USERNAME'),
    os.environ.get('MAIL_PASSWORD')
])
should_use_mock = MOCK_EMAIL_MODE or not email_configured

print(f"\nMOCK_EMAIL_MODE evaluado: {MOCK_EMAIL_MODE}")
print(f"email_configured: {email_configured}")
print(f"should_use_mock_email: {should_use_mock}")
print(f"\n{'🟢 Email real habilitado' if not should_use_mock else '🔴 Modo MOCK activo'}")

