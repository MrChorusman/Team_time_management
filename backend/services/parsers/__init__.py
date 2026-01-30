"""
Parsers para Boletines Oficiales de Comunidades Autónomas
"""
from .dog_parser import DOGParser
from .boja_parser import BOJAParser
from .dogc_parser import DOGCParser
from .bocm_parser import BOCMParser
from .dogv_parser import DOGVParser
from .bopv_parser import BOPVParser
from .boa_parser import BOAParser
from .bopa_parser import BOPAParser
from .boib_parser import BOIBParser
from .boc_canarias_parser import BOCCanariasParser
from .boc_cantabria_parser import BOCCantabriaParser
from .docm_parser import DOCMParser
from .bocyl_parser import BOCYLParser
from .doe_parser import DOEParser
from .borm_parser import BORMParser
from .bon_parser import BONParser
from .bor_parser import BORParser

__all__ = [
    'DOGParser', 'BOJAParser', 'DOGCParser', 'BOCMParser', 'DOGVParser', 'BOPVParser',
    'BOAParser', 'BOPAParser', 'BOIBParser', 'BOCCanariasParser', 'BOCCantabriaParser',
    'DOCMParser', 'BOCYLParser', 'DOEParser', 'BORMParser', 'BONParser', 'BORParser'
]
