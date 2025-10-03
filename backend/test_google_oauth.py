#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la configuración de Google OAuth
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_google_oauth_configuration():
    """Prueba la configuración de Google OAuth"""
    print("🔐 PROBANDO CONFIGURACIÓN GOOGLE OAUTH")
    print("=" * 50)
    
    # Verificar variables de entorno
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'GOOGLE_REDIRECT_URI'
    ]
    
    print("\n📋 Verificando variables de entorno:")
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if 'SECRET' in var:
                masked_value = value[:8] + "*" * (len(value) - 8) if len(value) > 8 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: NO CONFIGURADO")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Variables faltantes: {', '.join(missing_vars)}")
        print("   Configura estas variables en tu archivo .env antes de continuar")
        return False
    
    print("\n✅ Todas las variables de Google OAuth están configuradas")
    
    # Probar configuración del servicio
    try:
        print("\n🧪 Probando configuración del servicio...")
        
        # Importar después de verificar variables
        from services.google_oauth_service import GoogleOAuthService
        from app import create_app
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            # Inicializar servicio de Google OAuth
            google_oauth = GoogleOAuthService()
            google_oauth.init_app(app)
            
            if google_oauth.is_configured():
                print("✅ Google OAuth configurado correctamente")
                
                # Probar generación de URL (sin ejecutar)
                try:
                    auth_url = google_oauth.get_auth_url()
                    print(f"✅ URL de autorización generada: {auth_url[:50]}...")
                    return True
                except Exception as e:
                    print(f"❌ Error generando URL de autorización: {e}")
                    return False
            else:
                print("❌ Google OAuth no está configurado correctamente")
                return False
                
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def show_google_oauth_instructions():
    """Muestra instrucciones para configurar Google OAuth"""
    print("\n📖 INSTRUCCIONES DE CONFIGURACIÓN GOOGLE OAUTH")
    print("=" * 60)
    
    print("\n🔧 Pasos para configurar Google OAuth:")
    print("\n1️⃣ Crear proyecto en Google Cloud Console:")
    print("   • Ve a https://console.cloud.google.com/")
    print("   • Crea un nuevo proyecto o selecciona uno existente")
    print("   • Habilita la API de Google+ (o Google Identity)")
    
    print("\n2️⃣ Configurar OAuth 2.0:")
    print("   • Ve a 'Credenciales' en el menú lateral")
    print("   • Haz clic en 'Crear credenciales' → 'ID de cliente OAuth 2.0'")
    print("   • Selecciona 'Aplicación web' como tipo")
    print("   • Agrega URIs de redirección autorizados:")
    print("     - http://localhost:3000/auth/google/callback (desarrollo)")
    print("     - https://tu-dominio.com/auth/google/callback (producción)")
    
    print("\n3️⃣ Configurar variables de entorno:")
    print("   • Copia el Client ID y Client Secret")
    print("   • Agrega al archivo .env:")
    print("     GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com")
    print("     GOOGLE_CLIENT_SECRET=tu-client-secret")
    print("     GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback")
    
    print("\n4️⃣ Configurar pantalla de consentimiento:")
    print("   • Ve a 'Pantalla de consentimiento OAuth'")
    print("   • Completa la información requerida")
    print("   • Agrega usuarios de prueba (para desarrollo)")
    
    print("\n🔧 URLs de ejemplo para configuración:")
    print("   • Desarrollo: http://localhost:3000/auth/google/callback")
    print("   • Producción: https://tu-dominio.com/auth/google/callback")
    
    print("\n⚠️  Notas importantes:")
    print("   • El Client Secret debe mantenerse privado")
    print("   • Las URIs de redirección deben coincidir exactamente")
    print("   • Para producción, configura el dominio verificado")
    print("   • Revisa los límites de cuota de la API")

def show_endpoints_info():
    """Muestra información sobre los endpoints disponibles"""
    print("\n🌐 ENDPOINTS DE GOOGLE OAUTH DISPONIBLES")
    print("=" * 50)
    
    print("\n📋 Endpoints implementados:")
    print("   • GET  /api/auth/google/url      - Obtener URL de autorización")
    print("   • GET  /api/auth/google/callback - Manejar callback de Google")
    print("   • GET  /api/auth/google/config   - Verificar configuración")
    print("   • POST /api/auth/google/disconnect - Desconectar cuenta")
    
    print("\n🔄 Flujo de autenticación:")
    print("   1. Frontend solicita URL de autorización")
    print("   2. Usuario es redirigido a Google")
    print("   3. Usuario autoriza la aplicación")
    print("   4. Google redirige al callback con código")
    print("   5. Backend intercambia código por token")
    print("   6. Se obtiene información del usuario")
    print("   7. Se crea/inicia sesión del usuario")

def main():
    print("🚀 CONFIGURACIÓN GOOGLE OAUTH - TEAM TIME MANAGEMENT")
    print("=" * 70)
    
    # Verificar si existe archivo .env
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print(f"\n⚠️  No se encontró archivo .env en {env_file}")
        print("   Copia el archivo env.example como .env y configura las variables")
        show_google_oauth_instructions()
        return
    
    # Probar configuración
    if test_google_oauth_configuration():
        print("\n🎉 ¡Configuración Google OAuth funcionando correctamente!")
        print("   Los usuarios pueden autenticarse con Google")
        show_endpoints_info()
    else:
        print("\n❌ La configuración Google OAuth necesita ajustes")
        show_google_oauth_instructions()

if __name__ == '__main__':
    main()
