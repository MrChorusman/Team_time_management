#!/usr/bin/env python3
"""
Script para migrar configuración de archivos .env antiguos al nuevo sistema
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import json

class EnvMigrator:
    def __init__(self):
        self.backend_root = Path(__file__).parent.parent
        self.old_env_files = []
        self.new_config_dir = self.backend_root / 'config' / 'environments'
        self.backup_dir = self.backend_root / 'backups' / 'env_migration'
        
    def find_old_env_files(self):
        """Encuentra todos los archivos .env antiguos"""
        print("🔍 Buscando archivos .env antiguos...")
        
        patterns = ['.env', '.env.*']
        for pattern in patterns:
            files = list(self.backend_root.glob(pattern))
            self.old_env_files.extend(files)
        
        # Eliminar duplicados
        self.old_env_files = list(set(self.old_env_files))
        print(f"   Encontrados {len(self.old_env_files)} archivos")
        
        return self.old_env_files
    
    def create_backup(self):
        """Crea backup de todos los archivos .env"""
        print("\n📦 Creando backup de archivos .env...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for env_file in self.old_env_files:
            if env_file.exists():
                backup_name = f"{env_file.name}_{timestamp}"
                backup_path = self.backup_dir / backup_name
                shutil.copy2(env_file, backup_path)
                print(f"   ✅ Backup: {backup_name}")
        
        print(f"   📁 Backups guardados en: {self.backup_dir}")
    
    def prepare_new_env_files(self):
        """Prepara los nuevos archivos .env desde los ejemplos"""
        print("\n🔧 Preparando nuevos archivos de configuración...")
        
        # Copiar archivos de ejemplo
        examples = [
            ('env.development.example', '.env.development'),
            ('env.production.example', '.env.production')
        ]
        
        for example, target in examples:
            example_path = self.new_config_dir / example
            target_path = self.new_config_dir / target
            
            if example_path.exists():
                # Copiar archivo de ejemplo
                shutil.copy2(example_path, target_path)
                print(f"   ✅ Creado: {target}")
                
                # Hacer el archivo escribible
                os.chmod(target_path, 0o644)
    
    def extract_working_config(self):
        """Extrae la configuración que funciona de .env.production"""
        print("\n📋 Extrayendo configuración funcional...")
        
        # Buscar el archivo .env.production que sabemos que funciona
        prod_env = self.backend_root / '.env.production'
        
        if not prod_env.exists():
            print("   ❌ No se encontró .env.production")
            return None
        
        working_config = {}
        
        with open(prod_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Solo extraer las credenciales de Supabase que funcionan
                    if key.startswith('SUPABASE_') and 'your_' not in value:
                        working_config[key] = value
        
        print(f"   ✅ Extraídas {len(working_config)} variables funcionales")
        return working_config
    
    def update_env_file(self, filepath, updates):
        """Actualiza un archivo .env con nuevos valores"""
        if not updates:
            return
            
        # Leer archivo actual
        lines = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                lines = f.readlines()
        
        # Actualizar valores
        updated = False
        for i, line in enumerate(lines):
            if '=' in line:
                key = line.split('=', 1)[0].strip()
                if key in updates:
                    lines[i] = f"{key}={updates[key]}\n"
                    updated = True
        
        # Escribir archivo actualizado
        if updated:
            with open(filepath, 'w') as f:
                f.writelines(lines)
            print(f"   ✅ Actualizado: {filepath.name}")
    
    def create_instructions(self):
        """Crea instrucciones para completar la migración"""
        instructions_file = self.new_config_dir / 'MIGRATION_INSTRUCTIONS.md'
        
        content = """# 📋 INSTRUCCIONES DE MIGRACIÓN

## ✅ COMPLETADO AUTOMÁTICAMENTE:
1. Backup de archivos .env antiguos en `backups/env_migration/`
2. Creación de nuevos archivos de configuración
3. Migración de credenciales funcionales de Supabase

## ⚠️ ACCIÓN REQUERIDA:

### 1. RENOMBRAR ARCHIVOS:
```bash
cd backend/config/environments
mv env.development.example .env.development
mv env.production.example .env.production
```

### 2. CONFIGURAR DESARROLLO:
Editar `backend/config/environments/.env.development`:
- Verificar que las credenciales de Supabase estén correctas
- Configurar email si necesario (o dejar MOCK_EMAIL_MODE=true)
- Configurar Google OAuth si necesario (o dejar vacío para modo mock)

### 3. CONFIGURAR PRODUCCIÓN:
Editar `backend/config/environments/.env.production`:
- Actualizar SECRET_KEY y SECURITY_PASSWORD_SALT con valores seguros
- Configurar credenciales reales de email
- Configurar Google OAuth con credenciales reales
- Verificar credenciales de Supabase

### 4. CAMBIAR AL NUEVO SISTEMA:
```bash
# Usar el nuevo sistema de configuración
cd backend
python scripts/env_manager.py switch development

# Verificar configuración
python scripts/system_diagnostic.py
```

### 5. LIMPIAR ARCHIVOS ANTIGUOS:
Una vez verificado que todo funciona:
```bash
# Eliminar archivos .env antiguos del directorio backend/
rm backend/.env*
```

## 📁 NUEVA ESTRUCTURA:
```
backend/
├── config/
│   ├── environments/
│   │   ├── .env.development    # Variables para desarrollo
│   │   ├── .env.production     # Variables para producción
│   │   ├── base.json           # Config compartida
│   │   ├── development.json    # Config de desarrollo
│   │   └── production.json     # Config de producción
│   ├── app_config.py           # Gestor de configuración
│   └── database_manager.py     # Gestor de conexiones
└── .env                        # Symlink al entorno activo
```
"""
        
        with open(instructions_file, 'w') as f:
            f.write(content)
        
        print(f"\n📄 Instrucciones guardadas en: {instructions_file}")
    
    def run(self):
        """Ejecuta la migración completa"""
        print("🚀 Iniciando migración de configuración...")
        print("="*60)
        
        # 1. Encontrar archivos antiguos
        self.find_old_env_files()
        
        # 2. Crear backup
        self.create_backup()
        
        # 3. Preparar nuevos archivos
        self.prepare_new_env_files()
        
        # 4. Extraer configuración funcional
        working_config = self.extract_working_config()
        
        # 5. Actualizar archivos de desarrollo con config funcional
        if working_config:
            dev_env = self.new_config_dir / '.env.development'
            self.update_env_file(dev_env, working_config)
        
        # 6. Crear instrucciones
        self.create_instructions()
        
        print("\n✅ Migración completada")
        print("📋 Revisa MIGRATION_INSTRUCTIONS.md para los siguientes pasos")

def main():
    migrator = EnvMigrator()
    migrator.run()

if __name__ == '__main__':
    main()
