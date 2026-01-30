"""
Parser específico para el Boletín Oficial de Castilla y León (BOCYL)
Extrae festivos locales de las resoluciones publicadas
Nota: Los festivos locales se publican en los BOP de cada provincia
"""
import requests
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BOCYLParser:
    """Parser para festivos locales del BOCYL (Castilla y León)"""
    
    BOCYL_BASE_URL = "https://bocyl.jcyl.es"
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'text/html, application/xhtml+xml, */*'
        })
    
    def find_resolution_url(self, year: int) -> Optional[str]:
        """Busca la URL de la resolución de festivos locales para un año"""
        # Las resoluciones se publican típicamente en mayo/junio del año anterior
        search_year = year - 1
        
        # Buscar en el BOCYL
        # Nota: Los festivos locales se publican en BOP provinciales, pero puede haber resolución general
        search_url = f"{self.BOCYL_BASE_URL}/buscar"
        
        search_params = {
            'q': f'calendario laboral {year}',
            'year': search_year
        }
        
        try:
            response = self.session.get(search_url, params=search_params, timeout=30)
            if response.status_code == 200:
                # Buscar enlaces a decretos/resoluciones
                pattern = r'/bocyl/\d{4}/\d+/\d+'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    return f"https://bocyl.jcyl.es{matches[0]}"
        except Exception as e:
            logger.error(f"Error buscando resolución en BOCYL: {e}")
        
        return None
    
    def parse_resolution(self, url: str, year: int) -> List[Dict]:
        """Parsea una resolución del BOCYL para extraer festivos locales"""
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
                                'region': 'Castilla y León',
                                'country': 'España',
                                'description': f'Festivo local de {municipality}',
                                'is_fixed': False
                            })
                        except ValueError:
                            logger.warning(f"Fecha inválida: {day}/{month}/{year} para {municipality}")
            
        except Exception as e:
            logger.error(f"Error parseando resolución del BOCYL: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return local_holidays
    
    def load_local_holidays_for_year(self, year: int) -> List[Dict]:
        """Carga festivos locales de Castilla y León para un año específico"""
        logger.info(f"Buscando festivos locales en BOCYL para {year}")
        logger.warning("Nota: Los festivos locales de Castilla y León se publican en BOP provinciales")
        
        resolution_url = self.find_resolution_url(year)
        
        if not resolution_url and year == 2026:
            # Decreto 9/2025 (BOCYL nº 106 del 02-06-2025)
            pass
        
        if resolution_url:
            logger.info(f"Parseando resolución: {resolution_url}")
            return self.parse_resolution(resolution_url, year)
        
        return []
