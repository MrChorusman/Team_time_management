#!/usr/bin/env python3
"""
Gestor de entornos para Team Time Management
Permite cambiar fácilmente entre entornos de desarrollo y producción
"""
import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import subprocess

class EnvironmentManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_dir = self.project_root / 'backend'
        self.config_dir = self.backend_dir / 'config'
        self.environments_dir = self.config_dir / 'environments'
        
        # Archivos de configuración
        self.env_files = {
            'development': self.environments_dir / '.env.development',
            'production': self.environments_dir / '.env.production'
        }
        
        # Archivos JSON de configuración
        self.json_files = {
            'base': self.environments_dir / 'base.json',
            'development': self.environments_dir / 'development.json',
            'production': self.environments_dir / 'production.json'
        }
    
    def get_current_environment(self):
        """Obtiene el entorno actual"""
        try:
            # Intentar leer desde el archivo .env actual
            env_file = self.backend_dir / '.env'
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                    if 'FLASK_ENV=development' in content:
                        return 'development'
                    elif 'FLASK_ENV=production' in content:
                        return 'production'
            
            # Fallback: verificar variable de entorno
            return os.getenv('FLASK_ENV', 'development')
        except Exception as e:
            print(f"⚠️  Error detectando entorno actual: {e}")
            return 'development'
    
    def list_environments(self):
        """Lista todos los entornos disponibles"""
        print("📋 Entornos disponibles:")
        print("=" * 40)
        
        for env_name, env_file in self.env_files.items():
            status = "✅" if env_file.exists() else "❌"
            current = " (ACTUAL)" if env_name == self.get_current_environment() else ""
            print(f"   {status} {env_name}{current}")
        
        print("=" * 40)
    
    def switch_environment(self, target_env):
        """Cambia al entorno especificado"""
        if target_env not in self.env_files:
            print(f"❌ Entorno '{target_env}' no válido")
            print("Entornos disponibles: development, production")
            return False
        
        if not self.env_files[target_env].exists():
            print(f"❌ Archivo de entorno '{target_env}' no encontrado")
            print(f"Ruta esperada: {self.env_files[target_env]}")
            return False
        
        try:
            # Crear backup del .env actual
            current_env_file = self.backend_dir / '.env'
            if current_env_file.exists():
                backup_name = f".env.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(current_env_file, self.backend_dir / backup_name)
                print(f"📦 Backup creado: {backup_name}")
            
            # Copiar el nuevo archivo de entorno
            shutil.copy2(self.env_files[target_env], current_env_file)
            
            # Establecer variable de entorno
            os.environ['FLASK_ENV'] = target_env
            
            print(f"✅ Cambiado a entorno: {target_env}")
            print(f"📁 Archivo activo: {current_env_file}")
            
            # Mostrar configuración actual
            self.show_current_config(target_env)
            
            return True
            
        except Exception as e:
            print(f"❌ Error cambiando entorno: {e}")
            return False
    
    def show_current_config(self, env_name=None):
        """Muestra la configuración actual"""
        if env_name is None:
            env_name = self.get_current_environment()
        
        print(f"\n🔧 Configuración actual ({env_name}):")
        print("=" * 50)
        
        try:
            # Mostrar configuración JSON
            json_file = self.json_files[env_name]
            if json_file.exists():
                with open(json_file, 'r') as f:
                    config = json.load(f)
                
                print(f"📊 Puerto: {config.get('port', 'N/A')}")
                print(f"🐛 Debug: {config.get('debug', 'N/A')}")
                print(f"🗄️  Base de datos: {config.get('database', {}).get('provider', 'N/A')}")
                print(f"🔗 Conexión: {config.get('database', {}).get('connection_type', 'N/A')}")
                print(f"🌐 Frontend: {config.get('frontend', {}).get('url', 'N/A')}")
                print(f"📧 Email mock: {config.get('email', {}).get('mock_mode', 'N/A')}")
                print(f"🔐 Google OAuth mock: {config.get('google_oauth', {}).get('mock_mode', 'N/A')}")
            
            # Mostrar variables de entorno sensibles (sin mostrar valores)
            env_file = self.env_files[env_name]
            if env_file.exists():
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                print(f"\n🔑 Variables de entorno:")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key = line.split('=')[0]
                        print(f"   • {key}")
            
        except Exception as e:
            print(f"⚠️  Error mostrando configuración: {e}")
        
        print("=" * 50)
    
    def validate_environment(self, env_name):
        """Valida la configuración de un entorno"""
        print(f"🔍 Validando entorno: {env_name}")
        print("=" * 40)
        
        if env_name not in self.env_files:
            print(f"❌ Entorno '{env_name}' no válido")
            return False
        
        # Verificar archivos necesarios
        env_file = self.env_files[env_name]
        json_file = self.json_files[env_name]
        
        if not env_file.exists():
            print(f"❌ Archivo .env faltante: {env_file}")
            return False
        
        if not json_file.exists():
            print(f"❌ Archivo JSON faltante: {json_file}")
            return False
        
        # Validar configuración JSON
        try:
            with open(json_file, 'r') as f:
                config = json.load(f)
            
            required_fields = ['environment', 'debug', 'port']
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                print(f"❌ Campos faltantes en JSON: {missing_fields}")
                return False
            
            print(f"✅ Configuración JSON válida")
            
        except Exception as e:
            print(f"❌ Error validando JSON: {e}")
            return False
        
        # Validar variables de entorno
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            required_vars = ['SECRET_KEY', 'FLASK_ENV', 'SUPABASE_URL', 'SUPABASE_KEY']
            missing_vars = []
            
            for var in required_vars:
                if f"{var}=" not in content:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"❌ Variables faltantes: {missing_vars}")
                return False
            
            print(f"✅ Variables de entorno válidas")
            
        except Exception as e:
            print(f"❌ Error validando variables: {e}")
            return False
        
        print(f"✅ Entorno '{env_name}' válido")
        return True
    
    def test_connection(self, env_name):
        """Prueba la conexión de un entorno"""
        print(f"🔗 Probando conexión para: {env_name}")
        print("=" * 40)
        
        try:
            # Cambiar temporalmente al entorno
            original_env = self.get_current_environment()
            self.switch_environment(env_name)
            
            # Ejecutar script de prueba de conexión
            test_script = self.backend_dir / 'scripts' / 'test_new_config.py'
            if test_script.exists():
                result = subprocess.run([sys.executable, str(test_script)], 
                                      capture_output=True, text=True, cwd=self.backend_dir)
                
                if result.returncode == 0:
                    print("✅ Conexión exitosa")
                else:
                    print("❌ Error en conexión")
                    print(result.stderr)
            else:
                print("⚠️  Script de prueba no encontrado")
            
            # Restaurar entorno original
            self.switch_environment(original_env)
            
        except Exception as e:
            print(f"❌ Error probando conexión: {e}")
    
    def create_environment(self, env_name, template_env='development'):
        """Crea un nuevo entorno basado en una plantilla"""
        if env_name in self.env_files:
            print(f"❌ Entorno '{env_name}' ya existe")
            return False
        
        if template_env not in self.env_files:
            print(f"❌ Plantilla '{template_env}' no válida")
            return False
        
        try:
            # Crear archivo .env
            template_file = self.env_files[template_env]
            new_env_file = self.environments_dir / f'.env.{env_name}'
            
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Reemplazar FLASK_ENV
            content = content.replace(f'FLASK_ENV={template_env}', f'FLASK_ENV={env_name}')
            
            with open(new_env_file, 'w') as f:
                f.write(content)
            
            # Crear archivo JSON
            template_json = self.json_files[template_env]
            new_json_file = self.environments_dir / f'{env_name}.json'
            
            with open(template_json, 'r') as f:
                config = json.load(f)
            
            config['environment'] = env_name
            
            with open(new_json_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Entorno '{env_name}' creado basado en '{template_env}'")
            print(f"📁 Archivos creados:")
            print(f"   • {new_env_file}")
            print(f"   • {new_json_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando entorno: {e}")
            return False
    
    def show_help(self):
        """Muestra la ayuda del comando"""
        print("""
🔧 Gestor de Entornos - Team Time Management
============================================

Comandos disponibles:
  list                    Lista entornos disponibles
  switch <env>            Cambia al entorno especificado
  show [env]              Muestra configuración actual o del entorno especificado
  validate <env>          Valida la configuración de un entorno
  test <env>              Prueba la conexión de un entorno
  create <env> [template] Crea un nuevo entorno basado en una plantilla
  help                    Muestra esta ayuda

Ejemplos:
  python env_manager.py list
  python env_manager.py switch development
  python env_manager.py show production
  python env_manager.py validate development
  python env_manager.py test production
  python env_manager.py create staging development

Entornos disponibles:
  • development  - Entorno de desarrollo local
  • production   - Entorno de producción
        """)

def main():
    manager = EnvironmentManager()
    
    if len(sys.argv) < 2:
        manager.show_help()
        return 1
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        manager.list_environments()
    
    elif command == 'switch':
        if len(sys.argv) < 3:
            print("❌ Especifica el entorno a cambiar")
            print("Uso: python env_manager.py switch <env>")
            return 1
        
        target_env = sys.argv[2]
        success = manager.switch_environment(target_env)
        return 0 if success else 1
    
    elif command == 'show':
        env_name = sys.argv[2] if len(sys.argv) > 2 else None
        manager.show_current_config(env_name)
    
    elif command == 'validate':
        if len(sys.argv) < 3:
            print("❌ Especifica el entorno a validar")
            print("Uso: python env_manager.py validate <env>")
            return 1
        
        env_name = sys.argv[2]
        success = manager.validate_environment(env_name)
        return 0 if success else 1
    
    elif command == 'test':
        if len(sys.argv) < 3:
            print("❌ Especifica el entorno a probar")
            print("Uso: python env_manager.py test <env>")
            return 1
        
        env_name = sys.argv[2]
        manager.test_connection(env_name)
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Especifica el nombre del nuevo entorno")
            print("Uso: python env_manager.py create <env> [template]")
            return 1
        
        env_name = sys.argv[2]
        template_env = sys.argv[3] if len(sys.argv) > 3 else 'development'
        success = manager.create_environment(env_name, template_env)
        return 0 if success else 1
    
    elif command == 'help':
        manager.show_help()
    
    else:
        print(f"❌ Comando desconocido: {command}")
        manager.show_help()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
