#!/usr/bin/env python3
"""
Punto de entrada principal para el despliegue de Team Time Management Backend
"""

import os
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar los módulos
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Importar la aplicación Flask
from app import create_app, db

# Crear la aplicación
app = create_app()

# Inicializar la base de datos si es necesario
with app.app_context():
    try:
        # Crear todas las tablas si no existen
        db.create_all()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"⚠️  Error inicializando base de datos: {e}")

if __name__ == '__main__':
    # Configuración para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Desactivar debug en producción
    )
