#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para verificar variables de entorno
"""

import os

def check_environment():
    print "Verificando variables de entorno..."
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY', 
        'SUPABASE_DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print "   [OK] {}: {}".format(var, masked_value)
        else:
            print "   [ERROR] {}: NO CONFIGURADO".format(var)
            missing_vars.append(var)
    
    if missing_vars:
        print "\nVariables faltantes: {}".format(', '.join(missing_vars))
        print "Crear archivo .env con estas variables antes de continuar"
        return False
    
    print "Todas las variables de entorno estan configuradas"
    return True

if __name__ == '__main__':
    check_environment()
