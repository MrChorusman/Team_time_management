"""
Parser específico para el Diario Oficial de Cataluña (DOGC)
Extrae festivos locales de las órdenes publicadas
"""
import requests
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DOGCParser:
    """Parser para festivos locales del DOGC (Cataluña)"""
    
    DOGC_BASE_URL = "https://dogc.gencat.cat"
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'text/html, application/xhtml+xml, */*'
        })
    
    def find_order_url(self, year: int) -> Optional[str]:
        """
        Busca la URL de la orden de festivos locales para un año
        """
        # Las órdenes se publican típicamente en diciembre del año anterior
        search_year = year - 1
        
        # Buscar en el DOGC
        # Formato: Orden EMT/XXX/YYYY por la que se establece el calendario de fiestas locales
        search_url = f"{self.DOGC_BASE_URL}/ca/buscar"
        
        search_params = {
            'q': f'fiestas locales calendario {year}',
            'year': search_year
        }
        
        try:
            response = self.session.get(search_url, params=search_params, timeout=30)
            if response.status_code == 200:
                # Buscar enlaces a órdenes
                pattern = r'/ca/document-del-dogc/\?documentId=\d+'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    return f"https://dogc.gencat.cat{matches[0]}"
        except Exception as e:
            logger.error(f"Error buscando orden en DOGC: {e}")
        
        return None
    
    def parse_order(self, url: str, year: int) -> List[Dict]:
        """
        Parsea una orden del DOGC para extraer festivos locales
        """
        local_holidays = []
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return local_holidays
            
            # Limpiar HTML
            text = response.text
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            month_names_es = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
                'gener': 1, 'febrer': 2, 'març': 3, 'abril': 4, 'maig': 5, 'juny': 6,
                'juliol': 7, 'agost': 8, 'setembre': 9, 'octubre': 10, 'novembre': 11, 'desembre': 12
            }
            
            # Patrón para municipios y fechas en catalán/castellano
            # Formato puede variar según el DOGC
            municipality_pattern = r'([A-ZÁÉÍÓÚÑÀÈÉÍÒÓÚ][^:]+?):\s*(\d+)\s+de\s+(\w+)[^;]*?;\s*(\d+)\s+de\s+(\w+)'
            
            matches = re.finditer(municipality_pattern, text, re.IGNORECASE)
            
            for match in matches:
                municipality = match.group(1).strip()
                municipality = re.sub(r'\s+', ' ', municipality)
                
                # Parsear ambas fechas
                for day, month_name in [
                    (int(match.group(2)), match.group(3)),
                    (int(match.group(4)), match.group(5))
                ]:
                    month_name_lower = month_name.lower().strip()
                    if month_name_lower in month_names_es:
                        month = month_names_es[month_name_lower]
                        try:
                            holiday_date = date(year, month, day)
                            
                            local_holidays.append({
                                'name': f'Festivo local de {municipality}',
                                'date': holiday_date.isoformat(),
                                'city': municipality,
                                'region': 'Cataluña',
                                'country': 'España',
                                'description': f'Festivo local de {municipality}',
                                'is_fixed': False
                            })
                        except ValueError:
                            logger.warning(f"Fecha inválida: {day}/{month}/{year} para {municipality}")
            
        except Exception as e:
            logger.error(f"Error parseando orden del DOGC: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return local_holidays
    
    def load_local_holidays_for_year(self, year: int) -> List[Dict]:
        """Carga festivos locales de Cataluña para un año específico"""
        logger.info(f"Buscando festivos locales en DOGC para {year}")
        
        order_url = self.find_order_url(year)
        
        if not order_url:
            logger.warning(f"No se encontró orden de festivos locales en DOGC para {year}")
            # URL conocida para 2026 si está disponible
            if year == 2026:
                # Orden EMT/208/2025 publicada el 17-12-2025
                order_url = "https://dogc.gencat.cat/ca/document-del-dogc/?documentId=1032232"
        
        if order_url:
            logger.info(f"Parseando orden: {order_url}")
            return self.parse_order(order_url, year)
        
        return []
