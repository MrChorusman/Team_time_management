#!/usr/bin/env python3
"""
Tests de integración para la nueva arquitectura de configuración
"""
import unittest
import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Añadir el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.app_config import AppConfig, get_config
from config.database_manager import DatabaseManager
from config.validators.supabase_validator import SupabaseValidator

class TestAppConfig(unittest.TestCase):
    """Tests para la clase AppConfig"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / 'config'
        self.environments_dir = self.config_dir / 'environments'
    
    def test_config_loading_development(self):
        """Test carga de configuración de desarrollo"""
        try:
            config = AppConfig('development')
            
            # Verificar propiedades básicas
            self.assertEqual(config.environment, 'development')
            self.assertTrue(config.is_development())
            self.assertFalse(config.is_production())
            
            # Verificar que se pueden obtener valores
            debug = config.get('debug')
            port = config.get('port')
            
            self.assertIsNotNone(debug)
            self.assertIsNotNone(port)
            
        except Exception as e:
            self.fail(f"Error cargando configuración de desarrollo: {e}")
    
    def test_config_loading_production(self):
        """Test carga de configuración de producción"""
        try:
            config = AppConfig('production')
            
            # Verificar propiedades básicas
            self.assertEqual(config.environment, 'production')
            self.assertFalse(config.is_development())
            self.assertTrue(config.is_production())
            
            # Verificar que se pueden obtener valores
            debug = config.get('debug')
            port = config.get('port')
            
            self.assertIsNotNone(debug)
            self.assertIsNotNone(port)
            
        except Exception as e:
            self.fail(f"Error cargando configuración de producción: {e}")
    
    def test_config_inheritance(self):
        """Test herencia de configuración desde base.json"""
        try:
            config = get_config('development')
            
            # Verificar que se heredan valores de base.json
            app_name = config.get('app_name')
            version = config.get('version')
            
            self.assertIsNotNone(app_name)
            self.assertIsNotNone(version)
            
            # Verificar configuración anidada
            pagination = config.get_nested('pagination.employees_per_page')
            self.assertIsNotNone(pagination)
            
        except Exception as e:
            self.fail(f"Error en herencia de configuración: {e}")
    
    def test_config_override(self):
        """Test sobrescritura de configuración con variables de entorno"""
        try:
            # Simular variable de entorno
            with patch.dict(os.environ, {'FLASK_DEBUG': 'false'}):
                config = get_config('development')
                # La configuración debería cargar correctamente
                self.assertIsNotNone(config)
                
        except Exception as e:
            self.fail(f"Error en sobrescritura de configuración: {e}")
    
    def test_invalid_environment(self):
        """Test manejo de entorno inválido"""
        with self.assertRaises(Exception):
            AppConfig('invalid_environment')

class TestDatabaseManager(unittest.TestCase):
    """Tests para la clase DatabaseManager"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.config = get_config('development')
    
    def test_database_manager_initialization(self):
        """Test inicialización del DatabaseManager"""
        try:
            db_manager = DatabaseManager(self.config)
            self.assertIsNotNone(db_manager)
            
        except Exception as e:
            self.fail(f"Error inicializando DatabaseManager: {e}")
    
    def test_connection_url_construction(self):
        """Test construcción de URL de conexión"""
        try:
            db_manager = DatabaseManager(self.config)
            url = db_manager.get_connection_url()
            
            self.assertIsNotNone(url)
            self.assertIn('postgresql://', url)
            
        except Exception as e:
            self.fail(f"Error construyendo URL de conexión: {e}")
    
    @patch('config.database_manager.create_engine')
    def test_connection_validation_mock(self, mock_create_engine):
        """Test validación de conexión con mock"""
        try:
            # Mock de conexión exitosa
            mock_engine = MagicMock()
            mock_connection = MagicMock()
            mock_connection.execute.return_value.fetchone.return_value = ('PostgreSQL', '17.4', 'postgres', 13)
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_create_engine.return_value = mock_engine
            
            db_manager = DatabaseManager(self.config)
            success, message = db_manager.validate_connection()
            
            self.assertTrue(success)
            self.assertIn('Conexión exitosa', message)
            
        except Exception as e:
            self.fail(f"Error en validación de conexión mock: {e}")
    
    def test_health_status(self):
        """Test estado de salud de la base de datos"""
        try:
            db_manager = DatabaseManager(self.config)
            health = db_manager.get_health_status()
            
            self.assertIsInstance(health, dict)
            self.assertIn('connections', health)
            self.assertIn('current', health['connections'])
            
        except Exception as e:
            self.fail(f"Error obteniendo estado de salud: {e}")

class TestSupabaseValidator(unittest.TestCase):
    """Tests para la clase SupabaseValidator"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.config = get_config('development')
    
    def test_supabase_config_extraction(self):
        """Test extracción de configuración de Supabase"""
        try:
            supabase_config = {
                'SUPABASE_HOST': self.config.get('SUPABASE_HOST'),
                'SUPABASE_PORT': self.config.get('SUPABASE_PORT'),
                'SUPABASE_USER': self.config.get('SUPABASE_USER'),
                'SUPABASE_DB_PASSWORD': self.config.get('SUPABASE_DB_PASSWORD'),
                'SUPABASE_DB': self.config.get('SUPABASE_DB'),
                'SUPABASE_URL': self.config.get('SUPABASE_URL')
            }
            
            # Verificar que se pueden extraer las configuraciones
            for key, value in supabase_config.items():
                self.assertIsNotNone(value, f"Configuración faltante: {key}")
                
        except Exception as e:
            self.fail(f"Error extrayendo configuración de Supabase: {e}")
    
    def test_supabase_validation(self):
        """Test validación de configuración de Supabase"""
        try:
            supabase_config = {
                'SUPABASE_HOST': 'aws-0-eu-west-3.pooler.supabase.com',
                'SUPABASE_PORT': '6543',
                'SUPABASE_USER': 'postgres.test',
                'SUPABASE_DB_PASSWORD': 'test_password',
                'SUPABASE_DB': 'postgres',
                'SUPABASE_URL': 'https://test.supabase.co'
            }
            
            is_valid, errors = SupabaseValidator.validate_environment_config(supabase_config)
            
            # La validación debería pasar o dar errores específicos
            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(errors, list)
            
        except Exception as e:
            self.fail(f"Error validando configuración de Supabase: {e}")
    
    def test_supabase_suggestions(self):
        """Test sugerencias de corrección de Supabase"""
        try:
            supabase_config = {
                'SUPABASE_HOST': 'invalid-host',
                'SUPABASE_PORT': '5432',  # Puerto incorrecto para pooler
                'SUPABASE_USER': 'invalid_user',
                'SUPABASE_DB_PASSWORD': 'test_password',
                'SUPABASE_DB': 'postgres',
                'SUPABASE_URL': 'invalid-url'
            }
            
            suggestions = SupabaseValidator.suggest_fixes(supabase_config)
            
            self.assertIsInstance(suggestions, list)
            # Debería haber sugerencias para los problemas
            self.assertGreater(len(suggestions), 0)
            
        except Exception as e:
            self.fail(f"Error obteniendo sugerencias de Supabase: {e}")

class TestEnvironmentSwitching(unittest.TestCase):
    """Tests para cambio de entornos"""
    
    def test_environment_switching_development(self):
        """Test cambio a entorno de desarrollo"""
        try:
            config = AppConfig('development')
            
            # Verificar configuración específica del entorno
            self.assertTrue(config.get('debug'))
            
            # Probar DatabaseManager con este entorno
            db_manager = DatabaseManager(config)
            url = db_manager.get_connection_url()
            self.assertIsNotNone(url)
            
        except Exception as e:
            self.fail(f"Error en cambio a desarrollo: {e}")
    
    def test_environment_switching_production(self):
        """Test cambio a entorno de producción"""
        try:
            config = AppConfig('production')
            
            # Verificar configuración específica del entorno
            self.assertFalse(config.get('debug'))
            
            # Probar DatabaseManager con este entorno
            db_manager = DatabaseManager(config)
            url = db_manager.get_connection_url()
            self.assertIsNotNone(url)
            
        except Exception as e:
            self.fail(f"Error en cambio a producción: {e}")

class TestConfigurationFiles(unittest.TestCase):
    """Tests para archivos de configuración"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / 'config'
        self.environments_dir = self.config_dir / 'environments'
    
    def test_config_files_exist(self):
        """Test que los archivos de configuración existen"""
        required_files = [
            'base.json',
            'development.json',
            'production.json',
            '.env.development',
            '.env.production'
        ]
        
        for file_name in required_files:
            file_path = self.environments_dir / file_name
            self.assertTrue(file_path.exists(), f"Archivo faltante: {file_name}")
    
    def test_json_config_valid(self):
        """Test que los archivos JSON son válidos"""
        json_files = ['base.json', 'development.json', 'production.json']
        
        for file_name in json_files:
            file_path = self.environments_dir / file_name
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                
                # Verificar campos requeridos
                self.assertIn('environment', config)
                self.assertIn('debug', config)
                self.assertIn('port', config)
                
            except Exception as e:
                self.fail(f"Error validando JSON {file_name}: {e}")
    
    def test_env_files_have_required_vars(self):
        """Test que los archivos .env tienen variables requeridas"""
        env_files = ['.env.development', '.env.production']
        required_vars = ['SECRET_KEY', 'FLASK_ENV', 'SUPABASE_URL', 'SUPABASE_KEY']
        
        for file_name in env_files:
            file_path = self.environments_dir / file_name
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                for var in required_vars:
                    self.assertIn(f"{var}=", content, f"Variable faltante {var} en {file_name}")
                    
            except Exception as e:
                self.fail(f"Error validando .env {file_name}: {e}")

class TestIntegration(unittest.TestCase):
    """Tests de integración completa"""
    
    def test_full_configuration_flow(self):
        """Test flujo completo de configuración"""
        try:
            # 1. Cargar configuración
            config = get_config('development')
            self.assertIsNotNone(config)
            
            # 2. Inicializar DatabaseManager
            db_manager = DatabaseManager(config)
            self.assertIsNotNone(db_manager)
            
            # 3. Construir URL de conexión
            url = db_manager.get_connection_url()
            self.assertIsNotNone(url)
            
            # 4. Validar configuración de Supabase
            supabase_config = {
                'SUPABASE_HOST': config.get('SUPABASE_HOST'),
                'SUPABASE_PORT': config.get('SUPABASE_PORT'),
                'SUPABASE_USER': config.get('SUPABASE_USER'),
                'SUPABASE_DB_PASSWORD': config.get('SUPABASE_DB_PASSWORD'),
                'SUPABASE_DB': config.get('SUPABASE_DB'),
                'SUPABASE_URL': config.get('SUPABASE_URL')
            }
            
            is_valid, errors = SupabaseValidator.validate_environment_config(supabase_config)
            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(errors, list)
            
        except Exception as e:
            self.fail(f"Error en flujo completo de configuración: {e}")
    
    def test_environment_consistency(self):
        """Test consistencia entre entornos"""
        environments = ['development', 'production']
        
        for env in environments:
            try:
                config = AppConfig(env)
                
                # Verificar que cada entorno tiene configuración válida
                self.assertIsNotNone(config.get('debug'))
                self.assertIsNotNone(config.get('port'))
                self.assertIsNotNone(config.get('database'))
                
                # Verificar DatabaseManager funciona
                db_manager = DatabaseManager(config)
                url = db_manager.get_connection_url()
                self.assertIsNotNone(url)
                
            except Exception as e:
                self.fail(f"Error en consistencia de entorno {env}: {e}")

def run_tests():
    """Ejecuta todos los tests"""
    print("🧪 Ejecutando tests de integración...")
    print("=" * 50)
    
    # Crear suite de tests
    test_suite = unittest.TestSuite()
    
    # Añadir tests
    test_classes = [
        TestAppConfig,
        TestDatabaseManager,
        TestSupabaseValidator,
        TestEnvironmentSwitching,
        TestConfigurationFiles,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FALLOS:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORES:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\n✅ Todos los tests pasaron exitosamente")
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
