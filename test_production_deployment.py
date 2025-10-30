#!/usr/bin/env python3
"""
Script de pruebas para validar el despliegue en producción
Team Time Management - Pruebas de Producción
"""

import requests
import json
from datetime import datetime
import sys

# URLs de producción
BACKEND_URL = "https://team-time-management.onrender.com"
FRONTEND_URL = "https://team-time-management.vercel.app"
SUPABASE_URL = "https://qsbvoyjqfrhaqncqtknv.supabase.co"

def print_header(text):
    """Imprimir encabezado con formato"""
    print(f"\n{'=' * 80}")
    print(f"{text.center(80)}")
    print(f"{'=' * 80}\n")

def print_test(name, passed, details=""):
    """Imprimir resultado de prueba"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {name}")
    if details:
        print(f"    {details}")

def test_backend_info():
    """Probar endpoint /api/info del backend"""
    print_header("PRUEBA 1: Backend - Endpoint /api/info")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_test("Backend responde correctamente", True)
            print(f"    Nombre: {data.get('name', 'N/A')}")
            print(f"    Versión: {data.get('version', 'N/A')}")
            print(f"    Países soportados: {data.get('supported_countries', 'N/A')}")
            
            # Verificar endpoints disponibles
            endpoints = data.get('api_endpoints', {})
            print(f"\n    Endpoints disponibles:")
            for key, value in endpoints.items():
                print(f"      • {key}: {value}")
            
            return True
        else:
            print_test("Backend responde correctamente", False, 
                      f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Backend responde correctamente", False, str(e))
        return False

def test_backend_health():
    """Probar endpoint /api/health del backend"""
    print_header("PRUEBA 2: Backend - Endpoint /api/health")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_test("Health check exitoso", True)
            print(f"    Status: {data.get('status', 'N/A')}")
            print(f"    Versión: {data.get('version', 'N/A')}")
            print(f"    Ambiente: {data.get('environment', 'N/A')}")
            return True
        else:
            # Si falla el health, intentar ver el error
            try:
                error_data = response.json()
                print_test("Health check exitoso", False, 
                          f"Status: {response.status_code}, Error: {error_data.get('message', 'Unknown')}")
            except:
                print_test("Health check exitoso", False, 
                          f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Health check exitoso", False, str(e))
        return False

def test_frontend():
    """Probar que el frontend está disponible"""
    print_header("PRUEBA 3: Frontend - Vercel")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        
        if response.status_code == 200:
            print_test("Frontend carga correctamente", True)
            print(f"    URL: {FRONTEND_URL}")
            print(f"    Status: {response.status_code}")
            return True
        else:
            print_test("Frontend carga correctamente", False, 
                      f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Frontend carga correctamente", False, str(e))
        return False

def test_cors():
    """Probar configuración de CORS"""
    print_header("PRUEBA 4: Configuración CORS")
    
    try:
        # Simular request desde el frontend
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'GET'
        }
        
        response = requests.get(f"{BACKEND_URL}/api/info", 
                              headers=headers, 
                              timeout=10)
        
        cors_header = response.headers.get('Access-Control-Allow-Origin', '')
        
        if cors_header:
            print_test("CORS configurado", True, f"Origin permitido: {cors_header}")
            return True
        else:
            print_test("CORS configurado", False, "Header CORS no encontrado")
            return False
            
    except Exception as e:
        print_test("CORS configurado", False, str(e))
        return False

def test_database_connection():
    """Probar conexión a base de datos (indirecta)"""
    print_header("PRUEBA 5: Conexión a Base de Datos")
    
    try:
        # Probar endpoint que requiere DB
        response = requests.get(f"{BACKEND_URL}/api/teams", timeout=10)
        
        # Tanto 200 como 401 indican que la DB está conectada
        # (401 = no autenticado, pero el endpoint responde)
        if response.status_code in [200, 401]:
            print_test("Base de datos conectada", True, 
                      "El backend puede acceder a la base de datos")
            return True
        elif response.status_code == 500:
            print_test("Base de datos conectada", False, 
                      "Error 500 - posible problema de conexión a DB")
            return False
        else:
            print_test("Base de datos conectada", False, 
                      f"Status code inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Base de datos conectada", False, str(e))
        return False

def test_google_oauth_config():
    """Probar configuración de Google OAuth"""
    print_header("PRUEBA 6: Configuración Google OAuth")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/auth/google/config", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            is_configured = data.get('configured', False)
            is_mock = data.get('mock_mode', True)
            
            if is_configured and not is_mock:
                print_test("Google OAuth configurado", True, "OAuth configurado con credenciales reales")
                print(f"    Client ID: {data.get('client_id', 'N/A')[:30]}...")
                return True
            elif is_mock:
                print_test("Google OAuth configurado", False, 
                          "⚠️ Modo mock activo - credenciales de producción no configuradas")
                return False
            else:
                print_test("Google OAuth configurado", False, "OAuth no configurado")
                return False
        else:
            print_test("Google OAuth configurado", False, 
                      f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Google OAuth configurado", False, str(e))
        return False

def test_endpoints_availability():
    """Probar disponibilidad de endpoints principales"""
    print_header("PRUEBA 7: Disponibilidad de Endpoints")
    
    endpoints_to_test = [
        ('/api/auth/login', 'POST'),
        ('/api/teams', 'GET'),
        ('/api/employees', 'GET'),
        ('/api/holidays', 'GET'),
    ]
    
    all_passed = True
    
    for endpoint, method in endpoints_to_test:
        try:
            if method == 'GET':
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            elif method == 'POST':
                response = requests.post(f"{BACKEND_URL}{endpoint}", 
                                       json={}, 
                                       timeout=10)
            
            # 200, 400, 401 son válidos (significa que el endpoint responde)
            # 500 indica error en el servidor
            passed = response.status_code != 500
            print_test(f"{method} {endpoint}", passed, 
                      f"Status: {response.status_code}")
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            print_test(f"{method} {endpoint}", False, str(e))
            all_passed = False
    
    return all_passed

def generate_report(results):
    """Generar reporte final"""
    print_header("RESUMEN DE PRUEBAS")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total de pruebas: {total}")
    print(f"Pruebas exitosas: {passed}")
    print(f"Pruebas fallidas: {failed}")
    print(f"Tasa de éxito: {success_rate:.1f}%\n")
    
    if success_rate >= 80:
        print(f"✅ El sistema está mayormente operativo")
    elif success_rate >= 50:
        print(f"⚠️ El sistema tiene problemas que requieren atención")
    else:
        print(f"❌ El sistema tiene problemas críticos")
    
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"{'=' * 80}\n")
    
    return success_rate

def main():
    """Ejecutar todas las pruebas"""
    print_header("TEAM TIME MANAGEMENT - PRUEBAS DE PRODUCCIÓN")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Supabase URL: {SUPABASE_URL}")
    
    results = {}
    
    # Ejecutar pruebas
    results['Backend Info'] = test_backend_info()
    results['Backend Health'] = test_backend_health()
    results['Frontend'] = test_frontend()
    results['CORS'] = test_cors()
    results['Database'] = test_database_connection()
    results['Google OAuth'] = test_google_oauth_config()
    results['Endpoints'] = test_endpoints_availability()
    
    # Generar reporte
    success_rate = generate_report(results)
    
    # Salir con código apropiado
    sys.exit(0 if success_rate >= 80 else 1)

if __name__ == "__main__":
    main()

