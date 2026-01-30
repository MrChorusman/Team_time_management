"""
Parser específico para el Boletín Oficial del País Vasco (BOPV)
Extrae festivos locales desde datos abiertos (JSON/CSV) o resoluciones
"""
import requests
import re
import json
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BOPVParser:
    """Parser para festivos locales del BOPV (País Vasco)"""
    
    BOPV_BASE_URL = "https://www.euskadi.eus/bopv"
    DATOS_ABIERTOS_URL = "https://www.euskadi.eus/contenidos/calendario_laboral/calendario_laboral_{year}.json"
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'application/json, text/html, */*'
        })
    
    def load_from_open_data(self, year: int) -> List[Dict]:
        """
        Carga festivos locales desde datos abiertos en formato JSON
        País Vasco publica calendarios en formato JSON/CSV/XML
        """
        local_holidays = []
        
        try:
            # Intentar cargar desde datos abiertos JSON
            json_url = self.DATOS_ABIERTOS_URL.format(year=year)
            response = self.session.get(json_url, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Estructura típica: array de objetos con fecha, municipio, tipo
                    if isinstance(data, list):
                        for item in data:
                            if item.get('tipo') == 'local' or item.get('tipo') == 'municipal':
                                try:
                                    # Parsear fecha
                                    if isinstance(item.get('fecha'), str):
                                        holiday_date = datetime.strptime(item['fecha'], '%Y-%m-%d').date()
                                    else:
                                        continue
                                    
                                    municipality = item.get('municipio') or item.get('municipality') or item.get('nombre')
                                    if not municipality:
                                        continue
                                    
                                    holiday_name = item.get('nombre') or item.get('name') or f'Festivo local de {municipality}'
                                    
                                    local_holidays.append({
                                        'name': holiday_name[:200],
                                        'date': holiday_date.isoformat(),
                                        'city': municipality[:100],
                                        'region': 'País Vasco',
                                        'country': 'España',
                                        'description': item.get('descripcion') or f'Festivo local de {municipality}',
                                        'is_fixed': False
                                    })
                                except (ValueError, KeyError) as e:
                                    logger.warning(f"Error procesando item del JSON: {e}")
                                    continue
                    
                except json.JSONDecodeError:
                    logger.warning(f"No se pudo parsear JSON desde {json_url}")
            
        except Exception as e:
            logger.error(f"Error cargando desde datos abiertos del BOPV: {e}")
        
        return local_holidays
    
    def find_resolution_url(self, year: int) -> Optional[str]:
        """Busca la URL de la resolución de festivos locales para un año"""
        # Las resoluciones se publican típicamente en abril del año anterior
        search_year = year - 1
        
        # Buscar en el BOPV
        search_url = f"{self.BOPV_BASE_URL}/buscar"
        
        search_params = {
            'q': f'calendario fiestas laborales {year}',
            'year': search_year
        }
        
        try:
            response = self.session.get(search_url, params=search_params, timeout=30)
            if response.status_code == 200:
                # Buscar enlaces a decretos/resoluciones
                pattern = r'/bopv/\d{4}/\d+/\d+'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    return f"https://www.euskadi.eus{matches[0]}"
        except Exception as e:
            logger.error(f"Error buscando resolución en BOPV: {e}")
        
        return None
    
    def parse_resolution(self, url: str, year: int) -> List[Dict]:
        """Parsea una resolución del BOPV para extraer festivos locales"""
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
                'urtarrila': 1, 'otsaila': 2, 'martxoa': 3, 'apirila': 4, 'maiatza': 5, 'ekaina': 6,
                'uztaila': 7, 'abuztua': 8, 'iraila': 9, 'urria': 10, 'azaro': 11, 'abendua': 12
            }
            
            # Patrón para municipios y fechas (castellano/euskera)
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
                                'region': 'País Vasco',
                                'country': 'España',
                                'description': f'Festivo local de {municipality}',
                                'is_fixed': False
                            })
                        except ValueError:
                            logger.warning(f"Fecha inválida: {day}/{month}/{year} para {municipality}")
            
        except Exception as e:
            logger.error(f"Error parseando resolución del BOPV: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return local_holidays
    
    def load_local_holidays_for_year(self, year: int) -> List[Dict]:
        """Carga festivos locales del País Vasco para un año específico"""
        logger.info(f"Buscando festivos locales en BOPV para {year}")
        
        # Primero intentar desde datos abiertos (más confiable)
        local_holidays = self.load_from_open_data(year)
        
        if local_holidays:
            logger.info(f"Cargados {len(local_holidays)} festivos desde datos abiertos del BOPV")
            return local_holidays
        
        # Si no hay datos abiertos, intentar desde resolución
        resolution_url = self.find_resolution_url(year)
        
        if resolution_url:
            logger.info(f"Parseando resolución: {resolution_url}")
            return self.parse_resolution(resolution_url, year)
        
        return []
