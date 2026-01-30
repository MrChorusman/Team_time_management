"""
Servicio para cargar festivos locales desde Boletines Oficiales de Comunidades Autónomas
"""
import requests
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import logging
import re

from models.holiday import Holiday
from models.user import db

logger = logging.getLogger(__name__)

class CCAABOEService:
    """Servicio para acceder a Boletines Oficiales de CCAA"""
    
    # URLs base de los Boletines Oficiales de cada CCAA
    BOE_URLS = {
        'Andalucía': {
            'boe': 'BOJA',
            'url_base': 'https://www.juntadeandalucia.es/boja',
            'search_url': 'https://www.juntadeandalucia.es/boja/buscar'
        },
        'Aragón': {
            'boe': 'BOA',
            'url_base': 'https://www.boa.aragon.es',
            'search_url': 'https://www.boa.aragon.es/buscar'
        },
        'Asturias': {
            'boe': 'BOPA',
            'url_base': 'https://sede.asturias.es/bopa',
            'search_url': 'https://sede.asturias.es/bopa/buscar'
        },
        'Baleares': {
            'boe': 'BOIB',
            'url_base': 'https://www.boib.es',
            'search_url': 'https://www.boib.es/buscar'
        },
        'Canarias': {
            'boe': 'BOC',
            'url_base': 'https://www.gobiernodecanarias.org/boc',
            'search_url': 'https://www.gobiernodecanarias.org/boc/buscar'
        },
        'Cantabria': {
            'boe': 'BOC',
            'url_base': 'https://boc.cantabria.es',
            'search_url': 'https://boc.cantabria.es/buscar'
        },
        'Castilla-La Mancha': {
            'boe': 'DOCM',
            'url_base': 'https://docm.jccm.es',
            'search_url': 'https://docm.jccm.es/buscar'
        },
        'Castilla y León': {
            'boe': 'BOCYL',
            'url_base': 'https://bocyl.jcyl.es',
            'search_url': 'https://bocyl.jcyl.es/buscar'
        },
        'Cataluña': {
            'boe': 'DOGC',
            'url_base': 'https://dogc.gencat.cat',
            'search_url': 'https://dogc.gencat.cat/buscar'
        },
        'Comunidad Valenciana': {
            'boe': 'DOGV',
            'url_base': 'https://dogv.gva.es',
            'search_url': 'https://dogv.gva.es/buscar'
        },
        'Extremadura': {
            'boe': 'DOE',
            'url_base': 'https://doe.juntaex.es',
            'search_url': 'https://doe.juntaex.es/buscar'
        },
        'Galicia': {
            'boe': 'DOG',
            'url_base': 'https://www.xunta.gal/diario-oficial-galicia',
            'search_url': 'https://www.xunta.gal/diario-oficial-galicia/buscar'
        },
        'Madrid': {
            'boe': 'BOCM',
            'url_base': 'https://www.bocm.es',
            'search_url': 'https://www.bocm.es/buscar'
        },
        'Murcia': {
            'boe': 'BORM',
            'url_base': 'https://www.borm.es',
            'search_url': 'https://www.borm.es/buscar'
        },
        'Navarra': {
            'boe': 'BON',
            'url_base': 'https://bon.navarra.es',
            'search_url': 'https://bon.navarra.es/buscar'
        },
        'País Vasco': {
            'boe': 'BOPV',
            'url_base': 'https://www.euskadi.eus/bopv',
            'search_url': 'https://www.euskadi.eus/bopv/buscar'
        },
        'La Rioja': {
            'boe': 'BOR',
            'url_base': 'https://www.larioja.org/bor',
            'search_url': 'https://www.larioja.org/bor/buscar'
        }
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TeamTimeManagement/1.0',
            'Accept': 'text/html, application/json, */*'
        })
    
    def search_local_holidays_in_ccaa_boe(self, region: str, year: int = None) -> Tuple[int, List[str]]:
        """
        Busca festivos locales en el Boletín Oficial de una CCAA específica
        """
        if not year:
            year = datetime.now().year
        
        errors = []
        created_count = 0
        
        if region not in self.BOE_URLS:
            return 0, [f"Región '{region}' no tiene configuración de BOE"]
        
        boe_config = self.BOE_URLS[region]
        logger.info(f"Buscando festivos locales en {boe_config['boe']} para {region} ({year})")
        
        # Por ahora, retornamos 0 ya que requiere análisis específico de cada BOE
        # TODO: Implementar scraping específico para cada tipo de BOE
        # Cada CCAA tiene un formato diferente de publicación
        
        return created_count, errors
    
    def load_local_holidays_from_all_ccaas(self, year: int = None) -> Dict:
        """
        Carga festivos locales desde todos los Boletines de CCAA disponibles
        """
        if not year:
            year = datetime.now().year
        
        results = {
            'year': year,
            'total_loaded': 0,
            'by_region': {},
            'errors': []
        }
        
        # Obtener regiones con empleados
        from models.employee import Employee
        regions_with_employees = db.session.query(
            Employee.region
        ).filter(
            Employee.region.isnot(None),
            Employee.region != '',
            Employee.country.in_(['España', 'Spain'])
        ).distinct().all()
        
        regions_list = [r[0] for r in regions_with_employees if r[0]]
        
        logger.info(f"Buscando festivos locales en {len(regions_list)} CCAA con empleados")
        
        for region in regions_list:
            if region in self.BOE_URLS:
                count, errors = self.search_local_holidays_in_ccaa_boe(region, year)
                results['by_region'][region] = {
                    'loaded': count,
                    'errors': errors
                }
                results['total_loaded'] += count
                results['errors'].extend(errors)
        
        return results
