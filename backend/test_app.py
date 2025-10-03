#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la importación del módulo app
"""

import sys
sys.path.append('.')

try:
    import app
    print("Module app imported successfully")
    print("Module app:", app)
    print("Attributes:", dir(app))
    
    if hasattr(app, 'create_app'):
        print("create_app found")
        app_instance = app.create_app()
        print("App created successfully")
    else:
        print("create_app NOT found")
        
except Exception as e:
    print("Error importing app:", str(e))
    import traceback
    traceback.print_exc()
