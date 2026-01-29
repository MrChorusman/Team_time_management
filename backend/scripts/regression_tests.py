#!/usr/bin/env python3
"""
Script de pruebas de regresión automatizadas
Prueba funcionalidades críticas para usuarios admin y empleado
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configuración
BASE_URL = "https://team-time-management.onrender.com"  # URL de producción
# BASE_URL = "http://localhost:5001"  # Para pruebas locales

# Credenciales de usuarios de prueba
ADMIN_EMAIL = "admin@teamtime.com"
ADMIN_PASSWORD = "Admin2025!"
EMPLOYEE_EMAIL = "employee.test@example.com"
EMPLOYEE_PASSWORD = "EmployeeTest123!"

# Contador de queries SQL
query_count = 0
query_times = []

def count_queries():
    """Contador de queries SQL usando SQLAlchemy events"""
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        global query_count
        query_count += 1
        query_times.append(time.time())

class RegressionTestResult:
    """Clase para almacenar resultados de pruebas"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.response_time = 0
        self.status_code = None
        self.query_count = 0
        self.response_size = 0
        self.error_message = None
        self.data = None
    
    def to_dict(self):
        return {
            'test_name': self.test_name,
            'passed': self.passed,
            'response_time_ms': round(self.response_time * 1000, 2),
            'status_code': self.status_code,
            'query_count': self.query_count,
            'response_size_bytes': self.response_size,
            'error_message': self.error_message
        }

def login_user(session: requests.Session, email: str, password: str) -> Tuple[bool, Dict]:
    """Hacer login y retornar si fue exitoso y los datos del usuario"""
    try:
        start_time = time.time()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=30
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, {
                    'user': data.get('user'),
                    'roles': data.get('roles', []),
                    'response_time': response_time
                }
        
        # Obtener mensaje de error si está disponible
        try:
            error_data = response.json()
            error_msg = error_data.get('message', f"Status {response.status_code}")
        except:
            error_msg = f"Status {response.status_code}: {response.text[:200]}"
        
        return False, {'error': f"Login fallido: {error_msg}", 'status_code': response.status_code}
    except Exception as e:
        return False, {'error': str(e)}

def test_endpoint(session: requests.Session, method: str, endpoint: str, 
                  data: Dict = None, expected_status: int = 200) -> RegressionTestResult:
    """Probar un endpoint y capturar métricas"""
    global query_count
    query_count = 0
    
    test_name = f"{method} {endpoint}"
    result = RegressionTestResult(test_name)
    
    try:
        start_time = time.time()
        
        if method == 'GET':
            response = session.get(f"{BASE_URL}{endpoint}", timeout=30)
        elif method == 'POST':
            response = session.post(f"{BASE_URL}{endpoint}", json=data, timeout=30)
        elif method == 'PUT':
            response = session.put(f"{BASE_URL}{endpoint}", json=data, timeout=30)
        elif method == 'DELETE':
            response = session.delete(f"{BASE_URL}{endpoint}", timeout=30)
        else:
            result.error_message = f"Método HTTP no soportado: {method}"
            return result
        
        result.response_time = time.time() - start_time
        result.status_code = response.status_code
        result.response_size = len(response.content)
        result.query_count = query_count  # Nota: esto requiere acceso a la BD, se puede mejorar
        
        if response.status_code == expected_status:
            result.passed = True
            try:
                result.data = response.json()
            except:
                result.data = response.text
        else:
            result.error_message = f"Status code esperado {expected_status}, recibido {response.status_code}"
            try:
                result.data = response.json()
            except:
                result.data = response.text[:500]  # Limitar tamaño
        
    except Exception as e:
        result.error_message = str(e)
    
    return result

def run_admin_tests() -> List[RegressionTestResult]:
    """Ejecutar pruebas para usuario admin"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBAS PARA USUARIO ADMIN")
    print("=" * 60)
    
    session = requests.Session()
    results = []
    
    # Login
    print(f"\n1️⃣ Login como admin...")
    success, login_data = login_user(session, ADMIN_EMAIL, ADMIN_PASSWORD)
    if not success:
        print(f"❌ Login fallido: {login_data.get('error')}")
        return results
    
    print(f"✅ Login exitoso (tiempo: {login_data['response_time']*1000:.2f}ms)")
    results.append(RegressionTestResult("Login Admin"))
    results[-1].passed = True
    results[-1].response_time = login_data['response_time']
    results[-1].status_code = 200
    
    # Dashboard
    print(f"\n2️⃣ Acceso a dashboard...")
    result = test_endpoint(session, 'GET', '/api/dashboard')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Dashboard: {result.response_time*1000:.2f}ms")
    
    # Listar empleados
    print(f"\n3️⃣ Listar empleados...")
    result = test_endpoint(session, 'GET', '/api/employees')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Listar empleados: {result.response_time*1000:.2f}ms")
    
    # Listar equipos
    print(f"\n4️⃣ Listar equipos...")
    result = test_endpoint(session, 'GET', '/api/teams')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Listar equipos: {result.response_time*1000:.2f}ms")
    
    # Calendario mensual (todos los empleados)
    print(f"\n5️⃣ Calendario mensual (todos)...")
    year = datetime.now().year
    month = datetime.now().month
    result = test_endpoint(session, 'GET', f'/api/calendar?year={year}&month={month}')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Calendario mensual: {result.response_time*1000:.2f}ms")
    
    # Calendario anual optimizado
    print(f"\n6️⃣ Calendario anual optimizado...")
    result = test_endpoint(session, 'GET', f'/api/calendar/annual?year={year}')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Calendario anual: {result.response_time*1000:.2f}ms")
    
    # Health check
    print(f"\n7️⃣ Health check...")
    result = test_endpoint(session, 'GET', '/api/health')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Health check: {result.response_time*1000:.2f}ms")
    
    return results

def run_employee_tests() -> List[RegressionTestResult]:
    """Ejecutar pruebas para usuario empleado"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBAS PARA USUARIO EMPLEADO")
    print("=" * 60)
    
    session = requests.Session()
    results = []
    
    # Login
    print(f"\n1️⃣ Login como empleado...")
    success, login_data = login_user(session, EMPLOYEE_EMAIL, EMPLOYEE_PASSWORD)
    if not success:
        print(f"❌ Login fallido: {login_data.get('error')}")
        return results
    
    print(f"✅ Login exitoso (tiempo: {login_data['response_time']*1000:.2f}ms)")
    results.append(RegressionTestResult("Login Employee"))
    results[-1].passed = True
    results[-1].response_time = login_data['response_time']
    results[-1].status_code = 200
    
    # Dashboard personal
    print(f"\n2️⃣ Dashboard personal...")
    result = test_endpoint(session, 'GET', '/api/dashboard')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Dashboard: {result.response_time*1000:.2f}ms")
    
    # Calendario mensual (solo propio)
    print(f"\n3️⃣ Calendario mensual (propio)...")
    year = datetime.now().year
    month = datetime.now().month
    result = test_endpoint(session, 'GET', f'/api/calendar?year={year}&month={month}')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Calendario mensual: {result.response_time*1000:.2f}ms")
    
    # Calendario anual (solo propio)
    print(f"\n4️⃣ Calendario anual (propio)...")
    result = test_endpoint(session, 'GET', f'/api/calendar/annual?year={year}')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Calendario anual: {result.response_time*1000:.2f}ms")
    
    # Notificaciones
    print(f"\n5️⃣ Notificaciones...")
    result = test_endpoint(session, 'GET', '/api/notifications')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Notificaciones: {result.response_time*1000:.2f}ms")
    
    # Perfil personal
    print(f"\n6️⃣ Perfil personal...")
    result = test_endpoint(session, 'GET', '/api/profile')
    results.append(result)
    print(f"{'✅' if result.passed else '❌'} Perfil: {result.response_time*1000:.2f}ms")
    
    return results

def generate_report(results: List[RegressionTestResult], user_type: str):
    """Generar reporte de resultados"""
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    report = {
        'user_type': user_type,
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': round((passed / total * 100), 2) if total > 0 else 0
        },
        'tests': [r.to_dict() for r in results],
        'metrics': {
            'avg_response_time_ms': round(sum(r.response_time * 1000 for r in results) / total, 2) if total > 0 else 0,
            'max_response_time_ms': round(max(r.response_time * 1000 for r in results), 2) if results else 0,
            'min_response_time_ms': round(min(r.response_time * 1000 for r in results), 2) if results else 0
        }
    }
    
    return report

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE REGRESIÓN")
    print("=" * 60)
    print(f"URL Base: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = {}
    
    # Ejecutar pruebas de admin
    admin_results = run_admin_tests()
    all_results['admin'] = generate_report(admin_results, 'admin')
    
    # Ejecutar pruebas de empleado
    employee_results = run_employee_tests()
    all_results['employee'] = generate_report(employee_results, 'employee')
    
    # Generar reporte completo
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    for user_type, report in all_results.items():
        print(f"\n👤 {user_type.upper()}:")
        print(f"   Total: {report['summary']['total_tests']}")
        print(f"   ✅ Pasadas: {report['summary']['passed']}")
        print(f"   ❌ Fallidas: {report['summary']['failed']}")
        print(f"   📈 Tasa de éxito: {report['summary']['success_rate']}%")
        print(f"   ⏱️  Tiempo promedio: {report['metrics']['avg_response_time_ms']}ms")
    
    # Guardar reporte JSON
    report_file = Path(__file__).parent.parent / 'reports' / f'regression_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: {report_file}")
    
    # Determinar si todas las pruebas pasaron
    all_passed = all(r['summary']['failed'] == 0 for r in all_results.values())
    
    if all_passed:
        print("\n✅ TODAS LAS PRUEBAS PASARON")
        return 0
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        return 1

if __name__ == '__main__':
    sys.exit(main())
