#!/usr/bin/env python3
"""
Script para verificar la configuración de Google OAuth
"""

import os
import sys
from dotenv import load_dotenv

def check_google_oauth_config():
    """Verifica la configuración de Google OAuth"""
    
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN GOOGLE OAUTH")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar entorno
    flask_env = os.environ.get('FLASK_ENV', 'development')
    print(f"🌍 Entorno: {flask_env.upper()}")
    
    # Verificar variables de backend
    print("\n📋 BACKEND:")
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    google_redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    
    print(f"   GOOGLE_CLIENT_ID: {'✅ Configurado' if google_client_id else '❌ No configurado'}")
    print(f"   GOOGLE_CLIENT_SECRET: {'✅ Configurado' if google_client_secret else '❌ No configurado'}")
    print(f"   GOOGLE_REDIRECT_URI: {'✅ Configurado' if google_redirect_uri else '❌ No configurado'}")
    
    # Verificar variables de frontend
    print("\n📋 FRONTEND:")
    vite_google_client_id = os.environ.get('VITE_GOOGLE_CLIENT_ID')
    print(f"   VITE_GOOGLE_CLIENT_ID: {'✅ Configurado' if vite_google_client_id else '❌ No configurado'}")
    
    # Determinar modo
    print("\n🎯 MODO DE FUNCIONAMIENTO:")
    
    if flask_env == 'production':
        if google_client_id and google_client_secret and vite_google_client_id:
            print("   ✅ PRODUCCIÓN: Google OAuth real activado")
            print("   📝 Botón mostrará: 'Continuar con Google'")
        else:
            print("   ❌ PRODUCCIÓN: Google OAuth no configurado")
            print("   📝 Botón NO aparecerá (error de configuración)")
    else:
        if google_client_id and google_client_secret and vite_google_client_id:
            print("   ✅ DESARROLLO: Google OAuth real activado")
            print("   📝 Botón mostrará: 'Continuar con Google'")
        else:
            print("   🔧 DESARROLLO: Modo mock activado")
            print("   📝 Botón mostrará: 'Continuar con Google (Demo)'")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    
    if flask_env == 'production':
        if not (google_client_id and google_client_secret and vite_google_client_id):
            print("   ⚠️  Configurar credenciales de Google para producción")
            print("   📋 Crear proyecto en Google Cloud Console")
            print("   🔑 Configurar variables de entorno en Render")
        else:
            print("   ✅ Configuración de producción completa")
    else:
        if not (google_client_id and google_client_secret and vite_google_client_id):
            print("   ✅ Modo mock es perfecto para desarrollo")
            print("   🚀 Para activar Google real, configurar credenciales")
        else:
            print("   ✅ Google OAuth real configurado para desarrollo")
    
    print("\n🎉 Verificación completada")

if __name__ == "__main__":
    check_google_oauth_config()
