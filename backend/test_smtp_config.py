#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la configuración SMTP
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_smtp_configuration():
    """Prueba la configuración SMTP"""
    print("🔧 PROBANDO CONFIGURACIÓN SMTP")
    print("=" * 50)
    
    # Verificar variables de entorno
    required_vars = [
        'MAIL_SERVER',
        'MAIL_PORT', 
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_USE_TLS'
    ]
    
    print("\n📋 Verificando variables de entorno:")
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if var == 'MAIL_PASSWORD':
                masked_value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
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
    
    print("\n✅ Todas las variables SMTP están configuradas")
    
    # Probar configuración Flask-Mail
    try:
        print("\n🧪 Probando configuración Flask-Mail...")
        
        # Importar después de verificar variables
        from app import create_app
        from services.email_service import EmailService
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            # Inicializar servicio de email
            email_service = EmailService()
            email_service.init_app(app)
            
            # Probar configuración
            result = email_service.test_email_configuration()
            
            if result['success']:
                print(f"✅ {result['message']}")
                return True
            else:
                print(f"❌ {result['error']}")
                return False
                
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def show_smtp_instructions():
    """Muestra instrucciones para configurar SMTP"""
    print("\n📖 INSTRUCCIONES DE CONFIGURACIÓN SMTP")
    print("=" * 50)
    
    print("\n🔧 Para Gmail:")
    print("1. Habilita la verificación en 2 pasos en tu cuenta de Google")
    print("2. Genera una 'Contraseña de aplicación' específica")
    print("3. Configura en tu .env:")
    print("   MAIL_SERVER=smtp.gmail.com")
    print("   MAIL_PORT=587")
    print("   MAIL_USERNAME=tu-email@gmail.com")
    print("   MAIL_PASSWORD=tu-contraseña-de-aplicacion")
    print("   MAIL_USE_TLS=true")
    
    print("\n🔧 Para SendGrid:")
    print("1. Crea una cuenta en SendGrid")
    print("2. Obtén tu API Key desde el dashboard")
    print("3. Configura en tu .env:")
    print("   MAIL_SERVER=smtp.sendgrid.net")
    print("   MAIL_PORT=587")
    print("   MAIL_USERNAME=apikey")
    print("   MAIL_PASSWORD=tu-api-key")
    print("   MAIL_USE_TLS=true")
    
    print("\n🔧 Para Outlook:")
    print("1. Configura en tu .env:")
    print("   MAIL_SERVER=smtp-mail.outlook.com")
    print("   MAIL_PORT=587")
    print("   MAIL_USERNAME=tu-email@outlook.com")
    print("   MAIL_PASSWORD=tu-contraseña")
    print("   MAIL_USE_TLS=true")

def main():
    print("🚀 CONFIGURACIÓN SMTP - TEAM TIME MANAGEMENT")
    print("=" * 60)
    
    # Verificar si existe archivo .env
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print(f"\n⚠️  No se encontró archivo .env en {env_file}")
        print("   Copia el archivo env.example como .env y configura las variables")
        show_smtp_instructions()
        return
    
    # Probar configuración
    if test_smtp_configuration():
        print("\n🎉 ¡Configuración SMTP funcionando correctamente!")
        print("   Los emails se enviarán correctamente desde la aplicación")
    else:
        print("\n❌ La configuración SMTP necesita ajustes")
        show_smtp_instructions()

if __name__ == '__main__':
    main()
