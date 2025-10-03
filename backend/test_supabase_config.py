#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la configuración de Supabase
"""

import os
import sys
from dotenv import load_dotenv

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_environment_variables():
    """Probar variables de entorno"""
    print("🔍 Verificando variables de entorno...")
    
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
        print(f"\n⚠️  Variables faltantes: {', '.join(missing_vars)}")
        print("   Crear archivo .env con estas variables antes de continuar")
        return False
    
    print("✅ Todas las variables de entorno están configuradas")
    return True

def test_supabase_config():
    """Probar configuración de Supabase"""
    print("\n🔧 Verificando configuración de Supabase...")
    
    try:
        from supabase_config import SupabaseConfig
        
        print(f"   URL del proyecto: {SupabaseConfig.PROJECT_URL}")
        print(f"   Host de BD: {SupabaseConfig.DB_HOST}")
        print(f"   Puerto: {SupabaseConfig.DB_PORT}")
        print(f"   Nombre de BD: {SupabaseConfig.DB_NAME}")
        
        if SupabaseConfig.is_configured():
            print("   ✅ Configuración completa")
            
            # Probar construcción de URL
            try:
                db_url = SupabaseConfig.get_database_url()
                print(f"   ✅ URL de conexión generada correctamente")
                # Mostrar URL parcialmente enmascarada
                masked_url = db_url.replace(SupabaseConfig.DB_PASSWORD, "***")
                print(f"   📋 URL: {masked_url}")
                return True
            except Exception as e:
                print(f"   ❌ Error generando URL: {e}")
                return False
        else:
            missing = SupabaseConfig.get_missing_vars()
            print(f"   ❌ Configuración incompleta: {', '.join(missing)}")
            return False
            
    except ImportError as e:
        print(f"   ❌ Error importando configuración: {e}")
        return False

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n🔗 Probando conexión a la base de datos...")
    
    try:
        from supabase_config import SupabaseConfig
        from sqlalchemy import create_engine, text
        
        database_url = SupabaseConfig.get_database_url()
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as connection:
            # Ejecutar consulta simple
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   ✅ Conexión exitosa")
            print(f"   📋 Versión PostgreSQL: {version}")
            
            # Probar consulta de información del esquema
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   📋 Base de datos: {db_name}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def test_application_config():
    """Probar configuración de la aplicación"""
    print("\n⚙️  Verificando configuración de la aplicación...")
    
    try:
        from config import Config, SUPABASE_AVAILABLE
        
        print(f"   Supabase disponible: {'✅ Sí' if SUPABASE_AVAILABLE else '❌ No'}")
        print(f"   URL de BD: {Config.SQLALCHEMY_DATABASE_URI[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en configuración: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 Probando configuración de Supabase")
    print("=" * 50)
    
    tests = [
        ("Variables de entorno", test_environment_variables),
        ("Configuración de Supabase", test_supabase_config),
        ("Conexión a base de datos", test_database_connection),
        ("Configuración de aplicación", test_application_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("   La configuración de Supabase está lista para usar")
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar: python migrate_to_supabase.py")
        print("   2. Verificar migración exitosa")
        print("   3. Probar funcionalidad de la aplicación")
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        print("   Revisar la configuración antes de continuar")
        print("\n🔧 Acciones sugeridas:")
        print("   1. Verificar archivo .env")
        print("   2. Comprobar credenciales de Supabase")
        print("   3. Verificar conexión a internet")

if __name__ == '__main__':
    main()
