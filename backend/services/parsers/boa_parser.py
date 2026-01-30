"""
Parser específico para el Boletín Oficial de Aragón (BOA)
Extrae festivos locales de las resoluciones publicadas
"""
import requests
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BOAParser:
    """Parser para festivos locales del BOA (Aragón)"""
    
    BOA_BASE_URL = "https://www.boa.aragon.es"
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'text/html, application/xhtml+xml, */*'
        })
    
    def find_resolution_url(self, year: int) -> Optional[str]:
        """Busca la URL de la resolución de festivos locales para un año"""
        # Las resoluciones se publican típicamente en noviembre del año anterior
        search_year = year - 1
        
        # Buscar en el BOA
        # Formato: Resolución del Director General de Trabajo determinando fiestas laborales
        search_url = f"{self.BOA_BASE_URL}/buscar"
        
        search_params = {
            'q': f'fiestas laborales municipios {year}',
            'year': search_year
        }
        
        try:
            response = self.session.get(search_url, params=search_params, timeout=30)
            if response.status_code == 200:
                # Buscar enlaces a resoluciones
                pattern = r'/EBOA/BRSCGI\?CMD=VEROBJ&MLKOB=\d+'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    return f"https://www.boa.aragon.es{matches[0]}"
        except Exception as e:
            logger.error(f"Error buscando resolución en BOA: {e}")
        
        return None
    
    def parse_resolution(self, url: str, year: int) -> List[Dict]:
        """Parsea una resolución del BOA para extraer festivos locales"""
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
            # Formato típico: "Abiego: 30 de abril, 14 de agosto"
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
                                'region': 'Aragón',
                                'country': 'España',
                                'description': f'Festivo local de {municipality}',
                                'is_fixed': False
                            })
                        except ValueError:
                            logger.warning(f"Fecha inválida: {day}/{month}/{year} para {municipality}")
            
        except Exception as e:
            logger.error(f"Error parseando resolución del BOA: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return local_holidays
    
    def load_local_holidays_for_year(self, year: int) -> List[Dict]:
        """Carga festivos locales de Aragón para un año específico"""
        logger.info(f"Buscando festivos locales en BOA para {year}")
        
        resolution_url = self.find_resolution_url(year)
        
        if not resolution_url and year == 2026:
            # URL conocida para 2026: Resolución de 4 de noviembre de 2025 (BOA nº 225 del 20-11-2025)
            resolution_url = "https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1421874360606&type=pdf"
        
        if resolution_url:
            logger.info(f"Parseando resolución: {resolution_url}")
            return self.parse_resolution(resolution_url, year)
        
        return []
