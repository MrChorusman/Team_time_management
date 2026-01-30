"""
Servicio unificado para recargar todos los festivos (nacionales, autonómicos y locales)
sin duplicados
"""
from datetime import datetime, date
from typing import Dict, List, Tuple
import logging

from models.holiday import Holiday
from models.user import db
from services.holiday_service import HolidayService
from services.boe_holiday_service import BOEHolidayService
from services.ccaa_boe_service import CCAABOEService

logger = logging.getLogger(__name__)

class UnifiedHolidayService:
    """Servicio unificado para gestionar todos los tipos de festivos"""
    
    def __init__(self):
        self.holiday_service = HolidayService()
        self.boe_service = BOEHolidayService()
    
    def refresh_all_holidays_for_year(self, year: int = None, clean_before_load: bool = True) -> Dict:
        """
        Recarga todos los festivos para un año específico:
        - Nacionales y autonómicos desde Nager.Date API
        - Locales desde BOE y Boletines de CCAA
        
        Args:
            year: Año para el cual recargar festivos
            clean_before_load: Si True, elimina festivos existentes del año antes de cargar nuevos
                              (útil cuando festivos pueden cambiar de tipo entre años)
        
        Evita duplicados usando la lógica de deduplicación mejorada
        """
        if not year:
            year = datetime.now().year
        
        results = {
            'year': year,
            'cleaned': 0,
            'national_regional': {
                'loaded': 0,
                'errors': []
            },
            'local': {
                'loaded': 0,
                'errors': []
            },
            'total_loaded': 0,
            'duplicates_skipped': 0,
            'errors': []
        }
        
        logger.info(f"🔄 Iniciando recarga completa de festivos para {year}")
        
        # Limpiar festivos existentes del año si se solicita
        if clean_before_load:
            logger.info(f"🧹 Limpiando festivos existentes para {year}...")
            try:
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
                
                # Contar festivos que se van a eliminar
                holidays_to_delete = Holiday.query.filter(
                    Holiday.date >= start_date,
                    Holiday.date <= end_date
                ).all()
                
                deleted_count = len(holidays_to_delete)
                
                # Eliminar festivos del año
                Holiday.query.filter(
                    Holiday.date >= start_date,
                    Holiday.date <= end_date
                ).delete(synchronize_session=False)
                
                db.session.commit()
                
                results['cleaned'] = deleted_count
                logger.info(f"✅ Eliminados {deleted_count} festivos existentes para {year}")
                
            except Exception as e:
                error_msg = f"Error limpiando festivos existentes: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                db.session.rollback()
        
        # 1. Cargar festivos nacionales y autonómicos desde Nager.Date
        logger.info(f"📅 Cargando festivos nacionales y autonómicos para {year}...")
        try:
            national_results = self.holiday_service.refresh_holidays_for_year(year)
            results['national_regional']['loaded'] = national_results['total_holidays_loaded']
            results['national_regional']['errors'] = national_results.get('errors', [])
            results['total_loaded'] += national_results['total_holidays_loaded']
            logger.info(f"✅ Cargados {national_results['total_holidays_loaded']} festivos nacionales/autonómicos")
        except Exception as e:
            error_msg = f"Error cargando festivos nacionales/autonómicos: {e}"
            logger.error(error_msg)
            results['national_regional']['errors'].append(error_msg)
            results['errors'].append(error_msg)
        
        # 2. Cargar festivos locales desde BOE
        logger.info(f"🏛️ Cargando festivos locales desde BOE para {year}...")
        try:
            boe_count, boe_errors = self.boe_service.load_local_holidays_from_boe_resolutions(year)
            results['local']['loaded'] = boe_count
            results['local']['errors'] = boe_errors
            results['total_loaded'] += boe_count
            logger.info(f"✅ Cargados {boe_count} festivos locales desde BOE")
        except Exception as e:
            error_msg = f"Error cargando festivos locales desde BOE: {e}"
            logger.error(error_msg)
            results['local']['errors'].append(error_msg)
            results['errors'].append(error_msg)
        
        # 3. Intentar cargar desde Boletines de CCAA
        logger.info(f"🏛️ Buscando festivos locales en Boletines de CCAA para {year}...")
        try:
            ccaa_results = self.ccaa_boe_service.load_local_holidays_from_all_ccaas(year)
            results['ccaa_boe'] = {
                'loaded': ccaa_results['total_loaded'],
                'by_region': ccaa_results['by_region'],
                'errors': ccaa_results['errors']
            }
            results['total_loaded'] += ccaa_results['total_loaded']
            logger.info(f"✅ Cargados {ccaa_results['total_loaded']} festivos locales desde Boletines de CCAA")
        except Exception as e:
            error_msg = f"Error cargando desde Boletines de CCAA: {e}"
            logger.error(error_msg)
            results['ccaa_boe'] = {'loaded': 0, 'errors': [error_msg]}
            results['errors'].append(error_msg)
        
        # 4. Contar duplicados evitados
        # La lógica de deduplicación está en Holiday.bulk_create_holidays
        # que verifica si ya existe antes de crear
        
        logger.info(f"✅ Recarga completada: {results['total_loaded']} festivos cargados")
        
        return results
    
    def get_holiday_statistics(self, year: int = None) -> Dict:
        """Obtiene estadísticas de festivos para un año"""
        if not year:
            year = datetime.now().year
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Contar por tipo
        national = Holiday.query.filter(
            Holiday.date >= start_date,
            Holiday.date <= end_date,
            Holiday.holiday_type == 'national',
            Holiday.active == True
        ).count()
        
        regional = Holiday.query.filter(
            Holiday.date >= start_date,
            Holiday.date <= end_date,
            Holiday.holiday_type == 'regional',
            Holiday.active == True
        ).count()
        
        local = Holiday.query.filter(
            Holiday.date >= start_date,
            Holiday.date <= end_date,
            Holiday.holiday_type == 'local',
            Holiday.active == True
        ).count()
        
        # Contar por país
        by_country = db.session.query(
            Holiday.country,
            db.func.count(Holiday.id).label('count')
        ).filter(
            Holiday.date >= start_date,
            Holiday.date <= end_date,
            Holiday.active == True
        ).group_by(Holiday.country).all()
        
        return {
            'year': year,
            'total': national + regional + local,
            'national': national,
            'regional': regional,
            'local': local,
            'by_country': {country: count for country, count in by_country}
        }
