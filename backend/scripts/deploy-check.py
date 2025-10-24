#!/usr/bin/env python3
"""
Script de verificación de seguridad para despliegues
Verifica que no se despliegue configuración de desarrollo en producción
"""

import os
import sys
from dotenv import load_dotenv

def check_production_safety():
    """Verificar que la configuración sea segura para producción"""
    print("🔒 VERIFICACIÓN DE SEGURIDAD PARA DESPLIEGUE")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    errors = []
    warnings = []
    
    # Verificar entorno
    flask_env = os.environ.get('FLASK_ENV', '')
    if flask_env == 'development':
        errors.append("❌ FLASK_ENV=development en producción")
    elif flask_env != 'production':
        warnings.append(f"⚠️  FLASK_ENV={flask_env} (esperado: production)")
    
    # Verificar debug
    debug = os.environ.get('DEBUG', '').lower()
    if debug in ['true', '1', 'yes']:
        errors.append("❌ DEBUG habilitado en producción")
    
    # Verificar configuración de Supabase
    supabase_url = os.environ.get('SUPABASE_URL', '')
    if 'dev' in supabase_url.lower() or '[proyecto-dev]' in supabase_url.lower():
        errors.append("❌ URL de Supabase de desarrollo detectada")
    
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    if '[anon-key-dev]' in supabase_key.lower():
        errors.append("❌ Clave de Supabase de desarrollo detectada")
    
    # Verificar secretos
    secret_key = os.environ.get('SECRET_KEY', '')
    if 'dev-secret' in secret_key.lower():
        errors.append("❌ SECRET_KEY de desarrollo detectada")
    
    # Verificar configuración de email
    mail_username = os.environ.get('MAIL_USERNAME', '')
    if not mail_username or '@' not in mail_username:
        warnings.append("⚠️  MAIL_USERNAME no configurado correctamente")
    
    # Mostrar resultados
    if errors:
        print("🚨 ERRORES CRÍTICOS:")
        for error in errors:
            print(f"   {error}")
        print("\n❌ DESPLIEGUE BLOQUEADO - Corrige los errores antes de continuar")
        return False
    
    if warnings:
        print("⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"   {warning}")
        print("\n✅ Despliegue permitido, pero revisa las advertencias")
    else:
        print("✅ CONFIGURACIÓN CORRECTA PARA PRODUCCIÓN")
        print("   • Entorno: production")
        print("   • Debug: deshabilitado")
        print("   • Supabase: configuración de producción")
        print("   • Secretos: configuración de producción")
    
    return True

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("🔒 VERIFICADOR DE SEGURIDAD PARA DESPLIEGUES")
        print("=" * 50)
        print("Este script verifica que la configuración sea segura para producción")
        print("\nUso:")
        print("  python deploy-check.py")
        print("\nEl script verifica:")
        print("  • FLASK_ENV=production")
        print("  • DEBUG deshabilitado")
        print("  • Configuración de Supabase de producción")
        print("  • Secretos de producción")
        return
    
    success = check_production_safety()
    
    if not success:
        sys.exit(1)
    
    print("\n🚀 LISTO PARA DESPLIEGUE")

if __name__ == "__main__":
    main()
