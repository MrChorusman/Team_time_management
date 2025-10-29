#!/usr/bin/env python
"""Script para diagnosticar la configuración"""
import os
import sys

print("=" * 70)
print("DIAGNÓSTICO DE CONFIGURACIÓN")
print("=" * 70)

# 1. Verificar FLASK_ENV
print(f"\n1. FLASK_ENV: {os.getenv('FLASK_ENV', 'NO CONFIGURADO')}")

# 2. Cargar .env files en el orden que lo hace config.py
from dotenv import load_dotenv

print("\n2. Cargando archivos .env en orden:")
print("   a) load_dotenv()")
load_dotenv()
print(f"      SUPABASE_HOST después: {os.getenv('SUPABASE_HOST', 'NO CONFIGURADO')}")

print("   b) load_dotenv('.env.local')")
load_dotenv('.env.local')
print(f"      SUPABASE_HOST después: {os.getenv('SUPABASE_HOST', 'NO CONFIGURADO')}")

print("   c) load_dotenv('.env.development')")
load_dotenv('.env.development')
print(f"      SUPABASE_HOST después: {os.getenv('SUPABASE_HOST', 'NO CONFIGURADO')}")
print(f"      SUPABASE_DEV_HOST después: {os.getenv('SUPABASE_DEV_HOST', 'NO CONFIGURADO')}")

# 3. Verificar SupabaseConfig
print("\n3. SupabaseConfig:")
from supabase_config import SupabaseConfig

print(f"   is_configured (PROD): {SupabaseConfig.is_configured()}")
print(f"   is_development_configured (DEV): {SupabaseConfig.is_development_configured()}")

if SupabaseConfig.is_configured():
    try:
        url = SupabaseConfig.get_database_url()
        print(f"   URL PROD: {url[:80]}...")
    except Exception as e:
        print(f"   ERROR getting PROD URL: {e}")

if SupabaseConfig.is_development_configured():
    try:
        url = SupabaseConfig.get_development_database_url()
        print(f"   URL DEV: {url[:80]}...")
    except Exception as e:
        print(f"   ERROR getting DEV URL: {e}")

# 4. Verificar config
print("\n4. Configuración de Flask:")
import config as config_module
config = config_module.config

dev_config = config['development']
print(f"   DevelopmentConfig.SQLALCHEMY_DATABASE_URI:")
if hasattr(dev_config, 'SQLALCHEMY_DATABASE_URI'):
    uri = dev_config.SQLALCHEMY_DATABASE_URI
    if uri:
        print(f"      {uri[:80]}...")
    else:
        print("      None")
else:
    print("      No configurado")

print("\n" + "=" * 70)

