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

# Importar parsers específicos
try:
    from services.parsers.dog_parser import DOGParser
    HAS_DOG_PARSER = True
except ImportError:
    HAS_DOG_PARSER = False
    logger.warning("DOG parser no disponible")

try:
    from services.parsers.boja_parser import BOJAParser
    HAS_BOJA_PARSER = True
except ImportError:
    HAS_BOJA_PARSER = False
    logger.warning("BOJA parser no disponible")

try:
    from services.parsers.dogc_parser import DOGCParser
    HAS_DOGC_PARSER = True
except ImportError:
    HAS_DOGC_PARSER = False
    logger.warning("DOGC parser no disponible")

try:
    from services.parsers.bocm_parser import BOCMParser
    HAS_BOCM_PARSER = True
except ImportError:
    HAS_BOCM_PARSER = False
    logger.warning("BOCM parser no disponible")

try:
    from services.parsers.dogv_parser import DOGVParser
    HAS_DOGV_PARSER = True
except ImportError:
    HAS_DOGV_PARSER = False
    logger.warning("DOGV parser no disponible")

try:
    from services.parsers.bopv_parser import BOPVParser
    HAS_BOPV_PARSER = True
except ImportError:
    HAS_BOPV_PARSER = False
    logger.warning("BOPV parser no disponible")

try:
    from services.parsers.boa_parser import BOAParser
    HAS_BOA_PARSER = True
except ImportError:
    HAS_BOA_PARSER = False

try:
    from services.parsers.bopa_parser import BOPAParser
    HAS_BOPA_PARSER = True
except ImportError:
    HAS_BOPA_PARSER = False

try:
    from services.parsers.boib_parser import BOIBParser
    HAS_BOIB_PARSER = True
except ImportError:
    HAS_BOIB_PARSER = False

try:
    from services.parsers.boc_canarias_parser import BOCCanariasParser
    HAS_BOC_CANARIAS_PARSER = True
except ImportError:
    HAS_BOC_CANARIAS_PARSER = False

try:
    from services.parsers.boc_cantabria_parser import BOCCantabriaParser
    HAS_BOC_CANTABRIA_PARSER = True
except ImportError:
    HAS_BOC_CANTABRIA_PARSER = False

try:
    from services.parsers.docm_parser import DOCMParser
    HAS_DOCM_PARSER = True
except ImportError:
    HAS_DOCM_PARSER = False

try:
    from services.parsers.bocyl_parser import BOCYLParser
    HAS_BOCYL_PARSER = True
except ImportError:
    HAS_BOCYL_PARSER = False

try:
    from services.parsers.doe_parser import DOEParser
    HAS_DOE_PARSER = True
except ImportError:
    HAS_DOE_PARSER = False

try:
    from services.parsers.borm_parser import BORMParser
    HAS_BORM_PARSER = True
except ImportError:
    HAS_BORM_PARSER = False

try:
    from services.parsers.bon_parser import BONParser
    HAS_BON_PARSER = True
except ImportError:
    HAS_BON_PARSER = False

try:
    from services.parsers.bor_parser import BORParser
    HAS_BOR_PARSER = True
except ImportError:
    HAS_BOR_PARSER = False

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
        
        local_holidays_data = []
        
        # Usar parser específico según la CCAA
        try:
            if region == 'Galicia' and HAS_DOG_PARSER:
                parser = DOGParser(self.session)
                # Buscar URL de resolución
                resolution_url = parser.find_resolution_url(year)
                if not resolution_url and year == 2026:
                    # URL conocida para 2026
                    resolution_url = "https://www.xunta.gal/dog/Publicados/2025/20251030/AnuncioG0767-221025-0001_es.html"
                
                if resolution_url:
                    local_holidays_data = parser.parse_resolution(resolution_url, year)
                    logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del DOG para {region}")
                else:
                    errors.append(f"No se encontró resolución del DOG para {year}")
            
            elif region == 'Andalucía' and HAS_BOJA_PARSER:
                parser = BOJAParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOJA para {region}")
            
            elif region == 'Cataluña' and HAS_DOGC_PARSER:
                parser = DOGCParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del DOGC para {region}")
            
            elif region == 'Madrid' and HAS_BOCM_PARSER:
                parser = BOCMParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOCM para {region}")
            
            elif region == 'Comunidad Valenciana' and HAS_DOGV_PARSER:
                parser = DOGVParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del DOGV para {region}")
            
            elif region == 'País Vasco' and HAS_BOPV_PARSER:
                parser = BOPVParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOPV para {region}")
            
            elif region == 'Aragón' and HAS_BOA_PARSER:
                parser = BOAParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOA para {region}")
            
            elif region == 'Asturias' and HAS_BOPA_PARSER:
                parser = BOPAParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOPA para {region}")
            
            elif region == 'Baleares' and HAS_BOIB_PARSER:
                parser = BOIBParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOIB para {region}")
            
            elif region == 'Canarias' and HAS_BOC_CANARIAS_PARSER:
                parser = BOCCanariasParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOC Canarias para {region}")
            
            elif region == 'Cantabria' and HAS_BOC_CANTABRIA_PARSER:
                parser = BOCCantabriaParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOC Cantabria para {region}")
            
            elif region == 'Castilla-La Mancha' and HAS_DOCM_PARSER:
                parser = DOCMParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del DOCM para {region}")
            
            elif region == 'Castilla y León' and HAS_BOCYL_PARSER:
                parser = BOCYLParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOCYL para {region}")
            
            elif region == 'Extremadura' and HAS_DOE_PARSER:
                parser = DOEParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del DOE para {region}")
            
            elif region == 'Murcia' and HAS_BORM_PARSER:
                parser = BORMParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BORM para {region}")
            
            elif region == 'Navarra' and HAS_BON_PARSER:
                parser = BONParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BON para {region}")
            
            elif region == 'La Rioja' and HAS_BOR_PARSER:
                parser = BORParser(self.session)
                local_holidays_data = parser.load_local_holidays_for_year(year)
                logger.info(f"Extraídos {len(local_holidays_data)} festivos locales del BOR para {region}")
            
            else:
                # Para otras CCAA, aún no implementado
                logger.info(f"Parser para {region} ({boe_config['boe']}) aún no implementado")
                errors.append(f"Parser para {boe_config['boe']} no implementado aún")
        
        except Exception as e:
            error_msg = f"Error procesando {region}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Cargar festivos locales encontrados
        if local_holidays_data:
            from services.boe_holiday_service import BOEHolidayService
            boe_service = BOEHolidayService()
            created_count, load_errors = boe_service.load_local_holidays_from_manual_data(
                local_holidays_data, year
            )
            errors.extend(load_errors)
        
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
