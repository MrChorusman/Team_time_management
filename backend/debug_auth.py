#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas de autenticación
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_auth_system():
    """Diagnosticar el sistema de autenticación paso a paso"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 60)
    
    try:
        # 1. Verificar configuración de base de datos
        print("\n1️⃣ VERIFICANDO CONFIGURACIÓN DE BASE DE DATOS...")
        from config import Config
        print(f"   DATABASE_URL: {Config.SQLALCHEMY_DATABASE_URI}")
        print(f"   SUPABASE_URL: {Config.SUPABASE_URL}")
        print(f"   SUPABASE_KEY configurado: {'Sí' if Config.SUPABASE_KEY else 'No'}")
        
        # 2. Verificar conexión a base de datos
        print("\n2️⃣ VERIFICANDO CONEXIÓN A BASE DE DATOS...")
        import psycopg2
        
        # Extraer credenciales de la URL
        db_url = Config.SQLALCHEMY_DATABASE_URI
        if 'postgresql://' in db_url:
            # Parsear URL de PostgreSQL
            parts = db_url.replace('postgresql://', '').split('@')
            if len(parts) == 2:
                user_pass = parts[0].split(':')
                host_db = parts[1].split('/')
                if len(host_db) == 2:
                    host_port = host_db[0].split(':')
                    
                    user = user_pass[0]
                    password = user_pass[1]
                    host = host_port[0]
                    port = int(host_port[1]) if len(host_port) > 1 else 5432
                    database = host_db[1]
                    
                    print(f"   Host: {host}")
                    print(f"   Port: {port}")
                    print(f"   Database: {database}")
                    print(f"   User: {user}")
                    
                    # Probar conexión
                    try:
                        conn = psycopg2.connect(
                            host=host,
                            port=port,
                            database=database,
                            user=user,
                            password=password
                        )
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        print(f"   ✅ Conexión exitosa: {result}")
                    except Exception as e:
                        print(f"   ❌ Error de conexión: {e}")
                        return False
        
        # 3. Verificar modelos
        print("\n3️⃣ VERIFICANDO MODELOS...")
        try:
            from models.user import User, Role, db
            print("   ✅ Modelos importados correctamente")
            
            # Verificar si las tablas existen
            from sqlalchemy import inspect
            app = None
            try:
                import app as app_module
                app = app_module.create_app()
            except:
                print("   ⚠️ No se pudo crear la aplicación Flask")
            
            if app:
                with app.app_context():
                    inspector = inspect(db.engine)
                    tables = inspector.get_table_names()
                    print(f"   📊 Tablas encontradas: {tables}")
                    
                    # Verificar tabla user
                    if 'user' in tables:
                        print("   ✅ Tabla 'user' existe")
                        user_count = User.query.count()
                        print(f"   📊 Usuarios en BD: {user_count}")
                        
                        # Verificar usuario de prueba
                        test_user = User.query.filter_by(email='test@test.com').first()
                        if test_user:
                            print(f"   ✅ Usuario de prueba encontrado: {test_user.email}")
                            print(f"   📋 Activo: {test_user.active}")
                            print(f"   📋 Confirmado: {test_user.confirmed_at is not None}")
                        else:
                            print("   ❌ Usuario de prueba no encontrado")
                    else:
                        print("   ❌ Tabla 'user' no existe")
                        
                    # Verificar tabla role
                    if 'role' in tables:
                        print("   ✅ Tabla 'role' existe")
                        role_count = Role.query.count()
                        print(f"   📊 Roles en BD: {role_count}")
                    else:
                        print("   ❌ Tabla 'role' no existe")
        
        except Exception as e:
            print(f"   ❌ Error con modelos: {e}")
            traceback.print_exc()
            return False
        
        # 4. Verificar Flask-Security
        print("\n4️⃣ VERIFICANDO FLASK-SECURITY...")
        try:
            from flask_security import Security
            from flask_security.utils import verify_password, hash_password
            print("   ✅ Flask-Security importado correctamente")
            
            # Probar funciones de hash
            test_password = "123456"
            hashed = hash_password(test_password)
            print(f"   ✅ Hash generado: {hashed[:50]}...")
            
            verified = verify_password(test_password, hashed)
            print(f"   ✅ Verificación de hash: {verified}")
            
        except Exception as e:
            print(f"   ❌ Error con Flask-Security: {e}")
            traceback.print_exc()
            return False
        
        # 5. Verificar endpoints de autenticación
        print("\n5️⃣ VERIFICANDO ENDPOINTS DE AUTENTICACIÓN...")
        try:
            from app.auth import auth_bp
            print("   ✅ Blueprint de autenticación importado")
            
            # Verificar rutas
            routes = []
            for rule in auth_bp.url_map.iter_rules():
                routes.append(f"{rule.methods} {rule.rule}")
            print(f"   📋 Rutas disponibles: {routes}")
            
        except Exception as e:
            print(f"   ❌ Error con endpoints: {e}")
            traceback.print_exc()
            return False
        
        print("\n✅ DIAGNÓSTICO COMPLETADO")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN DIAGNÓSTICO: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_auth_system()



