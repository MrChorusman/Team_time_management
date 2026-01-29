#!/usr/bin/env python3
"""
Script para aplicar índices de rendimiento a la base de datos
Ejecuta la migración SQL de índices de optimización
"""
import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cargar variables de entorno - intentar primero .env.production, luego .env.development
backend_dir = Path(__file__).parent.parent
env_files = [
    backend_dir / '.env.production',  # Priorizar producción
    backend_dir / '.env.development',
    backend_dir / '.env'
]

for env_file in env_files:
    if env_file.exists():
        print(f"📄 Cargando variables de entorno desde: {env_file.name}")
        load_dotenv(env_file)
        break

def apply_indexes():
    """Aplica los índices de rendimiento a la base de datos"""
    try:
        # Leer configuración de base de datos
        from supabase_config import SupabaseConfig
        import re
        
        # Obtener credenciales
        db_password = os.environ.get('SUPABASE_DEV_DB_PASSWORD') or os.environ.get('SUPABASE_DB_PASSWORD')
        db_name = os.environ.get('SUPABASE_DB', 'postgres')
        
        if not db_password:
            print("❌ Error: No se encontró contraseña de base de datos")
            return False
        
        # Obtener project ref de la URL de Supabase
        project_url = os.environ.get('SUPABASE_URL') or os.environ.get('SUPABASE_DEV_URL')
        project_ref = None
        
        if project_url:
            match = re.search(r'https://([^.]+)\.supabase\.co', project_url)
            if match:
                project_ref = match.group(1)
                print(f"📋 Project ref detectado: {project_ref}")
        
        if not project_ref:
            print("❌ Error: No se pudo detectar el project ref de Supabase")
            return False
        
        # Usar Session Pooler de Supabase (disponible incluso cuando el proyecto está pausado)
        # Detectar región del pooler desde variables de entorno o usar la correcta según project ref
        pooler_host = os.environ.get('SUPABASE_HOST', 'aws-0-eu-west-3.pooler.supabase.com')
        pooler_port = os.environ.get('SUPABASE_PORT', '6543')
        
        # Si el puerto es 5432, usar 6543 para el pooler
        if pooler_port == '5432':
            pooler_port = '6543'
        
        # Si el host no es un pooler, usar el pooler correcto según la región
        if 'pooler' not in pooler_host:
            # Detectar región desde project ref o usar la correcta
            # Para xmaxohyxgsthligskjvg (producción): aws-0-eu-west-3
            # Para qsbvoyjqfrhaqncqtknv (desarrollo): aws-1-eu-west-1
            if project_ref == 'xmaxohyxgsthligskjvg':
                pooler_host = 'aws-0-eu-west-3.pooler.supabase.com'
            else:
                pooler_host = 'aws-1-eu-west-1.pooler.supabase.com'
        
        db_user = f"postgres.{project_ref}"  # Formato requerido para pooler
        
        db_url = f"postgresql://{db_user}:{db_password}@{pooler_host}:{pooler_port}/{db_name}"
        print(f"🔌 Usando Session Pooler de Supabase")
        print(f"   Project ref: {project_ref}")
        print(f"   Host: {pooler_host}:{pooler_port}")
        print(f"   Usuario: {db_user}")
        print(f"   Base de datos: {db_name}")
        
        # Leer archivo SQL de migración
        migration_file = Path(__file__).parent.parent / 'migrations' / 'add_performance_indexes.sql'
        
        if not migration_file.exists():
            print(f"❌ Error: Archivo de migración no encontrado: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Conectar a la base de datos
        print("🔌 Conectando a la base de datos...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Ejecutar migración
        print("📊 Aplicando índices de rendimiento...")
        cursor.execute(sql_content)
        
        # Verificar índices creados
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename IN ('calendar_activity', 'holiday', 'employee')
                AND indexname LIKE 'idx_%'
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        
        print(f"\n✅ Migración completada exitosamente")
        print(f"📈 Índices creados: {len(indexes)}\n")
        
        if indexes:
            print("Índices aplicados:")
            for schema, table, index_name, index_def in indexes:
                print(f"  - {table}.{index_name}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error aplicando índices: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Aplicando índices de rendimiento...\n")
    success = apply_indexes()
    
    if success:
        print("\n✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Proceso falló")
        sys.exit(1)
