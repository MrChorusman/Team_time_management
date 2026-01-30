"""
Parser específico para el Diario Oficial de Galicia (DOG)
Extrae festivos locales de las resoluciones publicadas
"""
import requests
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DOGParser:
    """Parser para festivos locales del DOG (Galicia)"""
    
    # URL base del DOG
    DOG_BASE_URL = "https://www.xunta.gal/dog"
    
    # Patrón para buscar resoluciones de festivos locales
    # Formato típico: "RESOLUCIÓN de [fecha], por la que se da publicidad a las fiestas laborales de carácter local"
    RESOLUTION_PATTERN = r'RESOLUCIÓN.*?fiestas.*?laborales.*?carácter.*?local.*?(\d{4})'
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'text/html, application/xhtml+xml, */*'
        })
    
    def find_resolution_url(self, year: int) -> Optional[str]:
        """
        Busca la URL de la resolución de festivos locales para un año
        """
        # Buscar en el DOG resoluciones publicadas en octubre/noviembre del año anterior
        # Las resoluciones de festivos locales se publican típicamente en octubre
        search_year = year - 1
        
        # URL de búsqueda del DOG
        search_url = f"{self.DOG_BASE_URL}/buscar"
        
        # Buscar resoluciones de festivos locales
        search_params = {
            'q': f'fiestas laborales carácter local {year}',
            'year': search_year,
            'month': '10'  # Octubre
        }
        
        try:
            response = self.session.get(search_url, params=search_params, timeout=30)
            if response.status_code == 200:
                # Buscar enlaces a resoluciones
                # El DOG tiene un formato específico de URLs
                # Ejemplo: /dog/Publicados/2025/20251030/AnuncioG0767-221025-0001_es.html
                pattern = r'/dog/Publicados/\d{4}/\d{8}/Anuncio[^"]*\.html'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    # Filtrar por resoluciones de festivos locales
                    for match in matches:
                        full_url = f"https://www.xunta.gal{match}"
                        # Verificar que sea la resolución correcta
                        if self._is_local_holidays_resolution(full_url, year):
                            return full_url
        except Exception as e:
            logger.error(f"Error buscando resolución en DOG: {e}")
        
        return None
    
    def _is_local_holidays_resolution(self, url: str, year: int) -> bool:
        """Verifica si una URL es la resolución de festivos locales"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                text = response.text.lower()
                # Buscar indicadores de que es la resolución correcta
                indicators = [
                    'fiestas laborales',
                    'carácter local',
                    f'año {year}',
                    'ayuntamientos',
                    'provincias'
                ]
                matches = sum(1 for indicator in indicators if indicator in text)
                return matches >= 3
        except:
            pass
        return False
    
    def parse_resolution(self, url: str, year: int) -> List[Dict]:
        """
        Parsea una resolución del DOG para extraer festivos locales
        Formato real del DOG: "30. Coruña, A: 17 de febrero, Martes de Carnaval; 7 de octubre, festividad del Rosario."
        """
        local_holidays = []
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return local_holidays
            
            # Limpiar HTML básico antes de parsear
            text = response.text
            # Remover etiquetas HTML pero mantener el texto
            text = re.sub(r'<[^>]+>', ' ', text)
            # Normalizar espacios
            text = re.sub(r'\s+', ' ', text)
            # Remover caracteres especiales HTML
            text = text.replace('&nbsp;', ' ').replace('&aacute;', 'á').replace('&eacute;', 'é')
            text = text.replace('&iacute;', 'í').replace('&oacute;', 'ó').replace('&uacute;', 'ú')
            text = text.replace('&ntilde;', 'ñ').replace('&Aacute;', 'Á').replace('&Eacute;', 'É')
            text = text.replace('&Iacute;', 'Í').replace('&Oacute;', 'Ó').replace('&Uacute;', 'Ú')
            text = text.replace('&Ntilde;', 'Ñ')
            
            month_names_es = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
                'xaneiro': 1, 'febreiro': 2, 'marzo': 3, 'abril': 4, 'maio': 5, 'xuño': 6,
                'xullo': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'decembro': 12
            }
            
            # Buscar anexos por provincia
            provinces = {
                'A Coruña': 'ANEXO I',
                'Lugo': 'ANEXO II',
                'Ourense': 'ANEXO III',
                'Pontevedra': 'ANEXO IV'
            }
            
            # Patrón mejorado para el formato del DOG
            # Formato: "30. Coruña, A: 17 de febrero, Martes de Carnaval; 7 de octubre, festividad del Rosario."
            # O: "1. Abegondo: 17 de febrero, Martes de Carnaval; 29 de junio, San Pedro."
            municipality_pattern = r'(\d+)\.\s+([^:]+?):\s+(\d+)\s+de\s+(\w+)[^;]*?;\s+(\d+)\s+de\s+(\w+)'
            
            for province_name, annexo_name in provinces.items():
                # Buscar sección del anexo
                annexo_match = re.search(
                    rf'{annexo_name}.*?Provincia:\s*{province_name}.*?(?={annexo_name}|$)',
                    text,
                    re.IGNORECASE | re.DOTALL
                )
                
                if annexo_match:
                    section_text = annexo_match.group(0)
                    
                    # Buscar todos los municipios en esta sección
                    matches = re.finditer(municipality_pattern, section_text, re.IGNORECASE)
                    
                    for match in matches:
                        municipality = match.group(2).strip()
                        # Limpiar nombre del municipio
                        # Formato puede ser: "Coruña, A" -> "A Coruña"
                        if municipality.endswith(', A'):
                            municipality = 'A ' + municipality[:-3].strip()
                        elif municipality.endswith(', O'):
                            municipality = 'O ' + municipality[:-3].strip()
                        # Limpiar espacios extra
                        municipality = re.sub(r'\s+', ' ', municipality).strip()
                        
                        # Primera fecha
                        day1 = int(match.group(3))
                        month1_name = match.group(4).lower().strip()
                        
                        # Segunda fecha
                        day2 = int(match.group(5))
                        month2_name = match.group(6).lower().strip()
                        
                        # Extraer nombres de festivos del contexto completo
                        full_match_text = match.group(0)
                        
                        # Parsear ambas fechas con sus nombres
                        # Formato: "17 de febrero, Martes de Carnaval; 7 de octubre, festividad del Rosario"
                        for idx, (day, month_name) in enumerate([(day1, month1_name), (day2, month2_name)]):
                            if month_name in month_names_es:
                                month = month_names_es[month_name]
                                try:
                                    holiday_date = date(year, month, day)
                                    
                                    # Extraer nombre del festivo del contexto
                                    holiday_name = None
                                    
                                    if idx == 0:
                                        # Primera fecha: buscar entre la fecha y el punto y coma
                                        # Patrón: "17 de febrero, [nombre];"
                                        name_match = re.search(
                                            rf'{day}\s+de\s+{month_name}[^,]*?,\s*([^;]+)',
                                            full_match_text,
                                            re.IGNORECASE
                                        )
                                    else:
                                        # Segunda fecha: buscar después del punto y coma hasta el punto final
                                        # Patrón: "; 7 de octubre, [nombre]."
                                        name_match = re.search(
                                            rf';\s*{day}\s+de\s+{month_name}[^,]*?,\s*([^.]*)',
                                            full_match_text,
                                            re.IGNORECASE
                                        )
                                    
                                    if name_match:
                                        holiday_name = name_match.group(1).strip()
                                        # Limpiar nombre: quitar "Martes de", "lunes de", etc si está al inicio
                                        holiday_name = re.sub(
                                            r'^(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+de\s+',
                                            '',
                                            holiday_name,
                                            flags=re.IGNORECASE
                                        )
                                        holiday_name = holiday_name.strip()
                                    
                                    # Si no encontramos nombre o es muy genérico, usar nombre descriptivo
                                    if not holiday_name or len(holiday_name) < 5:
                                        holiday_name = f'Festivo local de {municipality}'
                                    else:
                                        holiday_name = holiday_name[:100]  # Truncar
                                    
                                    local_holidays.append({
                                        'name': holiday_name,
                                        'date': holiday_date.isoformat(),
                                        'city': municipality,
                                        'region': 'Galicia',
                                        'country': 'España',
                                        'description': f'Festivo local de {municipality} ({province_name})',
                                        'is_fixed': False
                                    })
                                except ValueError:
                                    logger.warning(f"Fecha inválida: {day}/{month}/{year} para {municipality}")
            
            # Si no encontramos con el patrón principal, intentar patrón alternativo
            if not local_holidays:
                # Patrón más flexible: buscar cualquier línea con formato "municipio: fecha; fecha"
                flexible_pattern = r'([A-ZÁÉÍÓÚÑ][^:]+?):\s*(\d+)\s+de\s+(\w+)[^;]*?;\s*(\d+)\s+de\s+(\w+)'
                matches = re.finditer(flexible_pattern, text, re.IGNORECASE)
                
                for match in matches:
                    municipality = match.group(1).strip()
                    # Limpiar nombre
                    municipality = re.sub(r'^\d+\.\s*', '', municipality).strip()
                    municipality = re.sub(r'^([AO]),\s*', r'\1 ', municipality).strip()
                    
                    for day, month_name in [(int(match.group(2)), match.group(3)), (int(match.group(4)), match.group(5))]:
                        month_name_lower = month_name.lower().strip()
                        if month_name_lower in month_names_es:
                            month = month_names_es[month_name_lower]
                            try:
                                holiday_date = date(year, month, day)
                                
                                if not self._is_national_holiday(holiday_date):
                                    local_holidays.append({
                                        'name': f'Festivo local de {municipality}',
                                        'date': holiday_date.isoformat(),
                                        'city': municipality,
                                        'region': 'Galicia',
                                        'country': 'España',
                                        'description': f'Festivo local de {municipality}',
                                        'is_fixed': False
                                    })
                            except ValueError:
                                pass
            
        except Exception as e:
            logger.error(f"Error parseando resolución del DOG: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return local_holidays
    
    def _extract_holiday_name(self, context: str, day: int, month_name: str) -> Optional[str]:
        """Extrae el nombre del festivo del contexto"""
        # Buscar nombre después de la fecha
        # Ejemplo: "17 de febrero, Martes de Carnaval"
        pattern = rf'{day}\s+de\s+{month_name}[^,]*?,\s*([^;]+)'
        match = re.search(pattern, context, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Limpiar nombre
            name = re.sub(r'^\w+\s+de\s+', '', name)  # Quitar "Martes de" si existe
            return name[:100]  # Truncar si es muy largo
        return None
    
    def _is_national_holiday(self, holiday_date: date) -> bool:
        """Verifica si una fecha es un festivo nacional conocido"""
        national_dates = [
            (1, 1),   # Año Nuevo
            (1, 6),   # Epifanía
            (5, 1),   # Día del Trabajo
            (8, 15),  # Asunción
            (10, 12), # Fiesta Nacional
            (12, 8),  # Inmaculada
            (12, 25), # Navidad
        ]
        
        return (holiday_date.month, holiday_date.day) in national_dates
    
    def load_local_holidays_for_year(self, year: int) -> List[Dict]:
        """
        Carga festivos locales de Galicia para un año específico
        """
        logger.info(f"Buscando festivos locales en DOG para {year}")
        
        # Buscar URL de la resolución
        resolution_url = self.find_resolution_url(year)
        
        if not resolution_url:
            logger.warning(f"No se encontró resolución de festivos locales en DOG para {year}")
            # Intentar URL conocida para 2026
            if year == 2026:
                resolution_url = "https://www.xunta.gal/dog/Publicados/2025/20251030/AnuncioG0767-221025-0001_es.html"
        
        if resolution_url:
            logger.info(f"Parseando resolución: {resolution_url}")
            return self.parse_resolution(resolution_url, year)
        
        return []
