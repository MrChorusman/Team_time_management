#!/usr/bin/env python3
"""
Script de verificación pre-despliegue para Google OAuth
Verifica que la configuración esté lista para producción
"""

import os
import sys
import requests
from dotenv import load_dotenv

def check_production_readiness():
    """Verifica que la configuración esté lista para producción"""
    
    print("🚀 VERIFICACIÓN PRE-DESPLIEGUE - GOOGLE OAUTH")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar entorno
    flask_env = os.environ.get('FLASK_ENV', 'development')
    print(f"🌍 Entorno detectado: {flask_env.upper()}")
    
    # Variables requeridas
    required_vars = {
        'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'VITE_GOOGLE_CLIENT_ID': os.environ.get('VITE_GOOGLE_CLIENT_ID')
    }
    
    print("\n📋 VERIFICACIÓN DE VARIABLES:")
    all_configured = True
    
    for var_name, var_value in required_vars.items():
        if var_value and var_value != 'your-google-client-id-here':
            print(f"   ✅ {var_name}: Configurado")
        else:
            print(f"   ❌ {var_name}: No configurado")
            all_configured = False
    
    # Verificar formato de Google Client ID
    google_client_id = required_vars['GOOGLE_CLIENT_ID']
    if google_client_id and google_client_id != 'your-google-client-id-here':
        if '.apps.googleusercontent.com' in google_client_id:
            print(f"   ✅ Formato de Client ID: Correcto")
        else:
            print(f"   ⚠️  Formato de Client ID: Verificar (.apps.googleusercontent.com)")
    
    # Verificar formato de Google Client Secret
    google_client_secret = required_vars['GOOGLE_CLIENT_SECRET']
    if google_client_secret and google_client_secret != 'your-google-client-secret-here':
        if google_client_secret.startswith('GOCSPX-'):
            print(f"   ✅ Formato de Client Secret: Correcto")
        else:
            print(f"   ⚠️  Formato de Client Secret: Verificar (debe empezar con GOCSPX-)")
    
    # Verificar URIs de redirección
    print("\n🔗 VERIFICACIÓN DE URIs DE REDIRECCIÓN:")
    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    if redirect_uri:
        print(f"   ✅ GOOGLE_REDIRECT_URI: {redirect_uri}")
        
        # Verificar que sea HTTPS en producción
        if flask_env == 'production' and not redirect_uri.startswith('https://'):
            print(f"   ⚠️  ADVERTENCIA: URI debe ser HTTPS en producción")
    else:
        print(f"   ❌ GOOGLE_REDIRECT_URI: No configurado")
        all_configured = False
    
    # Verificar conectividad con Google
    print("\n🌐 VERIFICACIÓN DE CONECTIVIDAD:")
    try:
        response = requests.get('https://accounts.google.com', timeout=5)
        if response.status_code == 200:
            print("   ✅ Conectividad con Google: OK")
        else:
            print(f"   ⚠️  Conectividad con Google: Status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Conectividad con Google: Error - {e}")
    
    # Resultado final
    print("\n🎯 RESULTADO DE LA VERIFICACIÓN:")
    
    if flask_env == 'production':
        if all_configured:
            print("   ✅ LISTO PARA PRODUCCIÓN")
            print("   📝 El botón mostrará: 'Continuar con Google'")
            print("   🚀 Google OAuth real estará activo")
        else:
            print("   ❌ NO LISTO PARA PRODUCCIÓN")
            print("   📝 Configurar variables faltantes")
            print("   ⚠️  El botón NO aparecerá o mostrará error")
    else:
        if all_configured:
            print("   ✅ DESARROLLO CON GOOGLE REAL")
            print("   📝 El botón mostrará: 'Continuar con Google'")
            print("   🔧 Google OAuth real estará activo en desarrollo")
        else:
            print("   🔧 DESARROLLO CON MODO MOCK")
            print("   📝 El botón mostrará: 'Continuar con Google (Demo)'")
            print("   ✅ Modo mock es perfecto para desarrollo")
    
    # Recomendaciones específicas
    print("\n💡 RECOMENDACIONES:")
    
    if flask_env == 'production' and not all_configured:
        print("   🚨 CRÍTICO: Configurar Google OAuth antes del despliegue")
        print("   📋 Pasos requeridos:")
        print("      1. Crear proyecto en Google Cloud Console")
        print("      2. Configurar OAuth 2.0 credentials")
        print("      3. Agregar URIs de redirección autorizadas")
        print("      4. Configurar variables en Render.com")
    elif flask_env == 'production' and all_configured:
        print("   ✅ Configuración completa para producción")
        print("   🚀 Listo para despliegue")
    else:
        print("   ✅ Configuración adecuada para desarrollo")
        print("   🔧 Modo mock funcionando correctamente")
    
    print("\n🎉 Verificación completada")
    
    # Código de salida
    if flask_env == 'production' and not all_configured:
        return 1  # Error: no listo para producción
    else:
        return 0  # OK

if __name__ == "__main__":
    exit_code = check_production_readiness()
    sys.exit(exit_code)
