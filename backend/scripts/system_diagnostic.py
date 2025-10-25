#!/usr/bin/env python3
"""
Diagnóstico completo del sistema Team Time Management
Verifica configuración, conexiones, dependencias y estado general
"""
import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import importlib.util

class SystemDiagnostic:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'dependencies': {},
            'configuration': {},
            'connections': {},
            'files': {},
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
    
    def check_system_info(self):
        """Verifica información del sistema"""
        print("🖥️  Verificando información del sistema...")
        
        try:
            self.results['system'] = {
                'platform': platform.platform(),
                'python_version': sys.version,
                'python_executable': sys.executable,
                'current_directory': str(Path.cwd()),
                'project_root': str(self.project_root),
                'backend_dir': str(self.backend_dir),
                'frontend_dir': str(self.frontend_dir)
            }
            
            print(f"   ✅ Plataforma: {platform.platform()}")
            print(f"   ✅ Python: {sys.version.split()[0]}")
            print(f"   ✅ Directorio actual: {Path.cwd()}")
            
        except Exception as e:
            self.results['errors'].append(f"Error verificando sistema: {e}")
            print(f"   ❌ Error: {e}")
    
    def check_dependencies(self):
        """Verifica dependencias de Python"""
        print("\n📦 Verificando dependencias de Python...")
        
        required_packages = [
            'flask', 'sqlalchemy', 'psycopg2', 'python-dotenv',
            'requests', 'werkzeug', 'flask-cors', 'flask-sqlalchemy'
        ]
        
        for package in required_packages:
            try:
                spec = importlib.util.find_spec(package)
                if spec is not None:
                    print(f"   ✅ {package}")
                    self.results['dependencies'][package] = 'installed'
                else:
                    print(f"   ❌ {package} - No instalado")
                    self.results['dependencies'][package] = 'missing'
                    self.results['errors'].append(f"Paquete faltante: {package}")
            except Exception as e:
                print(f"   ⚠️  {package} - Error verificando: {e}")
                self.results['dependencies'][package] = 'error'
                self.results['warnings'].append(f"Error verificando {package}: {e}")
    
    def check_node_dependencies(self):
        """Verifica dependencias de Node.js"""
        print("\n📦 Verificando dependencias de Node.js...")
        
        try:
            # Verificar si Node.js está instalado
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"   ✅ Node.js: {node_version}")
                self.results['dependencies']['node'] = node_version
            else:
                print(f"   ❌ Node.js no encontrado")
                self.results['dependencies']['node'] = 'missing'
                self.results['errors'].append("Node.js no encontrado")
                return
            
            # Verificar si npm está instalado
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"   ✅ npm: {npm_version}")
                self.results['dependencies']['npm'] = npm_version
            else:
                print(f"   ❌ npm no encontrado")
                self.results['dependencies']['npm'] = 'missing'
                self.results['errors'].append("npm no encontrado")
            
            # Verificar package.json del frontend
            package_json = self.frontend_dir / 'package.json'
            if package_json.exists():
                print(f"   ✅ package.json encontrado")
                self.results['dependencies']['package_json'] = 'found'
            else:
                print(f"   ❌ package.json no encontrado")
                self.results['dependencies']['package_json'] = 'missing'
                self.results['errors'].append("package.json no encontrado")
            
        except Exception as e:
            self.results['errors'].append(f"Error verificando Node.js: {e}")
            print(f"   ❌ Error: {e}")
    
    def check_configuration_files(self):
        """Verifica archivos de configuración"""
        print("\n🔧 Verificando archivos de configuración...")
        
        # Archivos de configuración del backend
        backend_config_files = [
            'config.py',
            'config/app_config.py',
            'config/database_manager.py',
            'config/validators/supabase_validator.py',
            'config/environments/base.json',
            'config/environments/development.json',
            'config/environments/production.json',
            'config/environments/.env.development',
            'config/environments/.env.production'
        ]
        
        for config_file in backend_config_files:
            file_path = self.backend_dir / config_file
            if file_path.exists():
                print(f"   ✅ {config_file}")
                self.results['configuration'][config_file] = 'found'
            else:
                print(f"   ❌ {config_file} - No encontrado")
                self.results['configuration'][config_file] = 'missing'
                self.results['errors'].append(f"Archivo de configuración faltante: {config_file}")
        
        # Archivos de configuración del frontend
        frontend_config_files = [
            'src/config/environment.js',
            'src/config/api.config.js',
            'vite.config.js',
            'package.json'
        ]
        
        for config_file in frontend_config_files:
            file_path = self.frontend_dir / config_file
            if file_path.exists():
                print(f"   ✅ {config_file}")
                self.results['configuration'][config_file] = 'found'
            else:
                print(f"   ❌ {config_file} - No encontrado")
                self.results['configuration'][config_file] = 'missing'
                self.results['errors'].append(f"Archivo de configuración faltante: {config_file}")
    
    def check_database_connections(self):
        """Verifica conexiones a la base de datos"""
        print("\n🗄️  Verificando conexiones a la base de datos...")
        
        try:
            # Ejecutar script de prueba de conexiones
            test_script = self.backend_dir / 'scripts' / 'test_new_config.py'
            if test_script.exists():
                result = subprocess.run([sys.executable, str(test_script)], 
                                      capture_output=True, text=True, cwd=self.backend_dir)
                
                if result.returncode == 0:
                    print("   ✅ Conexiones de base de datos exitosas")
                    self.results['connections']['database'] = 'success'
                else:
                    print("   ❌ Error en conexiones de base de datos")
                    print(f"      {result.stderr}")
                    self.results['connections']['database'] = 'failed'
                    self.results['errors'].append("Error en conexiones de base de datos")
            else:
                print("   ⚠️  Script de prueba de conexiones no encontrado")
                self.results['connections']['database'] = 'script_missing'
                self.results['warnings'].append("Script de prueba de conexiones no encontrado")
        
        except Exception as e:
            self.results['errors'].append(f"Error verificando conexiones: {e}")
            print(f"   ❌ Error: {e}")
    
    def check_file_structure(self):
        """Verifica estructura de archivos del proyecto"""
        print("\n📁 Verificando estructura de archivos...")
        
        required_dirs = [
            'backend',
            'backend/config',
            'backend/config/environments',
            'backend/config/validators',
            'backend/scripts',
            'backend/models',
            'backend/services',
            'frontend',
            'frontend/src',
            'frontend/src/config',
            'frontend/src/components',
            'frontend/src/pages'
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                print(f"   ✅ {dir_path}/")
                self.results['files'][dir_path] = 'exists'
            else:
                print(f"   ❌ {dir_path}/ - No encontrado")
                self.results['files'][dir_path] = 'missing'
                self.results['errors'].append(f"Directorio faltante: {dir_path}")
    
    def check_environment_switching(self):
        """Verifica el cambio de entornos"""
        print("\n🔄 Verificando cambio de entornos...")
        
        try:
            # Ejecutar script de gestión de entornos
            env_manager = self.backend_dir / 'scripts' / 'env_manager.py'
            if env_manager.exists():
                result = subprocess.run([sys.executable, str(env_manager), 'list'], 
                                      capture_output=True, text=True, cwd=self.backend_dir)
                
                if result.returncode == 0:
                    print("   ✅ Gestor de entornos funcionando")
                    self.results['configuration']['env_manager'] = 'working'
                else:
                    print("   ❌ Error en gestor de entornos")
                    self.results['configuration']['env_manager'] = 'failed'
                    self.results['errors'].append("Error en gestor de entornos")
            else:
                print("   ❌ Gestor de entornos no encontrado")
                self.results['configuration']['env_manager'] = 'missing'
                self.results['errors'].append("Gestor de entornos no encontrado")
        
        except Exception as e:
            self.results['errors'].append(f"Error verificando cambio de entornos: {e}")
            print(f"   ❌ Error: {e}")
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en los resultados"""
        print("\n💡 Generando recomendaciones...")
        
        # Recomendaciones basadas en errores
        if any('missing' in str(value) for value in self.results['dependencies'].values()):
            self.results['recommendations'].append(
                "Instalar dependencias faltantes: pip install -r requirements.txt"
            )
        
        if any('missing' in str(value) for value in self.results['configuration'].values()):
            self.results['recommendations'].append(
                "Ejecutar migración de configuración: python scripts/migrate_env_config.py"
            )
        
        if self.results['connections'].get('database') == 'failed':
            self.results['recommendations'].append(
                "Verificar configuración de Supabase y credenciales"
            )
        
        if any('missing' in str(value) for value in self.results['files'].values()):
            self.results['recommendations'].append(
                "Verificar estructura del proyecto y archivos faltantes"
            )
        
        # Recomendaciones generales
        self.results['recommendations'].extend([
            "Ejecutar tests completos: python scripts/test_new_config.py",
            "Validar entornos: python scripts/env_manager.py validate development",
            "Probar cambio de entornos: python scripts/env_manager.py switch production"
        ])
        
        for recommendation in self.results['recommendations']:
            print(f"   💡 {recommendation}")
    
    def generate_report(self):
        """Genera reporte completo del diagnóstico"""
        print("\n" + "="*60)
        print("📊 REPORTE DE DIAGNÓSTICO DEL SISTEMA")
        print("="*60)
        
        # Resumen general
        total_checks = len(self.results['system']) + len(self.results['dependencies']) + \
                      len(self.results['configuration']) + len(self.results['connections']) + \
                      len(self.results['files'])
        
        errors_count = len(self.results['errors'])
        warnings_count = len(self.results['warnings'])
        
        print(f"\n📈 Resumen:")
        print(f"   • Total de verificaciones: {total_checks}")
        print(f"   • Errores encontrados: {errors_count}")
        print(f"   • Advertencias: {warnings_count}")
        print(f"   • Recomendaciones: {len(self.results['recommendations'])}")
        
        # Estado del sistema
        if errors_count == 0:
            print(f"\n✅ Estado del sistema: SALUDABLE")
        elif errors_count <= 3:
            print(f"\n⚠️  Estado del sistema: ADVERTENCIAS MENORES")
        else:
            print(f"\n❌ Estado del sistema: REQUIERE ATENCIÓN")
        
        # Mostrar errores
        if self.results['errors']:
            print(f"\n❌ Errores encontrados:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        # Mostrar advertencias
        if self.results['warnings']:
            print(f"\n⚠️  Advertencias:")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        # Mostrar recomendaciones
        if self.results['recommendations']:
            print(f"\n💡 Recomendaciones:")
            for recommendation in self.results['recommendations']:
                print(f"   • {recommendation}")
        
        # Guardar reporte
        reports_dir = self.backend_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f'system_diagnostic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        print("="*60)
        
        return errors_count == 0
    
    def run(self):
        """Ejecuta diagnóstico completo"""
        print("🚀 Iniciando diagnóstico completo del sistema...")
        print("="*60)
        
        self.check_system_info()
        self.check_dependencies()
        self.check_node_dependencies()
        self.check_configuration_files()
        self.check_database_connections()
        self.check_file_structure()
        self.check_environment_switching()
        self.generate_recommendations()
        
        success = self.generate_report()
        
        if success:
            print("\n✅ Sistema en buen estado")
        else:
            print("\n❌ Sistema requiere atención. Revisar errores y recomendaciones.")
        
        return success

def main():
    diagnostic = SystemDiagnostic()
    success = diagnostic.run()
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
