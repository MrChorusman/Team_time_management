#!/usr/bin/env python3
"""
Script de auditoría de configuración
Analiza todos los archivos .env y genera un reporte detallado
"""
import os
import glob
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

class ConfigAuditor:
    def __init__(self):
        self.backend_root = Path(__file__).parent.parent
        self.env_files = []
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'archivos_encontrados': [],
            'variables_por_archivo': {},
            'variables_duplicadas': defaultdict(list),
            'puertos_encontrados': set(),
            'problemas_detectados': [],
            'estadisticas': {}
        }
    
    def find_env_files(self):
        """Encuentra todos los archivos .env"""
        print("🔍 Buscando archivos .env...")
        
        # Buscar archivos .env en el directorio backend
        patterns = ['.env', '.env.*']
        for pattern in patterns:
            files = glob.glob(str(self.backend_root / pattern))
            self.env_files.extend(files)
        
        # Eliminar duplicados y ordenar
        self.env_files = sorted(list(set(self.env_files)))
        self.report['archivos_encontrados'] = [str(Path(f).name) for f in self.env_files]
        
        print(f"   Encontrados {len(self.env_files)} archivos")
        return self.env_files
    
    def analyze_file(self, filepath):
        """Analiza un archivo .env específico"""
        variables = {}
        line_count = 0
        
        try:
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    line_count += 1
                    
                    # Ignorar líneas vacías y comentarios
                    if not line or line.startswith('#'):
                        continue
                    
                    # Buscar variables
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Análisis especial para ciertas variables
                        if 'PORT' in key:
                            self.report['puertos_encontrados'].add(f"{key}={value}")
                        
                        # Detectar valores problemáticos
                        if value in ['', 'your_', 'change_me', 'xxx']:
                            self.report['problemas_detectados'].append({
                                'archivo': Path(filepath).name,
                                'variable': key,
                                'problema': 'Valor placeholder o vacío',
                                'valor': value
                            })
                        
                        variables[key] = {
                            'valor': value,
                            'linea': line_num
                        }
        
        except Exception as e:
            self.report['problemas_detectados'].append({
                'archivo': Path(filepath).name,
                'problema': f'Error leyendo archivo: {str(e)}'
            })
        
        return variables, line_count
    
    def analyze_all_files(self):
        """Analiza todos los archivos encontrados"""
        print("\n📋 Analizando archivos...")
        
        total_vars = 0
        all_vars = defaultdict(list)
        
        for filepath in self.env_files:
            filename = Path(filepath).name
            print(f"   Analizando {filename}...")
            
            variables, line_count = self.analyze_file(filepath)
            self.report['variables_por_archivo'][filename] = {
                'total_variables': len(variables),
                'total_lineas': line_count,
                'variables': list(variables.keys())
            }
            
            total_vars += len(variables)
            
            # Rastrear dónde aparece cada variable
            for var_name in variables:
                all_vars[var_name].append(filename)
        
        # Encontrar variables duplicadas
        for var_name, files in all_vars.items():
            if len(files) > 1:
                self.report['variables_duplicadas'][var_name] = files
        
        # Estadísticas
        self.report['estadisticas'] = {
            'total_archivos': len(self.env_files),
            'total_variables': total_vars,
            'variables_unicas': len(all_vars),
            'variables_duplicadas': len(self.report['variables_duplicadas']),
            'archivos_con_problemas': len(set(p['archivo'] for p in self.report['problemas_detectados'] if 'archivo' in p))
        }
    
    def analyze_inconsistencies(self):
        """Analiza inconsistencias entre archivos"""
        print("\n🔍 Analizando inconsistencias...")
        
        # Buscar variables de Supabase inconsistentes
        supabase_vars = defaultdict(dict)
        
        for filepath in self.env_files:
            filename = Path(filepath).name
            variables, _ = self.analyze_file(filepath)
            
            for var_name, var_info in variables.items():
                if 'SUPABASE' in var_name:
                    supabase_vars[var_name][filename] = var_info['valor']
        
        # Detectar inconsistencias en puertos
        for var_name, file_values in supabase_vars.items():
            if 'PORT' in var_name:
                unique_values = set(v for v in file_values.values() if v)
                if len(unique_values) > 1:
                    self.report['problemas_detectados'].append({
                        'tipo': 'Inconsistencia de puerto',
                        'variable': var_name,
                        'valores': dict(file_values)
                    })
        
        # Detectar mezcla de configuraciones DEV/PROD
        for filepath in self.env_files:
            filename = Path(filepath).name
            variables, _ = self.analyze_file(filepath)
            
            has_dev = any('_DEV_' in k for k in variables.keys())
            has_prod = any(k.startswith('SUPABASE_') and '_DEV_' not in k for k in variables.keys())
            
            if has_dev and has_prod:
                self.report['problemas_detectados'].append({
                    'archivo': filename,
                    'problema': 'Mezcla de variables DEV y PROD en el mismo archivo'
                })
    
    def generate_report(self):
        """Genera el reporte final"""
        print("\n📊 Generando reporte...")
        
        # Crear directorio de reportes si no existe
        reports_dir = self.backend_root / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        # Guardar reporte JSON
        report_file = reports_dir / f'audit_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        
        # Generar reporte en texto
        self.print_report()
        
        return report_file
    
    def print_report(self):
        """Imprime el reporte en formato legible"""
        print("\n" + "="*60)
        print("📊 REPORTE DE AUDITORÍA DE CONFIGURACIÓN")
        print("="*60)
        
        print(f"\n📁 Archivos encontrados: {len(self.report['archivos_encontrados'])}")
        for file in self.report['archivos_encontrados']:
            print(f"   • {file}")
        
        print(f"\n📈 Estadísticas:")
        for key, value in self.report['estadisticas'].items():
            print(f"   • {key}: {value}")
        
        if self.report['variables_duplicadas']:
            print(f"\n🔄 Variables duplicadas: {len(self.report['variables_duplicadas'])}")
            for var, files in self.report['variables_duplicadas'].items():
                print(f"   • {var}: aparece en {', '.join(files)}")
        
        if self.report['puertos_encontrados']:
            print(f"\n🔌 Puertos configurados:")
            for port_config in sorted(self.report['puertos_encontrados']):
                print(f"   • {port_config}")
        
        if self.report['problemas_detectados']:
            print(f"\n⚠️  Problemas detectados: {len(self.report['problemas_detectados'])}")
            for problema in self.report['problemas_detectados']:
                if 'archivo' in problema:
                    print(f"   • [{problema['archivo']}] {problema.get('problema', '')} - {problema.get('variable', '')}")
                else:
                    print(f"   • {problema}")
        
        print(f"\n📄 Reporte completo guardado en: reports/")
        print("="*60)
    
    def run(self):
        """Ejecuta la auditoría completa"""
        print("🔧 Iniciando auditoría de configuración...")
        print(f"📁 Directorio: {self.backend_root}")
        
        self.find_env_files()
        self.analyze_all_files()
        self.analyze_inconsistencies()
        report_file = self.generate_report()
        
        print(f"\n✅ Auditoría completada")
        print(f"📄 Reporte guardado en: {report_file}")
        
        return self.report

def main():
    """Función principal"""
    auditor = ConfigAuditor()
    report = auditor.run()
    
    # Retornar código de salida basado en problemas encontrados
    if report['problemas_detectados']:
        return 1
    return 0

if __name__ == '__main__':
    exit(main())
