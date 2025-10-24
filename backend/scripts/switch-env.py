#!/usr/bin/env python3
"""
Script para cambiar entre entornos de desarrollo
Uso: python switch-env.py <entorno>
Entornos disponibles: local, dev-prod, production
"""

import os
import shutil
import sys

def switch_environment(env_name):
    """Cambia el entorno activo"""
    env_files = {
        'local': '.env.development',
        'dev-prod': '.env.development-production-like', 
        'production': '.env.production'
    }
    
    if env_name not in env_files:
        print(f"❌ Entorno '{env_name}' no válido")
        print(f"Entornos disponibles: {list(env_files.keys())}")
        return False
    
    source_file = env_files[env_name]
    if not os.path.exists(source_file):
        print(f"❌ Archivo {source_file} no encontrado")
        return False
    
    # Crear backup del .env actual si existe
    if os.path.exists('.env'):
        shutil.copy('.env', '.env.backup')
        print(f"📦 Backup creado: .env.backup")
    
    # Copiar archivo de configuración
    shutil.copy(source_file, '.env')
    print(f"✅ Cambiado a entorno: {env_name}")
    print(f"📁 Archivo activo: .env (desde {source_file})")
    
    # Mostrar información del entorno
    show_environment_info(env_name)
    return True

def show_environment_info(env_name):
    """Muestra información del entorno activo"""
    print(f"\n🔍 INFORMACIÓN DEL ENTORNO: {env_name.upper()}")
    print("=" * 50)
    
    if env_name == 'local':
        print("📍 Tipo: Desarrollo local")
        print("🗄️  Base de datos: PostgreSQL local")
        print("🔧 Debug: Habilitado")
        print("⚠️  Nota: Requiere PostgreSQL local instalado")
        
    elif env_name == 'dev-prod':
        print("📍 Tipo: Desarrollo que simula producción")
        print("🗄️  Base de datos: Supabase desarrollo")
        print("🔧 Debug: Habilitado")
        print("🌐 Conexión: Transaction Pooler (puerto 6543)")
        
    elif env_name == 'production':
        print("📍 Tipo: Producción")
        print("🗄️  Base de datos: Supabase producción")
        print("🔧 Debug: Deshabilitado")
        print("⚠️  ADVERTENCIA: Entorno de producción")
        print("🚫 NO usar para desarrollo local")

def main():
    if len(sys.argv) != 2:
        print("🔧 GESTOR DE ENTORNOS - Team Time Management")
        print("=" * 50)
        print("Uso: python switch-env.py <entorno>")
        print("\nEntornos disponibles:")
        print("  local      - Desarrollo con PostgreSQL local")
        print("  dev-prod   - Desarrollo con Supabase (simula producción)")
        print("  production - Producción (SOLO para despliegues)")
        print("\nEjemplos:")
        print("  python switch-env.py local")
        print("  python switch-env.py dev-prod")
        return
    
    env_name = sys.argv[1]
    success = switch_environment(env_name)
    
    if success:
        print(f"\n🎯 PRÓXIMOS PASOS:")
        if env_name == 'local':
            print("  1. Asegúrate de que PostgreSQL esté ejecutándose")
            print("  2. Crea la base de datos: createdb team_time_management_dev")
            print("  3. Ejecuta: python main.py")
        elif env_name == 'dev-prod':
            print("  1. Configura las variables SUPABASE_DEV_* en .env")
            print("  2. Ejecuta: python main.py")
        elif env_name == 'production':
            print("  1. ⚠️  SOLO usar para despliegues en Render")
            print("  2. NO usar para desarrollo local")

if __name__ == "__main__":
    main()
