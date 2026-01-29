#!/usr/bin/env python3
"""
Script de estudio de rendimiento
Mide métricas antes y después de las optimizaciones
"""
import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

BASE_URL = "https://team-time-management.onrender.com"
ADMIN_EMAIL = "admin@teamtime.com"
ADMIN_PASSWORD = "Admin2025!"

def login(session):
    """Login y retornar sesión"""
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30
    )
    return response.status_code == 200

def measure_endpoint(session, method, endpoint, iterations=5):
    """Medir tiempo de respuesta de un endpoint"""
    times = []
    status_codes = []
    response_sizes = []
    
    for i in range(iterations):
        try:
            start = time.time()
            if method == 'GET':
                response = session.get(f"{BASE_URL}{endpoint}", timeout=30)
            elif method == 'POST':
                response = session.post(f"{BASE_URL}{endpoint}", json={}, timeout=30)
            else:
                continue
            
            elapsed = time.time() - start
            times.append(elapsed)
            status_codes.append(response.status_code)
            response_sizes.append(len(response.content))
        except Exception as e:
            print(f"Error en iteración {i+1}: {e}")
    
    if not times:
        return None
    
    return {
        'endpoint': endpoint,
        'method': method,
        'iterations': len(times),
        'avg_time_ms': round(statistics.mean(times) * 1000, 2),
        'min_time_ms': round(min(times) * 1000, 2),
        'max_time_ms': round(max(times) * 1000, 2),
        'median_time_ms': round(statistics.median(times) * 1000, 2),
        'status_codes': status_codes,
        'avg_response_size_bytes': round(statistics.mean(response_sizes), 2)
    }

def main():
    """Función principal"""
    print("🚀 ESTUDIO DE RENDIMIENTO")
    print("=" * 60)
    
    session = requests.Session()
    
    if not login(session):
        print("❌ Error en login")
        return 1
    
    print("✅ Login exitoso\n")
    
    # Endpoints a medir
    year = datetime.now().year
    month = datetime.now().month
    
    endpoints = [
        ('GET', '/api/dashboard'),
        ('GET', f'/api/calendar?year={year}&month={month}'),
        ('GET', f'/api/calendar/annual?year={year}'),
        ('GET', '/api/employees'),
        ('GET', '/api/teams'),
    ]
    
    results = []
    
    for method, endpoint in endpoints:
        print(f"📊 Midiendo {method} {endpoint}...")
        result = measure_endpoint(session, method, endpoint, iterations=5)
        if result:
            results.append(result)
            print(f"   ⏱️  Promedio: {result['avg_time_ms']}ms")
            print(f"   📦 Tamaño respuesta: {result['avg_response_size_bytes']} bytes")
    
    # Generar reporte
    report = {
        'timestamp': datetime.now().isoformat(),
        'base_url': BASE_URL,
        'results': results,
        'summary': {
            'total_endpoints': len(results),
            'avg_response_time_ms': round(statistics.mean([r['avg_time_ms'] for r in results]), 2) if results else 0
        }
    }
    
    # Guardar reporte
    report_file = Path(__file__).parent.parent / 'reports' / f'performance_study_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: {report_file}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
