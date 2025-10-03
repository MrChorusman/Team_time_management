#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para verificar la configuración de Supabase
"""

import os
import sys
from dotenv import load_dotenv

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_environment_variables():
    """Probar variables de entorno"""
    print("Verificando variables de entorno...")
    
    # Cargar variables de entorno
    load_dotenv()
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY', 
        'SUPABASE_DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mostrar solo los primeros caracteres por seguridad
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"   [OK] {var}: {masked_value}")
        else:
            print(f"   [ERROR] {var}: NO CONFIGURADO")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\nVariables faltantes: {', '.join(missing_vars)}")
        print("Crear archivo .env con estas variables antes de continuar")
        return False
    
    print("Todas las variables de entorno estan configuradas")
    return True

def test_supabase_config():
    """Probar configuración de Supabase"""
    print("\nVerificando configuración de Supabase...")
    
    try:
        from supabase_config import SupabaseConfig
        
        print(f"   URL del proyecto: {SupabaseConfig.PROJECT_URL}")
        print(f"   Host de BD: {SupabaseConfig.DB_HOST}")
        print(f"   Puerto: {SupabaseConfig.DB_PORT}")
        print(f"   Nombre de BD: {SupabaseConfig.DB_NAME}")
        
        if SupabaseConfig.is_configured():
            print("   [OK] Configuración completa")
            
            # Probar construcción de URL
            try:
                db_url = SupabaseConfig.get_database_url()
                print(f"   [OK] URL de conexión generada correctamente")
                # Mostrar URL parcialmente enmascarada
                masked_url = db_url.replace(SupabaseConfig.DB_PASSWORD, "***")
                print(f"   URL: {masked_url}")
                return True
            except Exception as e:
                print(f"   [ERROR] Error generando URL: {e}")
                return False
        else:
            missing = SupabaseConfig.get_missing_vars()
            print(f"   [ERROR] Configuración incompleta: {', '.join(missing)}")
            return False
            
    except ImportError as e:
        print(f"   [ERROR] Error importando configuración: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("Probando configuración de Supabase")
    print("=" * 50)
    
    tests = [
        ("Variables de entorno", test_environment_variables),
        ("Configuración de Supabase", test_supabase_config),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   [ERROR] Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "[PASO]" if result else "[FALLO]"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("\nTodas las pruebas pasaron!")
        print("La configuración de Supabase esta lista para usar")
    else:
        print("\nAlgunas pruebas fallaron")
        print("Revisar la configuración antes de continuar")

if __name__ == '__main__':
    main()
