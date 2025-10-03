#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para crear tablas en Supabase
"""

import os
import sys
sys.path.insert(0, '.')

# Configurar variables de entorno
os.environ['SUPABASE_URL'] = 'https://xmaxohyxgsthligskjvg.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtYXhvaHl4Z3N0aGxpZ3NranZnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTY2MjY0OCwiZXhwIjoyMDY1MjM4NjQ4fQ.GEytEALEkruS6aa8LZ1A8GMORvRW68Q0os6WIrzAJ_k'
os.environ['SUPABASE_DB_PASSWORD'] = 'Littletosti29.'
os.environ['SUPABASE_HOST'] = 'aws-0-eu-west-3.pooler.supabase.com'
os.environ['SUPABASE_PORT'] = '6543'
os.environ['SUPABASE_DB_USER'] = 'postgres.xmaxohyxgsthligskjvg'

def create_tables():
    """Crear tablas en Supabase"""
    print("Creando tablas en Supabase...")
    
    try:
        # Importar directamente desde el archivo app.py
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        from models.user import db
        create_app = app_module.create_app
        
        app = create_app()
        
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            print("Tablas creadas exitosamente en Supabase")
            return True
            
    except Exception as e:
        print(f"Error creando tablas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    create_tables()
