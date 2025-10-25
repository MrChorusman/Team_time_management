#!/usr/bin/env python3
"""
Script de limpieza para eliminar archivos .env duplicados y obsoletos
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

class EnvironmentCleaner:
    def __init__(self):
        self.backend_dir = Path(__file__).parent.parent
        self.backups_dir = self.backend_dir / 'backups' / 'env_cleanup'
        
        # Archivos a mantener (nueva arquitectura)
        self.keep_files = {
            '.env',  # Archivo activo actual
            'config/environments/.env.development',
            'config/environments/.env.production'
        }
        
        # Archivos obsoletos a eliminar
        self.obsolete_files = [
            '.env.backup',
            '.env.backup_20251025_121023',
            '.env.development-production-like',
            '.env.development-test',
            '.env.local'
        ]
    
    def create_backup_dir(self):
        """Crear directorio de backup"""
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio de backup: {self.backups_dir}")
    
    def backup_obsolete_files(self):
        """Crear backup de archivos obsoletos antes de eliminarlos"""
        print("\n📦 Creando backup de archivos obsoletos...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for file_name in self.obsolete_files:
            file_path = self.backend_dir / file_name
            
            if file_path.exists():
                backup_name = f"{file_name}_{timestamp}"
                backup_path = self.backups_dir / backup_name
                
                shutil.copy2(file_path, backup_path)
                print(f"   ✅ Backup: {file_name} → {backup_name}")
            else:
                print(f"   ⚠️  No encontrado: {file_name}")
    
    def remove_obsolete_files(self):
        """Eliminar archivos obsoletos"""
        print("\n🗑️  Eliminando archivos obsoletos...")
        
        for file_name in self.obsolete_files:
            file_path = self.backend_dir / file_name
            
            if file_path.exists():
                file_path.unlink()
                print(f"   ✅ Eliminado: {file_name}")
            else:
                print(f"   ⚠️  Ya no existe: {file_name}")
    
    def verify_cleanup(self):
        """Verificar que la limpieza fue exitosa"""
        print("\n🔍 Verificando limpieza...")
        
        # Verificar archivos mantenidos
        print("   📋 Archivos mantenidos:")
        for file_name in self.keep_files:
            file_path = self.backend_dir / file_name
            if file_path.exists():
                print(f"      ✅ {file_name}")
            else:
                print(f"      ❌ {file_name} - No encontrado")
        
        # Verificar archivos eliminados
        print("   🗑️  Archivos eliminados:")
        for file_name in self.obsolete_files:
            file_path = self.backend_dir / file_name
            if not file_path.exists():
                print(f"      ✅ {file_name} - Eliminado")
            else:
                print(f"      ❌ {file_name} - Aún existe")
    
    def show_current_structure(self):
        """Mostrar estructura actual de archivos .env"""
        print("\n📁 Estructura actual de archivos .env:")
        print("=" * 50)
        
        # Archivos en directorio raíz
        env_files_root = list(self.backend_dir.glob('.env*'))
        if env_files_root:
            print("   📂 Directorio raíz:")
            for file_path in sorted(env_files_root):
                print(f"      • {file_path.name}")
        
        # Archivos en config/environments
        env_files_config = list((self.backend_dir / 'config' / 'environments').glob('.env*'))
        if env_files_config:
            print("   📂 config/environments/:")
            for file_path in sorted(env_files_config):
                print(f"      • {file_path.name}")
        
        print("=" * 50)
    
    def generate_cleanup_report(self):
        """Generar reporte de limpieza"""
        print("\n" + "="*60)
        print("📊 REPORTE DE LIMPIEZA")
        print("="*60)
        
        # Contar archivos
        total_obsolete = len(self.obsolete_files)
        total_kept = len(self.keep_files)
        
        print(f"\n📈 Resumen:")
        print(f"   • Archivos obsoletos eliminados: {total_obsolete}")
        print(f"   • Archivos mantenidos: {total_kept}")
        print(f"   • Backups creados en: {self.backups_dir}")
        
        # Mostrar estructura final
        self.show_current_structure()
        
        print(f"\n✅ Limpieza completada")
        print("="*60)
    
    def run(self):
        """Ejecutar limpieza completa"""
        print("🧹 Iniciando limpieza de archivos .env obsoletos...")
        print("="*60)
        
        self.create_backup_dir()
        self.backup_obsolete_files()
        self.remove_obsolete_files()
        self.verify_cleanup()
        self.generate_cleanup_report()
        
        return True

def main():
    cleaner = EnvironmentCleaner()
    success = cleaner.run()
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
