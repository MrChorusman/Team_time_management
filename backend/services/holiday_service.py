import requests
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import logging
from flask import current_app

from models.holiday import Holiday
from models.user import db

logger = logging.getLogger(__name__)

class HolidayService:
    """Servicio para gestión automática de festivos globales"""
    
    # Países soportados por la API Nager.Date
    SUPPORTED_COUNTRIES = {
        'AD': 'Andorra', 'AR': 'Argentina', 'AT': 'Austria', 'AU': 'Australia',
        'AX': 'Åland Islands', 'BB': 'Barbados', 'BE': 'Belgium', 'BG': 'Bulgaria',
        'BJ': 'Benin', 'BO': 'Bolivia', 'BR': 'Brazil', 'BS': 'Bahamas',
        'BW': 'Botswana', 'BY': 'Belarus', 'BZ': 'Belize', 'CA': 'Canada',
        'CH': 'Switzerland', 'CL': 'Chile', 'CN': 'China', 'CO': 'Colombia',
        'CR': 'Costa Rica', 'CU': 'Cuba', 'CY': 'Cyprus', 'CZ': 'Czech Republic',
        'DE': 'Germany', 'DK': 'Denmark', 'DO': 'Dominican Republic', 'EC': 'Ecuador',
        'EE': 'Estonia', 'EG': 'Egypt', 'ES': 'Spain', 'FI': 'Finland',
        'FO': 'Faroe Islands', 'FR': 'France', 'GA': 'Gabon', 'GB': 'United Kingdom',
        'GD': 'Grenada', 'GG': 'Guernsey', 'GI': 'Gibraltar', 'GL': 'Greenland',
        'GM': 'Gambia', 'GR': 'Greece', 'GT': 'Guatemala', 'GU': 'Guam',
        'GY': 'Guyana', 'HK': 'Hong Kong', 'HN': 'Honduras', 'HR': 'Croatia',
        'HT': 'Haiti', 'HU': 'Hungary', 'ID': 'Indonesia', 'IE': 'Ireland',
        'IM': 'Isle of Man', 'IS': 'Iceland', 'IT': 'Italy', 'JE': 'Jersey',
        'JM': 'Jamaica', 'JP': 'Japan', 'KR': 'South Korea', 'LI': 'Liechtenstein',
        'LS': 'Lesotho', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia',
        'MA': 'Morocco', 'MC': 'Monaco', 'MD': 'Moldova', 'MG': 'Madagascar',
        'MK': 'North Macedonia', 'MN': 'Mongolia', 'MS': 'Montserrat', 'MT': 'Malta',
        'MW': 'Malawi', 'MX': 'Mexico', 'MZ': 'Mozambique', 'NA': 'Namibia',
        'NE': 'Niger', 'NG': 'Nigeria', 'NI': 'Nicaragua', 'NL': 'Netherlands',
        'NO': 'Norway', 'NZ': 'New Zealand', 'PA': 'Panama', 'PE': 'Peru',
        'PL': 'Poland', 'PR': 'Puerto Rico', 'PT': 'Portugal', 'PY': 'Paraguay',
        'RO': 'Romania', 'RS': 'Serbia', 'RU': 'Russia', 'SE': 'Sweden',
        'SG': 'Singapore', 'SI': 'Slovenia', 'SJ': 'Svalbard and Jan Mayen',
        'SK': 'Slovakia', 'SM': 'San Marino', 'SR': 'Suriname', 'SV': 'El Salvador',
        'TN': 'Tunisia', 'TR': 'Turkey', 'UA': 'Ukraine', 'US': 'United States',
        'UY': 'Uruguay', 'VA': 'Vatican City', 'VE': 'Venezuela', 'VG': 'British Virgin Islands',
        'VI': 'U.S. Virgin Islands', 'ZA': 'South Africa', 'ZW': 'Zimbabwe'
    }
    
    def __init__(self):
        self.api_base_url = current_app.config.get('NAGER_DATE_API_URL', 'https://date.nager.at/api/v3')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'application/json'
        })
    
    def get_available_countries(self) -> List[Dict]:
        """Obtiene la lista de países disponibles en la API"""
        try:
            response = self.session.get(f"{self.api_base_url}/AvailableCountries")
            response.raise_for_status()
            
            countries = response.json()
            
            # Enriquecer con información local
            for country in countries:
                country_code = country.get('countryCode')
                if country_code in self.SUPPORTED_COUNTRIES:
                    country['supported'] = True
                    country['local_name'] = self.SUPPORTED_COUNTRIES[country_code]
                else:
                    country['supported'] = False
            
            return countries
            
        except requests.RequestException as e:
            logger.error(f"Error obteniendo países disponibles: {e}")
            return []
    
    def load_holidays_for_country(self, country_code: str, year: int = None) -> Tuple[int, List[str]]:
        """Carga festivos para un país específico"""
        if not year:
            year = datetime.now().year
        
        try:
            response = self.session.get(f"{self.api_base_url}/PublicHolidays/{year}/{country_code}")
            response.raise_for_status()
            
            holidays_data = response.json()
            
            if not holidays_data:
                return 0, [f"No se encontraron festivos para {country_code} en {year}"]
            
            holidays_to_create = []
            errors = []
            
            for holiday_data in holidays_data:
                try:
                    # Parsear fecha
                    holiday_date = datetime.strptime(holiday_data['date'], '%Y-%m-%d').date()
                    
                    # Determinar tipo y ubicación
                    holiday_type = 'national'
                    region = None
                    city = None
                    
                    # Algunos festivos pueden tener información regional
                    if 'counties' in holiday_data and holiday_data['counties']:
                        # Si tiene condados/regiones específicas, es regional
                        holiday_type = 'regional'
                        region = holiday_data['counties'][0] if holiday_data['counties'] else None
                    
                    holiday_dict = {
                        'name': holiday_data['name'],
                        'date': holiday_date,
                        'country': self.SUPPORTED_COUNTRIES.get(country_code, country_code),
                        'region': region,
                        'city': city,
                        'holiday_type': holiday_type,
                        'description': holiday_data.get('localName', ''),
                        'is_fixed': holiday_data.get('fixed', True),
                        'source': 'nager.date',
                        'source_id': f"{country_code}_{year}_{holiday_data['date']}"
                    }
                    
                    holidays_to_create.append(holiday_dict)
                    
                except Exception as e:
                    errors.append(f"Error procesando festivo {holiday_data.get('name', 'Unknown')}: {e}")
                    continue
            
            # Crear festivos en lote
            created_count = Holiday.bulk_create_holidays(holidays_to_create)
            
            logger.info(f"Cargados {created_count} festivos para {country_code} ({year})")
            
            return created_count, errors
            
        except requests.RequestException as e:
            error_msg = f"Error cargando festivos para {country_code}: {e}"
            logger.error(error_msg)
            return 0, [error_msg]
    
    def load_holidays_for_employee_location(self, employee) -> Tuple[int, List[str]]:
        """Carga festivos automáticamente para la ubicación de un empleado"""
        # Mapear país a código ISO
        country_code = self.get_country_code(employee.country)
        
        if not country_code:
            return 0, [f"País '{employee.country}' no soportado por la API de festivos"]
        
        # Cargar festivos para el año actual y siguiente
        current_year = datetime.now().year
        total_created = 0
        all_errors = []
        
        for year in [current_year, current_year + 1]:
            created, errors = self.load_holidays_for_country(country_code, year)
            total_created += created
            all_errors.extend(errors)
        
        return total_created, all_errors
    
    def get_country_code(self, country_name: str) -> Optional[str]:
        """Obtiene el código ISO del país a partir del nombre"""
        # Buscar por nombre exacto
        for code, name in self.SUPPORTED_COUNTRIES.items():
            if name.lower() == country_name.lower():
                return code
        
        # Buscar por coincidencia parcial
        country_name_lower = country_name.lower()
        for code, name in self.SUPPORTED_COUNTRIES.items():
            if country_name_lower in name.lower() or name.lower() in country_name_lower:
                return code
        
        return None
    
    def auto_load_missing_holidays(self) -> Dict:
        """Carga automáticamente festivos para países que no los tienen"""
        from models.employee import Employee
        
        # Obtener países únicos de empleados
        countries_in_use = db.session.query(Employee.country).distinct().all()
        countries_in_use = [country[0] for country in countries_in_use if country[0]]
        
        results = {
            'processed_countries': [],
            'total_holidays_loaded': 0,
            'errors': []
        }
        
        for country in countries_in_use:
            # Verificar si ya tiene festivos para el año actual
            current_year = datetime.now().year
            existing_holidays = Holiday.query.filter(
                Holiday.country == country,
                db.extract('year', Holiday.date) == current_year
            ).count()
            
            if existing_holidays == 0:
                logger.info(f"Cargando festivos automáticamente para {country}")
                created, errors = self.load_holidays_for_employee_location_by_country(country)
                
                results['processed_countries'].append({
                    'country': country,
                    'holidays_loaded': created,
                    'errors': errors
                })
                results['total_holidays_loaded'] += created
                results['errors'].extend(errors)
        
        return results
    
    def load_holidays_for_employee_location_by_country(self, country_name: str) -> Tuple[int, List[str]]:
        """Carga festivos para un país por nombre"""
        country_code = self.get_country_code(country_name)
        
        if not country_code:
            return 0, [f"País '{country_name}' no soportado"]
        
        current_year = datetime.now().year
        total_created = 0
        all_errors = []
        
        for year in [current_year, current_year + 1]:
            created, errors = self.load_holidays_for_country(country_code, year)
            total_created += created
            all_errors.extend(errors)
        
        return total_created, all_errors
    
    def get_holidays_for_employee(self, employee, year: int = None) -> List[Holiday]:
        """Obtiene todos los festivos aplicables para un empleado"""
        if not year:
            year = datetime.now().year
        
        return Holiday.get_holidays_for_location(
            country=employee.country,
            region=employee.region,
            city=employee.city,
            year=year
        )
    
    def get_holidays_summary(self) -> Dict:
        """Obtiene resumen estadístico de festivos cargados"""
        total_holidays = Holiday.query.filter(Holiday.active == True).count()
        
        # Festivos por país
        countries_stats = db.session.query(
            Holiday.country,
            db.func.count(Holiday.id).label('count')
        ).filter(
            Holiday.active == True
        ).group_by(Holiday.country).order_by(db.desc('count')).all()
        
        # Festivos por tipo
        type_stats = db.session.query(
            Holiday.holiday_type,
            db.func.count(Holiday.id).label('count')
        ).filter(
            Holiday.active == True
        ).group_by(Holiday.holiday_type).all()
        
        # Países sin festivos
        from models.employee import Employee
        countries_with_employees = db.session.query(Employee.country).distinct().all()
        countries_with_employees = [c[0] for c in countries_with_employees if c[0]]
        
        countries_with_holidays = [c[0] for c in countries_stats]
        countries_without_holidays = [
            c for c in countries_with_employees 
            if c not in countries_with_holidays
        ]
        
        return {
            'total_holidays': total_holidays,
            'countries_with_holidays': len(countries_stats),
            'countries_without_holidays': len(countries_without_holidays),
            'countries_stats': [
                {'country': country, 'count': count} 
                for country, count in countries_stats[:10]  # Top 10
            ],
            'type_stats': [
                {'type': holiday_type, 'count': count}
                for holiday_type, count in type_stats
            ],
            'missing_countries': countries_without_holidays
        }
    
    def refresh_holidays_for_year(self, year: int) -> Dict:
        """Actualiza todos los festivos para un año específico"""
        from models.employee import Employee
        
        # Obtener países únicos de empleados
        countries_in_use = db.session.query(Employee.country).distinct().all()
        countries_in_use = [country[0] for country in countries_in_use if country[0]]
        
        results = {
            'year': year,
            'processed_countries': [],
            'total_holidays_loaded': 0,
            'errors': []
        }
        
        for country in countries_in_use:
            country_code = self.get_country_code(country)
            if country_code:
                created, errors = self.load_holidays_for_country(country_code, year)
                
                results['processed_countries'].append({
                    'country': country,
                    'holidays_loaded': created,
                    'errors': errors
                })
                results['total_holidays_loaded'] += created
                results['errors'].extend(errors)
        
        return results
