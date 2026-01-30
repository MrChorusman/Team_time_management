"""
Parser específico para el Boletín Oficial de Canarias (BOC)
Extrae festivos locales de las órdenes publicadas
"""
import requests
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BOCCanariasParser:
    """Parser para festivos locales del BOC (Canarias)"""
    
    BOC_BASE_URL = "https://www.gobiernodecanarias.org/boc"
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'text/html, application/xhtml+xml, */*'
        })
    
    def find_order_url(self, year: int) -> Optional[str]:
        """Busca la URL de la orden de festivos locales para un año"""
        # Las órdenes se publican típicamente en agosto del año anterior
        search_year = year - 1
        
        # Buscar en el BOC
        # Formato: ORDEN determinando fiestas locales propias de cada municipio
        search_url = f"{self.BOC_BASE_URL}/buscar"
        
        search_params = {
            'q': f'fiestas locales municipios {year}',
            'year': search_year
        }
        
        try:
            response = self.session.get(search_url, params=search_params, timeout=30)
            if response.status_code == 200:
                # Buscar enlaces a órdenes
                pattern = r'/boc/\d{4}/\d+/\d+'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    return f"https://www.gobiernodecanarias.org{matches[0]}"
        except Exception as e:
            logger.error(f"Error buscando orden en BOC Canarias: {e}")
        
        return None
    
    def parse_order(self, url: str, year: int) -> List[Dict]:
        """Parsea una orden del BOC para extraer festivos locales"""
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
                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            
            # Patrón para municipios y fechas
            # Formato típico: "Adeje: 15 de agosto, 8 de septiembre"
            municipality_pattern = r'([A-ZÁÉÍÓÚÑ][^:]+?):\s*(\d+)\s+de\s+(\w+)[^;]*?;\s*(\d+)\s+de\s+(\w+)'
            
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
                                'region': 'Canarias',
                                'country': 'España',
                                'description': f'Festivo local de {municipality}',
                                'is_fixed': False
                            })
                        except ValueError:
                            logger.warning(f"Fecha inválida: {day}/{month}/{year} para {municipality}")
            
        except Exception as e:
            logger.error(f"Error parseando orden del BOC Canarias: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return local_holidays
    
    def load_local_holidays_for_year(self, year: int) -> List[Dict]:
        """Carga festivos locales de Canarias para un año específico"""
        logger.info(f"Buscando festivos locales en BOC Canarias para {year}")
        
        order_url = self.find_order_url(year)
        
        if not order_url and year == 2026:
            # ORDEN de 6 de agosto de 2025 (BOC nº 165 del 21-08-2025, Anuncio 3029)
            # Intentar construir URL conocida si está disponible
            pass
        
        if order_url:
            logger.info(f"Parseando orden: {order_url}")
            return self.parse_order(order_url, year)
        
        return []
