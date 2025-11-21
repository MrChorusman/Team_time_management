#!/usr/bin/env python3
"""
Script para eliminar festivos duplicados de la base de datos.
Prioriza festivos con nombres en español y país en español.
"""

import sys
import os

# Agregar el directorio backend al path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from main import create_app
from models.holiday import Holiday
from models.user import db
from utils.country_mapper import get_country_variants, COUNTRY_MAPPING

def is_spanish_country(country_name):
    """Verifica si un nombre de país está en español"""
    if not country_name:
        return False
    spanish_countries = [v['es'] for v in COUNTRY_MAPPING.values() if v]
    return country_name in spanish_countries

def is_spanish_name(holiday_name):
    """Heurística simple para detectar nombres de festivos en español"""
    if not holiday_name:
        return False
    name_lower = holiday_name.lower()
    spanish_indicators = ['día', 'santos', 'virgen', 'inmaculada', 'navidad', 'año nuevo', 
                          'reyes', 'trabajador', 'constitución', 'inmaculada concepción',
                          'asunción', 'pilar', 'todos los santos', 'difuntos']
    return any(indicator in name_lower for indicator in spanish_indicators)

def deduplicate_holidays(dry_run=True):
    """Elimina festivos duplicados, priorizando español"""
    app = create_app()
    
    with app.app_context():
        # Obtener todos los festivos activos
        all_holidays = Holiday.query.filter(Holiday.active == True).all()
        
        # Agrupar por (fecha, país_normalizado, región, ciudad)
        holidays_by_key = {}
        
        for holiday in all_holidays:
            # Normalizar país
            variants = get_country_variants(holiday.country)
            if variants:
                normalized_country = variants['en']
            else:
                normalized_country = holiday.country
            
            # Crear clave única
            key = (
                str(holiday.date),
                normalized_country,
                holiday.region or '',
                holiday.city or ''
            )
            
            if key not in holidays_by_key:
                holidays_by_key[key] = []
            holidays_by_key[key].append(holiday)
        
        # Identificar duplicados
        duplicates_to_remove = []
        duplicates_info = []
        
        for key, holidays in holidays_by_key.items():
            if len(holidays) > 1:
                # Hay duplicados para esta fecha/ubicación
                date_str, country, region, city = key
                
                # Priorizar: festivos con país en español y nombre en español
                best_holiday = None
                best_score = -1
                
                for holiday in holidays:
                    score = 0
                    # Priorizar país en español
                    if is_spanish_country(holiday.country):
                        score += 10
                    # Priorizar nombre en español
                    if is_spanish_name(holiday.name):
                        score += 5
                    # Priorizar por ID más bajo (más antiguo, probablemente más correcto)
                    score += 1.0 / (holiday.id + 1)
                    
                    if score > best_score:
                        best_score = score
                        best_holiday = holiday
                
                # Marcar los demás para eliminación
                for holiday in holidays:
                    if holiday.id != best_holiday.id:
                        duplicates_to_remove.append(holiday)
                        duplicates_info.append({
                            'remove': {
                                'id': holiday.id,
                                'name': holiday.name,
                                'country': holiday.country,
                                'date': str(holiday.date)
                            },
                            'keep': {
                                'id': best_holiday.id,
                                'name': best_holiday.name,
                                'country': best_holiday.country,
                                'date': str(best_holiday.date)
                            }
                        })
        
        # Mostrar resultados
        print(f"\n{'='*80}")
        print(f"ANÁLISIS DE FESTIVOS DUPLICADOS")
        print(f"{'='*80}\n")
        print(f"Total de festivos activos: {len(all_holidays)}")
        print(f"Grupos con duplicados: {len([k for k, v in holidays_by_key.items() if len(v) > 1])}")
        print(f"Festivos a eliminar: {len(duplicates_to_remove)}\n")
        
        if duplicates_info:
            print("DETALLES DE DUPLICADOS:")
            print("-" * 80)
            for i, info in enumerate(duplicates_info, 1):
                print(f"\n{i}. Fecha: {info['remove']['date']}")
                print(f"   ELIMINAR: ID {info['remove']['id']} - '{info['remove']['name']}' ({info['remove']['country']})")
                print(f"   MANTENER: ID {info['keep']['id']} - '{info['keep']['name']}' ({info['keep']['country']})")
        
        # Ejecutar eliminación si no es dry-run
        if not dry_run and duplicates_to_remove:
            print(f"\n{'='*80}")
            print("ELIMINANDO DUPLICADOS...")
            print(f"{'='*80}\n")
            
            for holiday in duplicates_to_remove:
                print(f"Eliminando festivo ID {holiday.id}: '{holiday.name}' ({holiday.country})")
                db.session.delete(holiday)
            
            db.session.commit()
            print(f"\n✅ Se eliminaron {len(duplicates_to_remove)} festivos duplicados")
        elif duplicates_to_remove:
            print(f"\n{'='*80}")
            print("⚠️  MODO DRY-RUN: No se eliminaron festivos")
            print("Ejecuta con --execute para eliminar los duplicados")
            print(f"{'='*80}\n")
        else:
            print("\n✅ No se encontraron duplicados para eliminar")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Elimina festivos duplicados de la base de datos')
    parser.add_argument('--execute', action='store_true', 
                       help='Ejecutar la eliminación (por defecto es dry-run)')
    
    args = parser.parse_args()
    
    deduplicate_holidays(dry_run=not args.execute)

