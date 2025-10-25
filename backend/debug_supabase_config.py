#!/usr/bin/env python3
"""
Script temporal para obtener la contraseña de Supabase
"""
import os
import sys
sys.path.append('/Users/thelittle/Team_time_management/Team_time_management/backend')

# Cargar variables de entorno explícitamente
from dotenv import load_dotenv
load_dotenv('.env.development')

from supabase_config import SupabaseConfig

def main():
    print("=== Configuración de Supabase ===")
    print(f"PROJECT_URL: {SupabaseConfig.PROJECT_URL}")
    print(f"SERVICE_KEY: {SupabaseConfig.SERVICE_KEY[:20]}..." if SupabaseConfig.SERVICE_KEY else "No configurado")
    print(f"DB_HOST: {SupabaseConfig.DB_HOST}")
    print(f"DB_PORT: {SupabaseConfig.DB_PORT}")
    print(f"DB_NAME: {SupabaseConfig.DB_NAME}")
    print(f"DB_USER: {SupabaseConfig.DB_USER}")
    print(f"DB_PASSWORD: {'***' if SupabaseConfig.DB_PASSWORD else 'No configurado'}")
    
    print("\n=== Variables de Entorno ===")
    print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL', 'No configurado')}")
    print(f"SUPABASE_KEY: {os.environ.get('SUPABASE_KEY', 'No configurado')[:20]}..." if os.environ.get('SUPABASE_KEY') else "No configurado")
    print(f"SUPABASE_HOST: {os.environ.get('SUPABASE_HOST', 'No configurado')}")
    print(f"SUPABASE_PORT: {os.environ.get('SUPABASE_PORT', 'No configurado')}")
    print(f"SUPABASE_DB: {os.environ.get('SUPABASE_DB', 'No configurado')}")
    print(f"SUPABASE_USER: {os.environ.get('SUPABASE_USER', 'No configurado')}")
    print(f"SUPABASE_DB_PASSWORD: {'***' if os.environ.get('SUPABASE_DB_PASSWORD') else 'No configurado'}")
    
    print("\n=== URL de Conexión ===")
    try:
        url = SupabaseConfig.get_database_url()
        print(f"URL: {url[:50]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()