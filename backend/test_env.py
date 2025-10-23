#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("Verificando variables de entorno:")
print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
print(f"SUPABASE_KEY: {'***' if os.environ.get('SUPABASE_KEY') else 'NO CONFIGURADO'}")
print(f"SUPABASE_HOST: {os.environ.get('SUPABASE_HOST')}")
print(f"SUPABASE_PORT: {os.environ.get('SUPABASE_PORT')}")
print(f"SUPABASE_DB: {os.environ.get('SUPABASE_DB')}")
print(f"SUPABASE_USER: {os.environ.get('SUPABASE_USER')}")
print(f"SUPABASE_DB_PASSWORD: {'***' if os.environ.get('SUPABASE_DB_PASSWORD') else 'NO CONFIGURADO'}")

print("\nVerificando SupabaseConfig:")
from supabase_config import SupabaseConfig
print(f"is_configured(): {SupabaseConfig.is_configured()}")
if SupabaseConfig.is_configured():
    try:
        url = SupabaseConfig.get_database_url()
        print(f"Database URL: {url[:70]}...")
    except Exception as e:
        print(f"Error getting URL: {e}")
else:
    missing = SupabaseConfig.get_missing_vars()
    print(f"Missing vars: {missing}")

