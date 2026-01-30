#!/usr/bin/env python3
"""
Script para cargar festivos de 2026 (nacionales, autonómicos y locales)
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from services.holiday_service import HolidayService
from models.employee import Employee
from models.user import db
from datetime import datetime

def load_holidays_2026():
    """Carga festivos de 2026 para todos los países con empleados"""
    
    app = create_app()
    
    with app.app_context():
        print('=' * 70)
        print('🎉 CARGA DE FESTIVOS PARA 2026')
        print('=' * 70)
        print()
        
        holiday_service = HolidayService()
        
        # Obtener países únicos de empleados
        countries_in_use = db.session.query(Employee.country).distinct().all()
        countries_in_use = [country[0] for country in countries_in_use if country[0]]
        
        print(f'📋 Países encontrados con empleados: {countries_in_use}')
        print()
        
        # Cargar festivos para 2026
        year = 2026
        print(f'📅 Cargando festivos para el año {year}...')
        print()
        
        results = holiday_service.refresh_holidays_for_year(year)
        
        print('=' * 70)
        print('✅ RESULTADOS DE LA CARGA')
        print('=' * 70)
        print()
        print(f'📊 Total festivos cargados: {results["total_holidays_loaded"]}')
        print(f'🌍 Países procesados: {len(results["processed_countries"])}')
        print()
        
        # Detalles por país
        print('📋 Detalles por país:')
        for country_result in results['processed_countries']:
            status = '✅' if country_result['holidays_loaded'] > 0 else '⚠️'
            print(f'   {status} {country_result["country"]}: {country_result["holidays_loaded"]} festivos')
            if country_result.get('errors'):
                for error in country_result['errors'][:3]:
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
        
        summary = holiday_service.get_holidays_summary()
        print(f'📈 Total festivos en base de datos: {summary["total_holidays"]}')
        print(f'🌍 Países con festivos: {summary["countries_with_holidays"]}')
        print(f'🎯 Tipos de festivos:')
        for type_stat in summary['type_stats']:
            print(f'   - {type_stat["type"]}: {type_stat["count"]}')
        
        # Verificar festivos de 2026 específicamente
        from models.holiday import Holiday
        holidays_2026 = Holiday.query.filter(
            db.extract('year', Holiday.date) == 2026,
            Holiday.active == True
        ).count()
        
        print()
        print(f'📅 Festivos activos para 2026: {holidays_2026}')
        
        # Desglose por tipo para 2026
        holidays_by_type_2026 = db.session.query(
            Holiday.holiday_type,
            db.func.count(Holiday.id).label('count')
        ).filter(
            db.extract('year', Holiday.date) == 2026,
            Holiday.active == True
        ).group_by(Holiday.holiday_type).all()
        
        if holidays_by_type_2026:
            print('   Desglose por tipo:')
            for holiday_type, count in holidays_by_type_2026:
                print(f'      - {holiday_type}: {count}')
        
        print()
        print('✅ Carga completada exitosamente')
        print()

if __name__ == '__main__':
    try:
        load_holidays_2026()
    except Exception as e:
        print(f'\n❌ Error durante la carga: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
