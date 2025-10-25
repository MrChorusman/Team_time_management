#!/usr/bin/env python3
"""
Script para probar todas las conexiones de Supabase configuradas
"""
import os
import sys
import psycopg2
from datetime import datetime
from pathlib import Path
import json
from collections import defaultdict

# Añadir el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

class ConnectionTester:
    def __init__(self):
        self.backend_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'connections_tested': 0,
            'connections_successful': 0,
            'connections_failed': 0,
            'details': {}
        }
    
    def extract_connection_info(self, env_file):
        """Extrae información de conexión de un archivo .env"""
        connection_info = {}
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Buscar variables de Supabase
                        if 'SUPABASE' in key and any(x in key for x in ['HOST', 'PORT', 'USER', 'PASSWORD', 'DB']):
                            connection_info[key] = value
        
        except Exception as e:
            print(f"   ❌ Error leyendo {env_file}: {str(e)}")
            
        return connection_info
    
    def build_connection_url(self, info, prefix='SUPABASE'):
        """Construye URL de conexión desde las variables"""
        host = info.get(f'{prefix}_HOST', info.get('SUPABASE_HOST'))
        port = info.get(f'{prefix}_PORT', info.get('SUPABASE_PORT'))
        user = info.get(f'{prefix}_USER', info.get('SUPABASE_USER'))
        password = info.get(f'{prefix}_DB_PASSWORD', info.get('SUPABASE_DB_PASSWORD'))
        database = info.get(f'{prefix}_DB', info.get('SUPABASE_DB', 'postgres'))
        
        if not all([host, port, user, password]):
            return None
            
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def test_connection(self, connection_url, name):
        """Prueba una conexión específica"""
        print(f"\n🔌 Probando conexión: {name}")
        
        # Ocultar credenciales en el log
        safe_url = connection_url.replace(
            connection_url.split('@')[0].split('://')[-1],
            '***:***'
        ) if '@' in connection_url else connection_url
        
        print(f"   URL: {safe_url}")
        
        try:
            # Intentar conectar
            conn = psycopg2.connect(connection_url, connect_timeout=10)
            cursor = conn.cursor()
            
            # Obtener información del servidor
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            
            cursor.execute("SELECT current_user;")
            current_user = cursor.fetchone()[0]
            
            # Verificar tablas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            result = {
                'status': 'success',
                'version': version.split(',')[0],
                'database': db_name,
                'user': current_user,
                'tables': table_count,
                'connection_type': 'Pooler' if ':6543' in connection_url else 'Direct'
            }
            
            print(f"   ✅ Conexión exitosa")
            print(f"   📊 Base de datos: {db_name}")
            print(f"   👤 Usuario: {current_user}")
            print(f"   📋 Tablas: {table_count}")
            print(f"   🔌 Tipo: {result['connection_type']}")
            
            self.results['connections_successful'] += 1
            
        except psycopg2.OperationalError as e:
            result = {
                'status': 'failed',
                'error': str(e),
                'error_type': 'OperationalError'
            }
            print(f"   ❌ Error de conexión: {str(e)}")
            self.results['connections_failed'] += 1
            
        except Exception as e:
            result = {
                'status': 'failed',
                'error': str(e),
                'error_type': type(e).__name__
            }
            print(f"   ❌ Error inesperado: {str(e)}")
            self.results['connections_failed'] += 1
        
        self.results['connections_tested'] += 1
        self.results['details'][name] = result
        
        return result
    
    def test_all_env_files(self):
        """Prueba conexiones desde todos los archivos .env"""
        print("🔍 Buscando archivos .env...")
        
        env_files = list(self.backend_root.glob('.env*'))
        print(f"   Encontrados {len(env_files)} archivos")
        
        connections_to_test = {}
        
        # Extraer conexiones únicas
        for env_file in env_files:
            if env_file.is_file():
                print(f"\n📄 Analizando {env_file.name}...")
                info = self.extract_connection_info(env_file)
                
                # Buscar conexiones de producción
                if any(k.startswith('SUPABASE_') and '_DEV_' not in k for k in info.keys()):
                    url = self.build_connection_url(info, 'SUPABASE')
                    if url:
                        connections_to_test[f"{env_file.name} (PROD)"] = url
                
                # Buscar conexiones de desarrollo
                if any('_DEV_' in k for k in info.keys()):
                    url = self.build_connection_url(info, 'SUPABASE_DEV')
                    if url:
                        connections_to_test[f"{env_file.name} (DEV)"] = url
        
        # Eliminar duplicados manteniendo el nombre
        unique_connections = {}
        for name, url in connections_to_test.items():
            if url not in unique_connections.values():
                unique_connections[name] = url
        
        print(f"\n📊 Conexiones únicas encontradas: {len(unique_connections)}")
        
        # Probar cada conexión
        for name, url in unique_connections.items():
            self.test_connection(url, name)
    
    def test_mcp_connections(self):
        """Intenta detectar y probar conexiones MCP si están configuradas"""
        print("\n🔍 Buscando configuraciones MCP...")
        
        # Buscar en variables de entorno actuales
        mcp_vars = {k: v for k, v in os.environ.items() if 'MCP' in k and 'SUPABASE' in k}
        
        if mcp_vars:
            print(f"   Encontradas {len(mcp_vars)} variables MCP")
            for var, value in mcp_vars.items():
                print(f"   • {var}: {value[:20]}...")
        else:
            print("   ⚠️  No se encontraron variables MCP de Supabase")
            print("   💡 Los MCPs mencionados (MCP-supabase-PRO, MCP-Supabase-DEV) no están configurados como variables de entorno")
    
    def generate_report(self):
        """Genera reporte de resultados"""
        print("\n" + "="*60)
        print("📊 REPORTE DE PRUEBAS DE CONEXIÓN")
        print("="*60)
        
        print(f"\n📈 Resumen:")
        print(f"   • Conexiones probadas: {self.results['connections_tested']}")
        print(f"   • Exitosas: {self.results['connections_successful']} ✅")
        print(f"   • Fallidas: {self.results['connections_failed']} ❌")
        
        # Agrupar por estado
        successful = {k: v for k, v in self.results['details'].items() if v['status'] == 'success'}
        failed = {k: v for k, v in self.results['details'].items() if v['status'] == 'failed'}
        
        if successful:
            print(f"\n✅ Conexiones exitosas ({len(successful)}):")
            for name, details in successful.items():
                print(f"   • {name}")
                print(f"     - Base de datos: {details['database']}")
                print(f"     - Tipo: {details['connection_type']}")
                print(f"     - Tablas: {details['tables']}")
        
        if failed:
            print(f"\n❌ Conexiones fallidas ({len(failed)}):")
            for name, details in failed.items():
                print(f"   • {name}")
                print(f"     - Error: {details['error_type']}")
                print(f"     - Mensaje: {details['error'][:100]}...")
        
        # Guardar reporte
        reports_dir = self.backend_root / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f'connection_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        print("="*60)
    
    def run(self):
        """Ejecuta todas las pruebas"""
        print("🔧 Iniciando pruebas de conexión...")
        print(f"📁 Directorio: {self.backend_root}")
        
        self.test_all_env_files()
        self.test_mcp_connections()
        self.generate_report()
        
        return self.results

def main():
    """Función principal"""
    tester = ConnectionTester()
    results = tester.run()
    
    # Retornar código basado en resultados
    if results['connections_failed'] > 0:
        return 1
    return 0

if __name__ == '__main__':
    exit(main())
