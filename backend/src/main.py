#!/usr/bin/env python3
"""
Punto de entrada principal para el despliegue de Team Time Management Backend
"""

# Importar la aplicación Flask
from app import app

# La aplicación ya está configurada e inicializada en app.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
