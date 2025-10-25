#!/usr/bin/env python3
"""
Script para probar la nueva arquitectura de configuración
"""
import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Añadir el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.app_config import AppConfig, get_config
from config.database_manager import DatabaseManager
from config.validators.supabase_validator import SupabaseValidator

class NewConfigTester:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'errors': [],
            'warnings': []
        }
    
    def test_config_loading(self):
        """Prueba la carga de configuración"""
        print("\n🔧 Probando carga de configuración...")
        
        try:
            # Probar configuración de desarrollo
            config = AppConfig('development')
            
            # Verificar propiedades básicas
            assert config.environment == 'development'
            assert config.is_development() == True
            assert config.is_production() == False
            
            # Verificar que se pueden obtener valores
            debug = config.get('debug')
            port = config.get('port')
            
            self.results['tests']['config_loading'] = {
                'status': 'success',
                'environment': config.environment,
                'debug': debug,
                'port': port
            }
            
            print(f"   ✅ Configuración cargada: {config.environment}")
            print(f"   📊 Debug: {debug}, Puerto: {port}")
            
        except Exception as e:
            self.results['tests']['config_loading'] = {
                'status': 'failed',
                'error': str(e)
            }
            self.results['errors'].append(f"Error cargando configuración: {e}")
            print(f"   ❌ Error: {e}")
    
    def test_database_manager(self):
        """Prueba el gestor de base de datos"""
        print("\n🗄️ Probando gestor de base de datos...")
        
        try:
            config = get_config('development')
            db_manager = DatabaseManager(config)
            
            # Probar construcción de URL
            url = db_manager.get_connection_url()
            print(f"   📡 URL construida: {url[:50]}...")
            
            # Probar validación de conexión
            success, message = db_manager.validate_connection()
            
            if success:
                print(f"   ✅ Conexión exitosa: {message}")
                self.results['tests']['database_manager'] = {
                    'status': 'success',
                    'connection': True,
                    'message': message
                }
            else:
                print(f"   ❌ Conexión fallida: {message}")
                self.results['tests']['database_manager'] = {
                    'status': 'failed',
                    'connection': False,
                    'message': message
                }
                self.results['errors'].append(f"Conexión DB fallida: {message}")
            
            # Probar health status
            health = db_manager.get_health_status()
            print(f"   📊 Estado de salud: {health['connections']['current']['healthy']}")
            
        except Exception as e:
            self.results['tests']['database_manager'] = {
                'status': 'failed',
                'error': str(e)
            }
            self.results['errors'].append(f"Error en DatabaseManager: {e}")
            print(f"   ❌ Error: {e}")
    
    def test_supabase_validator(self):
        """Prueba el validador de Supabase"""
        print("\n🔍 Probando validador de Supabase...")
        
        try:
            config = get_config('development')
            
            # Obtener configuración de Supabase
            supabase_config = {
                'SUPABASE_HOST': config.get('SUPABASE_HOST'),
                'SUPABASE_PORT': config.get('SUPABASE_PORT'),
                'SUPABASE_USER': config.get('SUPABASE_USER'),
                'SUPABASE_DB_PASSWORD': config.get('SUPABASE_DB_PASSWORD'),
                'SUPABASE_DB': config.get('SUPABASE_DB'),
                'SUPABASE_URL': config.get('SUPABASE_URL')
            }
            
            # Validar configuración
            is_valid, errors = SupabaseValidator.validate_environment_config(supabase_config)
            
            if is_valid:
                print(f"   ✅ Configuración válida")
                self.results['tests']['supabase_validator'] = {
                    'status': 'success',
                    'valid': True,
                    'errors': []
                }
            else:
                print(f"   ⚠️  Problemas encontrados: {len(errors)}")
                for error in errors:
                    print(f"      • {error}")
                
                self.results['tests']['supabase_validator'] = {
                    'status': 'warning',
                    'valid': False,
                    'errors': errors
                }
                self.results['warnings'].extend(errors)
            
            # Obtener sugerencias
            suggestions = SupabaseValidator.suggest_fixes(supabase_config)
            if suggestions:
                print(f"   💡 Sugerencias:")
                for suggestion in suggestions:
                    print(f"      • {suggestion}")
            
        except Exception as e:
            self.results['tests']['supabase_validator'] = {
                'status': 'failed',
                'error': str(e)
            }
            self.results['errors'].append(f"Error en SupabaseValidator: {e}")
            print(f"   ❌ Error: {e}")
    
    def test_environment_switching(self):
        """Prueba el cambio entre entornos"""
        print("\n🔄 Probando cambio de entornos...")
        
        environments = ['development', 'production']
        
        for env in environments:
            try:
                print(f"\n   📋 Probando entorno: {env}")
                config = AppConfig(env)
                
                # Verificar configuración específica del entorno
                if env == 'development':
                    assert config.get('debug') == True
                    print(f"      ✅ Debug habilitado")
                elif env == 'production':
                    assert config.get('debug') == False
                    print(f"      ✅ Debug deshabilitado")
                
                # Probar DatabaseManager con este entorno
                db_manager = DatabaseManager(config)
                url = db_manager.get_connection_url()
                print(f"      📡 URL: {url[:50]}...")
                
            except Exception as e:
                print(f"      ❌ Error en {env}: {e}")
                self.results['errors'].append(f"Error en entorno {env}: {e}")
        
        self.results['tests']['environment_switching'] = {
            'status': 'success',
            'environments_tested': environments
        }
    
    def test_configuration_inheritance(self):
        """Prueba la herencia de configuración"""
        print("\n📋 Probando herencia de configuración...")
        
        try:
            config = get_config('development')
            
            # Verificar que se heredan valores de base.json
            app_name = config.get('app_name')
            version = config.get('version')
            
            # Verificar que se sobrescriben valores específicos del entorno
            debug = config.get('debug')
            port = config.get('port')
            
            print(f"   📊 App: {app_name} v{version}")
            print(f"   🔧 Debug: {debug}, Puerto: {port}")
            
            # Verificar configuración anidada
            pagination = config.get_nested('pagination.employees_per_page')
            print(f"   📄 Paginación: {pagination}")
            
            self.results['tests']['configuration_inheritance'] = {
                'status': 'success',
                'app_name': app_name,
                'version': version,
                'debug': debug,
                'port': port
            }
            
        except Exception as e:
            self.results['tests']['configuration_inheritance'] = {
                'status': 'failed',
                'error': str(e)
            }
            self.results['errors'].append(f"Error en herencia: {e}")
            print(f"   ❌ Error: {e}")
    
    def generate_report(self):
        """Genera reporte de pruebas"""
        print("\n" + "="*60)
        print("📊 REPORTE DE PRUEBAS - NUEVA ARQUITECTURA")
        print("="*60)
        
        # Contar resultados
        total_tests = len(self.results['tests'])
        successful = sum(1 for t in self.results['tests'].values() if t['status'] == 'success')
        failed = sum(1 for t in self.results['tests'].values() if t['status'] == 'failed')
        warnings = sum(1 for t in self.results['tests'].values() if t['status'] == 'warning')
        
        print(f"\n📈 Resumen:")
        print(f"   • Total de pruebas: {total_tests}")
        print(f"   • Exitosas: {successful} ✅")
        print(f"   • Fallidas: {failed} ❌")
        print(f"   • Advertencias: {warnings} ⚠️")
        
        # Mostrar detalles por prueba
        print(f"\n📋 Detalles por prueba:")
        for test_name, result in self.results['tests'].items():
            status_emoji = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'failed' else "⚠️"
            print(f"   {status_emoji} {test_name}: {result['status']}")
        
        # Mostrar errores
        if self.results['errors']:
            print(f"\n❌ Errores encontrados:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        # Mostrar advertencias
        if self.results['warnings']:
            print(f"\n⚠️ Advertencias:")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        # Guardar reporte
        reports_dir = Path(__file__).parent.parent / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f'new_config_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        print("="*60)
        
        return len(self.results['errors']) == 0
    
    def run(self):
        """Ejecuta todas las pruebas"""
        print("🚀 Iniciando pruebas de nueva arquitectura...")
        print("="*60)
        
        self.test_config_loading()
        self.test_database_manager()
        self.test_supabase_validator()
        self.test_environment_switching()
        self.test_configuration_inheritance()
        
        success = self.generate_report()
        
        if success:
            print("\n✅ Todas las pruebas pasaron exitosamente")
        else:
            print("\n❌ Algunas pruebas fallaron. Revisar errores arriba.")
        
        return success

def main():
    tester = NewConfigTester()
    success = tester.run()
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
