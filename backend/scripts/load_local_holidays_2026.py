#!/usr/bin/env python3
"""
Script para cargar festivos locales de 2026 desde el BOE y datos abiertos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from services.boe_holiday_service import BOEHolidayService
from models.employee import Employee
from models.user import db
from datetime import datetime

def load_local_holidays_2026():
    """Carga festivos locales de 2026 para ciudades con empleados"""
    
    app = create_app()
    
    with app.app_context():
        print('=' * 70)
        print('🏛️  CARGA DE FESTIVOS LOCALES PARA 2026')
        print('=' * 70)
        print()
        
        boe_service = BOEHolidayService()
        
        # Obtener ciudades con empleados
        cities_with_employees = boe_service.get_cities_with_employees()
        
        print(f'📋 Ciudades con empleados encontradas: {len(cities_with_employees)}')
        if cities_with_employees:
            print('   Ciudades:')
            for city_data in cities_with_employees[:10]:  # Mostrar primeras 10
                print(f'      - {city_data["city"]} ({city_data["region"]}, {city_data["country"]})')
            if len(cities_with_employees) > 10:
                print(f'      ... y {len(cities_with_employees) - 10} más')
        print()
        
        # Cargar festivos locales para 2026
        year = 2026
        print(f'📅 Cargando festivos locales para el año {year}...')
        print()
        
        # Primero intentar desde el BOE
        print('1️⃣ Intentando cargar desde resoluciones del BOE...')
        boe_count, boe_errors = boe_service.load_local_holidays_from_boe_resolutions(year)
        print(f'   ✅ Cargados {boe_count} festivos desde BOE')
        if boe_errors:
            print(f'   ⚠️  Errores: {len(boe_errors)}')
            for error in boe_errors[:3]:
                print(f'      - {error}')
        print()
        
        # Luego intentar carga automática completa
        print('2️⃣ Intentando carga automática desde múltiples fuentes...')
        results = boe_service.load_local_holidays_for_year(year)
        
        print('=' * 70)
        print('✅ RESULTADOS DE LA CARGA')
        print('=' * 70)
        print()
        print(f'📊 Total festivos locales cargados: {results["total_loaded"]}')
        print()
        
        # Detalles por fuente
        print('📋 Detalles por fuente:')
        for source, data in results['sources'].items():
            status = '✅' if data['loaded'] > 0 else '⚠️'
            print(f'   {status} {source}: {data["loaded"]} festivos')
            if data.get('errors'):
                for error in data['errors'][:2]:
                    print(f'      ⚠️  {error}')
        
        if results['errors']:
            print()
            print(f'⚠️  Errores totales: {len(results["errors"])}')
            print('   Primeros 5 errores:')
            for error in results['errors'][:5]:
                print(f'   - {error}')
        
        # Estadísticas finales
        print()
        print('=' * 70)
        print('📊 ESTADÍSTICAS FINALES')
        print('=' * 70)
        print()
        
        from models.holiday import Holiday
        
        # Festivos locales de 2026
        local_holidays_2026 = Holiday.query.filter(
            db.extract('year', Holiday.date) == 2026,
            Holiday.holiday_type == 'local',
            Holiday.active == True
        ).count()
        
        print(f'📅 Festivos locales activos para 2026: {local_holidays_2026}')
        
        # Festivos locales por ciudad
        local_by_city = db.session.query(
            Holiday.city,
            db.func.count(Holiday.id).label('count')
        ).filter(
            db.extract('year', Holiday.date) == 2026,
            Holiday.holiday_type == 'local',
            Holiday.active == True,
            Holiday.city.isnot(None)
        ).group_by(Holiday.city).order_by(db.desc('count')).limit(10).all()
        
        if local_by_city:
            print('   Top 10 ciudades con festivos locales:')
            for city, count in local_by_city:
                print(f'      - {city}: {count} festivos')
        
        print()
        print('✅ Carga completada')
        print()
        print('💡 NOTA: Los festivos locales requieren fuentes específicas.')
        print('   Puedes cargar festivos manualmente usando:')
        print('   - load_local_holidays_from_json_file()')
        print('   - load_local_holidays_from_manual_data()')
        print()

if __name__ == '__main__':
    try:
        load_local_holidays_2026()
    except Exception as e:
        print(f'\n❌ Error durante la carga: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
