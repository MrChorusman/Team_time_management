#!/usr/bin/env python3
"""
Script para gestionar ambos proyectos Supabase (desarrollo y producción)
"""

import requests
import json

class SupabaseManager:
    """Gestor de proyectos Supabase"""
    
    def __init__(self):
        self.projects = {
            'dev': {
                'name': 'Desarrollo',
                'url': 'https://qsbvoyjqfrhaqncqtknv.supabase.co',
                'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzYnZveWpxZnJoYXFuY3F0a252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODc5NTIsImV4cCI6MjA3Njg2Mzk1Mn0.i-ZBx7KFbSlCQl4yiAxcH95m6NZ96eyI4Ldxvyrct0k',
                'password': 'Littletosti29.',
                'user': 'postgres.qsbvoyjqfrhaqncqtknv'
            },
            'prod': {
                'name': 'Producción',
                'url': 'https://xmaxohyxgsthligskjvg.supabase.co',
                'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtYXhvaHl4Z3N0aGxpZ3NranZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk2NjI2NDgsImV4cCI6MjA2NTIzODY0OH0.O7D9MVMxCyg10dRLnJGZStamR4IOltRLx5wK5aENqB4',
                'password': 'Littletosti29.',
                'user': 'postgres.xmaxohyxgsthligskjvg'
            }
        }
    
    def test_connection(self, project_type):
        """Probar conexión a un proyecto"""
        project = self.projects[project_type]
        
        print(f"🔍 Probando conexión a {project['name']}...")
        print(f"📍 URL: {project['url']}")
        
        headers = {
            'apikey': project['anon_key'],
            'Authorization': f"Bearer {project['anon_key']}",
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{project['url']}/rest/v1/", headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Conexión exitosa a {project['name']}")
                return True
            else:
                print(f"❌ Error conectando a {project['name']}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error conectando a {project['name']}: {e}")
            return False
    
    def get_tables(self, project_type):
        """Obtener tablas de un proyecto"""
        project = self.projects[project_type]
        
        headers = {
            'apikey': project['anon_key'],
            'Authorization': f"Bearer {project['anon_key']}",
            'Content-Type': 'application/json'
        }
        
        try:
            # Obtener información de tablas usando la API REST
            response = requests.get(
                f"{project['url']}/rest/v1/",
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ Tablas disponibles en {project['name']}")
                # Nota: La API REST no devuelve directamente las tablas
                # Necesitarías usar el MCP o SQL directo
                return True
            else:
                print(f"❌ Error obteniendo tablas: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error obteniendo tablas: {e}")
            return False
    
    def migrate_data(self, source='prod', target='dev'):
        """Migrar datos entre proyectos"""
        print(f"🔄 Migrando datos de {self.projects[source]['name']} a {self.projects[target]['name']}")
        
        # Verificar conexiones
        if not self.test_connection(source):
            print(f"❌ No se puede conectar a {self.projects[source]['name']}")
            return False
        
        if not self.test_connection(target):
            print(f"❌ No se puede conectar a {self.projects[target]['name']}")
            return False
        
        print("✅ Ambas conexiones verificadas")
        print("📋 Para migrar datos, usa el MCP de Supabase:")
        print(f"   • Fuente: supabase-{source}")
        print(f"   • Destino: supabase-{target}")
        
        return True
    
    def show_status(self):
        """Mostrar estado de ambos proyectos"""
        print("📊 ESTADO DE PROYECTOS SUPABASE")
        print("=" * 40)
        
        for project_type, project in self.projects.items():
            print(f"\n🔍 {project['name'].upper()}:")
            print(f"   URL: {project['url']}")
            print(f"   Usuario: {project['user']}")
            print(f"   Estado: {'✅ Activo' if self.test_connection(project_type) else '❌ Inactivo'}")

def main():
    """Función principal"""
    manager = SupabaseManager()
    
    print("🔧 GESTOR DE PROYECTOS SUPABASE")
    print("=" * 40)
    print("Proyectos configurados:")
    print("  • Desarrollo: qsbvoyjqfrhaqncqtknv")
    print("  • Producción: xmaxohyxgsthligskjvg")
    print()
    
    # Mostrar estado
    manager.show_status()
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Reinicia Cursor para activar los nuevos MCPs")
    print("2. Usa 'supabase-dev' para desarrollo")
    print("3. Usa 'supabase-prod' para producción")
    print("4. Migra datos usando los MCPs")

if __name__ == "__main__":
    main()
