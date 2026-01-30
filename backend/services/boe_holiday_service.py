"""
Servicio para cargar festivos locales desde el BOE y portales de datos abiertos
"""
import requests
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import logging
import re
import json

from models.holiday import Holiday
from models.user import db
from models.location import City, AutonomousCommunity, Province

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger.warning("BeautifulSoup4 no disponible. Algunas funciones de scraping estarán limitadas.")

class BOEHolidayService:
    """Servicio para cargar festivos locales desde el BOE y datos abiertos"""
    
    # API de datos abiertos del gobierno español
    DATOS_GOB_API = "https://datos.gob.es/apidata/catalog/distribution"
    
    # Portal de calendarios laborales
    CALENDARIOS_PORTAL = "https://administracion.gob.es/pag_Home/atencionCiudadana/calendarios/laboral.html"
    
    # Mapeo de comunidades autónomas a códigos ISO
    AUTONOMOUS_COMMUNITY_CODES = {
        'Andalucía': 'ES-AN',
        'Aragón': 'ES-AR',
        'Asturias': 'ES-AS',
        'Baleares': 'ES-IB',
        'Canarias': 'ES-CN',
        'Cantabria': 'ES-CB',
        'Castilla y León': 'ES-CL',
        'Castilla-La Mancha': 'ES-CM',
        'Cataluña': 'ES-CT',
        'Comunidad Valenciana': 'ES-VC',
        'Extremadura': 'ES-EX',
        'Galicia': 'ES-GA',
        'Madrid': 'ES-MD',
        'Murcia': 'ES-MC',
        'Navarra': 'ES-NA',
        'País Vasco': 'ES-PV',
        'La Rioja': 'ES-RI',
        'Ceuta': 'ES-CE',
        'Melilla': 'ES-ML'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'application/json, text/html, */*'
        })
    
    def load_local_holidays_from_datos_gob(self, year: int = None) -> Tuple[int, List[str]]:
        """
        Carga festivos locales desde datos.gob.es
        Busca datasets de calendarios laborales municipales
        """
        if not year:
            year = datetime.now().year
        
        errors = []
        created_count = 0
        
        try:
            # Buscar datasets de calendarios laborales
            search_params = {
                'q': f'calendario laboral {year}',
                'format': 'json',
                'rows': 50
            }
            
            response = self.session.get(
                "https://datos.gob.es/apidata/catalog/distribution",
                params=search_params,
                timeout=30
            )
            
            if response.status_code != 200:
                errors.append(f"Error accediendo a datos.gob.es: {response.status_code}")
                return 0, errors
            
            # Parsear resultados (si la API devuelve JSON)
            try:
                data = response.json()
                # Procesar datasets encontrados
                # Nota: La estructura exacta depende de la API de datos.gob.es
                logger.info(f"Encontrados datasets en datos.gob.es para {year}")
            except:
                # Si no es JSON, intentar scraping HTML
                logger.info("Intentando scraping de datos.gob.es")
                pass
            
        except Exception as e:
            errors.append(f"Error en load_local_holidays_from_datos_gob: {e}")
            logger.error(f"Error cargando desde datos.gob.es: {e}")
        
        return created_count, errors
    
    def parse_boe_resolution(self, boe_text: str, year: int = None) -> List[Dict]:
        """
        Parsea una resolución del BOE sobre calendarios laborales
        Extrae festivos locales mencionados en las notas aclaratorias
        """
        if not year:
            year = datetime.now().year
        
        local_holidays = []
        
        try:
            # Buscar notas aclaratorias que mencionan festivos locales
            # El BOE menciona festivos locales en notas como:
            # "en El Hierro: el 24 de septiembre, festividad de Nuestra Señora de los Reyes"
            
            # Patrón mejorado para encontrar festivos locales individuales
            # Captura: "en [ubicación]: el [día] de [mes], festividad de [nombre]"
            # Usamos lookahead negativo para evitar capturar múltiples festivos
            pattern = r'en\s+([^:]+?):\s+el\s+(\d+)\s+de\s+(\w+),\s+festividad\s+de\s+([^;]+?)(?=\s*;|\.|$)'
            
            import re
            matches = re.finditer(pattern, boe_text, re.IGNORECASE | re.DOTALL)
            
            month_names_es = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            
            for match in matches:
                location = match.group(1).strip()
                day = int(match.group(2))
                month_name = match.group(3).lower().strip()
                holiday_name = match.group(4).strip()
                
                # Limpiar nombre del festivo (puede tener caracteres especiales)
                holiday_name = re.sub(r'\s+', ' ', holiday_name).strip()
                # Truncar si es muy largo (máximo 200 caracteres para la BD)
                if len(holiday_name) > 200:
                    holiday_name = holiday_name[:197] + '...'
                
                if month_name in month_names_es:
                    month = month_names_es[month_name]
                    try:
                        holiday_date = date(year, month, day)
                    except ValueError:
                        logger.warning(f"Fecha inválida: {day}/{month}/{year} para {location}")
                        continue
                    
                    # Determinar ciudad y región basándose en la ubicación
                    city = location
                    region = None
                    
                    # Mapear ubicaciones conocidas a regiones
                    if any(island in location for island in ['El Hierro', 'Fuerteventura', 'Gran Canaria', 
                                                              'La Gomera', 'La Palma', 'Lanzarote', 'La Graciosa', 'Tenerife']):
                        region = 'Canarias'
                    elif 'Arán' in location or 'Aran' in location:
                        region = 'Cataluña'
                    
                    local_holidays.append({
                        'name': holiday_name,
                        'date': holiday_date.isoformat(),
                        'city': city[:100] if city else None,  # Truncar ciudad también
                        'region': region[:100] if region else None,  # Truncar región también
                        'country': 'España',
                        'description': f'Festivo local de {location}'[:500] if location else '',  # Truncar descripción
                        'is_fixed': False
                    })
            
        except Exception as e:
            logger.error(f"Error parseando resolución del BOE: {e}")
        
        return local_holidays
    
    def load_local_holidays_from_boe_resolutions(self, year: int = None) -> Tuple[int, List[str]]:
        """
        Carga festivos locales desde resoluciones del BOE
        Busca resoluciones de calendarios laborales municipales
        """
        if not year:
            year = datetime.now().year
        
        errors = []
        created_count = 0
        
        try:
            # URL de la resolución del BOE para el año específico
            # Formato: https://www.boe.es/diario_boe/txt.php?id=BOE-A-{year-1}-{numero}
            # Para 2026, la resolución es BOE-A-2025-21667
            
            boe_id_map = {
                2026: 'BOE-A-2025-21667',
                2025: 'BOE-A-2024-21316',
                2024: 'BOE-A-2023-22014',
                2023: 'BOE-A-2022-16755'
            }
            
            boe_id = boe_id_map.get(year)
            if not boe_id:
                errors.append(f"No hay mapeo de BOE ID para el año {year}")
                return 0, errors
            
            boe_url = f"https://www.boe.es/diario_boe/txt.php?id={boe_id}"
            
            response = self.session.get(boe_url, timeout=30)
            
            if response.status_code == 200:
                # Parsear texto del BOE
                boe_text = response.text
                
                # Extraer festivos locales del texto
                local_holidays_data = self.parse_boe_resolution(boe_text, year)
                
                if local_holidays_data:
                    # Cargar festivos locales encontrados
                    created_count, parse_errors = self.load_local_holidays_from_manual_data(
                        local_holidays_data, year
                    )
                    errors.extend(parse_errors)
                    logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOE para {year}")
                else:
                    logger.info(f"No se encontraron festivos locales en la resolución del BOE para {year}")
            else:
                errors.append(f"Error accediendo al BOE: HTTP {response.status_code}")
                
        except Exception as e:
            errors.append(f"Error en load_local_holidays_from_boe_resolutions: {e}")
            logger.error(f"Error cargando desde BOE: {e}")
        
        return created_count, errors
    
    def load_local_holidays_for_cities(self, cities: List[str], year: int = None) -> Tuple[int, List[str]]:
        """
        Carga festivos locales para ciudades específicas
        Busca en portales municipales o APIs locales
        """
        if not year:
            year = datetime.now().year
        
        errors = []
        created_count = 0
        
        # Obtener ciudades de la BD que tienen empleados
        cities_with_employees = db.session.query(City.name).distinct().all()
        cities_list = [c[0] for c in cities_with_employees if c[0]]
        
        if not cities_list:
            logger.info("No hay ciudades con empleados para cargar festivos locales")
            return 0, []
        
        logger.info(f"Cargando festivos locales para {len(cities_list)} ciudades")
        
        # Por ahora, retornamos 0 ya que requiere integración con APIs municipales
        # TODO: Implementar integración con APIs municipales específicas
        
        return created_count, errors
    
    def load_local_holidays_from_manual_data(self, holidays_data: List[Dict], year: int = None) -> Tuple[int, List[str]]:
        """
        Carga festivos locales desde datos manuales proporcionados
        Formato esperado:
        [
            {
                'name': 'Fiesta Local',
                'date': '2026-06-15',
                'city': 'Madrid',
                'region': 'Madrid',
                'country': 'España',
                'description': 'Fiesta patronal'
            },
            ...
        ]
        """
        if not year:
            year = datetime.now().year
            
        errors = []
        created_count = 0
        
        if not holidays_data:
            return 0, ["No se proporcionaron datos de festivos"]
        
        holidays_to_create = []
        
        for holiday_data in holidays_data:
            try:
                # Validar datos requeridos
                if not all(k in holiday_data for k in ['name', 'date', 'city', 'country']):
                    errors.append(f"Faltan datos requeridos en festivo: {holiday_data.get('name', 'Unknown')}")
                    continue
                
                # Parsear fecha
                if isinstance(holiday_data['date'], str):
                    holiday_date = datetime.strptime(holiday_data['date'], '%Y-%m-%d').date()
                else:
                    holiday_date = holiday_data['date']
                
                # Normalizar país
                country = holiday_data['country']
                if country not in ['España', 'Spain']:
                    country = 'España'  # Por ahora solo soportamos España
                
                # Truncar campos para cumplir con límites de la BD
                name = holiday_data['name'][:200] if len(holiday_data['name']) > 200 else holiday_data['name']
                city = holiday_data['city'][:100] if len(holiday_data['city']) > 100 else holiday_data['city']
                region = holiday_data.get('region')
                if region and len(region) > 100:
                    region = region[:100]
                description = holiday_data.get('description', '')
                if len(description) > 500:
                    description = description[:500]
                
                holiday_dict = {
                    'name': name,
                    'date': holiday_date,
                    'country': country,
                    'region': region,
                    'city': city,
                    'holiday_type': 'local',
                    'description': description,
                    'is_fixed': holiday_data.get('is_fixed', False),
                    'source': 'boe.manual',
                    'source_id': f"local_{city}_{year}_{holiday_date.isoformat()}"[:100]  # Truncar source_id también
                }
                
                holidays_to_create.append(holiday_dict)
                
            except Exception as e:
                errors.append(f"Error procesando festivo {holiday_data.get('name', 'Unknown')}: {e}")
                continue
        
        # Crear festivos en lote
        if holidays_to_create:
            created_count = Holiday.bulk_create_holidays(holidays_to_create)
            logger.info(f"Cargados {created_count} festivos locales desde datos manuales")
        
        return created_count, errors
    
    def load_local_holidays_from_json_file(self, file_path: str) -> Tuple[int, List[str]]:
        """
        Carga festivos locales desde un archivo JSON
        Útil para importar datos de fuentes externas o manuales
        """
        errors = []
        created_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                holidays_data = json.load(f)
            
            if not isinstance(holidays_data, list):
                return 0, ["El archivo JSON debe contener un array de festivos"]
            
            created_count, errors = self.load_local_holidays_from_manual_data(holidays_data)
            
        except FileNotFoundError:
            errors.append(f"Archivo no encontrado: {file_path}")
        except json.JSONDecodeError as e:
            errors.append(f"Error parseando JSON: {e}")
        except Exception as e:
            errors.append(f"Error cargando desde archivo: {e}")
            logger.error(f"Error cargando festivos desde {file_path}: {e}")
        
        return created_count, errors
    
    def get_cities_with_employees(self) -> List[Dict]:
        """Obtiene lista de ciudades que tienen empleados"""
        from models.employee import Employee
        
        cities_data = db.session.query(
            Employee.city,
            Employee.region,
            Employee.country
        ).filter(
            Employee.city.isnot(None),
            Employee.city != ''
        ).distinct().all()
        
        return [
            {
                'city': city,
                'region': region,
                'country': country
            }
            for city, region, country in cities_data
        ]
    
    def load_local_holidays_for_year(self, year: int = None) -> Dict:
        """
        Carga festivos locales para un año específico
        Intenta múltiples fuentes: datos.gob.es, BOE, APIs municipales
        """
        if not year:
            year = datetime.now().year
        
        results = {
            'year': year,
            'total_loaded': 0,
            'sources': {},
            'errors': []
        }
        
        # 1. Intentar desde datos.gob.es
        count, errors = self.load_local_holidays_from_datos_gob(year)
        results['sources']['datos_gob'] = {'loaded': count, 'errors': errors}
        results['total_loaded'] += count
        results['errors'].extend(errors)
        
        # 2. Intentar desde resoluciones del BOE
        count, errors = self.load_local_holidays_from_boe_resolutions(year)
        results['sources']['boe'] = {'loaded': count, 'errors': errors}
        results['total_loaded'] += count
        results['errors'].extend(errors)
        
        # 3. Cargar para ciudades con empleados
        cities = self.get_cities_with_employees()
        count, errors = self.load_local_holidays_for_cities([c['city'] for c in cities], year)
        results['sources']['municipal'] = {'loaded': count, 'errors': errors}
        results['total_loaded'] += count
        results['errors'].extend(errors)
        
        return results
