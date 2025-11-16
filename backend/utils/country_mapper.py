"""
Utilidad para mapear nombres de países entre diferentes formatos
(inglés, español, códigos ISO) para compatibilidad con festivos
"""

# Mapeo completo bidireccional de países
# Formato: {código_iso: {'en': nombre_inglés, 'es': nombre_español}}
COUNTRY_MAPPING = {
    'ES': {'en': 'Spain', 'es': 'España'},
    'US': {'en': 'United States', 'es': 'Estados Unidos'},
    'GB': {'en': 'United Kingdom', 'es': 'Reino Unido'},
    'FR': {'en': 'France', 'es': 'Francia'},
    'DE': {'en': 'Germany', 'es': 'Alemania'},
    'IT': {'en': 'Italy', 'es': 'Italia'},
    'PT': {'en': 'Portugal', 'es': 'Portugal'},
    'MX': {'en': 'Mexico', 'es': 'México'},
    'AR': {'en': 'Argentina', 'es': 'Argentina'},
    'CO': {'en': 'Colombia', 'es': 'Colombia'},
    'CL': {'en': 'Chile', 'es': 'Chile'},
    'PE': {'en': 'Peru', 'es': 'Perú'},
    'VE': {'en': 'Venezuela', 'es': 'Venezuela'},
    'EC': {'en': 'Ecuador', 'es': 'Ecuador'},
    'BO': {'en': 'Bolivia', 'es': 'Bolivia'},
    'PY': {'en': 'Paraguay', 'es': 'Paraguay'},
    'UY': {'en': 'Uruguay', 'es': 'Uruguay'},
    'CR': {'en': 'Costa Rica', 'es': 'Costa Rica'},
    'PA': {'en': 'Panama', 'es': 'Panamá'},
    'DO': {'en': 'Dominican Republic', 'es': 'República Dominicana'},
    'GT': {'en': 'Guatemala', 'es': 'Guatemala'},
    'HN': {'en': 'Honduras', 'es': 'Honduras'},
    'SV': {'en': 'El Salvador', 'es': 'El Salvador'},
    'NI': {'en': 'Nicaragua', 'es': 'Nicaragua'},
    'CU': {'en': 'Cuba', 'es': 'Cuba'},
    'CA': {'en': 'Canada', 'es': 'Canadá'},
    'BR': {'en': 'Brazil', 'es': 'Brasil'},
    'AU': {'en': 'Australia', 'es': 'Australia'},
    'NZ': {'en': 'New Zealand', 'es': 'Nueva Zelanda'},
    'JP': {'en': 'Japan', 'es': 'Japón'},
    'CN': {'en': 'China', 'es': 'China'},
    'IN': {'en': 'India', 'es': 'India'},
    'RU': {'en': 'Russia', 'es': 'Rusia'},
    'NL': {'en': 'Netherlands', 'es': 'Países Bajos'},
    'BE': {'en': 'Belgium', 'es': 'Bélgica'},
    'CH': {'en': 'Switzerland', 'es': 'Suiza'},
    'AT': {'en': 'Austria', 'es': 'Austria'},
    'SE': {'en': 'Sweden', 'es': 'Suecia'},
    'NO': {'en': 'Norway', 'es': 'Noruega'},
    'DK': {'en': 'Denmark', 'es': 'Dinamarca'},
    'FI': {'en': 'Finland', 'es': 'Finlandia'},
    'PL': {'en': 'Poland', 'es': 'Polonia'},
    'GR': {'en': 'Greece', 'es': 'Grecia'},
    'IE': {'en': 'Ireland', 'es': 'Irlanda'},
    'CZ': {'en': 'Czech Republic', 'es': 'República Checa'},
    'HU': {'en': 'Hungary', 'es': 'Hungría'},
    'RO': {'en': 'Romania', 'es': 'Rumania'},
    'BG': {'en': 'Bulgaria', 'es': 'Bulgaria'},
    'HR': {'en': 'Croatia', 'es': 'Croacia'},
    'RS': {'en': 'Serbia', 'es': 'Serbia'},
    'SK': {'en': 'Slovakia', 'es': 'Eslovaquia'},
    'SI': {'en': 'Slovenia', 'es': 'Eslovenia'},
    'EE': {'en': 'Estonia', 'es': 'Estonia'},
    'LV': {'en': 'Latvia', 'es': 'Letonia'},
    'LT': {'en': 'Lithuania', 'es': 'Lituania'},
    'IS': {'en': 'Iceland', 'es': 'Islandia'},
    'LU': {'en': 'Luxembourg', 'es': 'Luxemburgo'},
    'MT': {'en': 'Malta', 'es': 'Malta'},
    'CY': {'en': 'Cyprus', 'es': 'Chipre'},
    'TR': {'en': 'Turkey', 'es': 'Turquía'},
    'ZA': {'en': 'South Africa', 'es': 'Sudáfrica'},
    'EG': {'en': 'Egypt', 'es': 'Egipto'},
    'MA': {'en': 'Morocco', 'es': 'Marruecos'},
    'TN': {'en': 'Tunisia', 'es': 'Túnez'},
    'DZ': {'en': 'Algeria', 'es': 'Argelia'},
    'SA': {'en': 'Saudi Arabia', 'es': 'Arabia Saudí'},
    'AE': {'en': 'United Arab Emirates', 'es': 'Emiratos Árabes Unidos'},
    'IL': {'en': 'Israel', 'es': 'Israel'},
    'KR': {'en': 'South Korea', 'es': 'Corea del Sur'},
    'TH': {'en': 'Thailand', 'es': 'Tailandia'},
    'VN': {'en': 'Vietnam', 'es': 'Vietnam'},
    'PH': {'en': 'Philippines', 'es': 'Filipinas'},
    'ID': {'en': 'Indonesia', 'es': 'Indonesia'},
    'MY': {'en': 'Malaysia', 'es': 'Malasia'},
    'SG': {'en': 'Singapore', 'es': 'Singapur'},
}

def normalize_country_name(country_input):
    """
    Normaliza un nombre de país a formato estándar (inglés)
    Acepta: códigos ISO, nombres en inglés, nombres en español
    
    Args:
        country_input: Código ISO, nombre en inglés o español
        
    Returns:
        Tupla (nombre_inglés, código_iso) o (None, None) si no se encuentra
    """
    if not country_input:
        return None, None
    
    country_input = str(country_input).strip()
    
    # Si es un código ISO (2 letras), buscar directamente
    if len(country_input) == 2 and country_input.upper() in COUNTRY_MAPPING:
        code = country_input.upper()
        return COUNTRY_MAPPING[code]['en'], code
    
    # Buscar por código ISO de 3 letras (ESP, USA, etc.)
    if len(country_input) == 3:
        # Mapeo de códigos ISO de 3 letras a 2 letras
        iso3_to_iso2 = {
            'ESP': 'ES', 'USA': 'US', 'GBR': 'GB', 'FRA': 'FR',
            'DEU': 'DE', 'ITA': 'IT', 'PRT': 'PT'
        }
        if country_input.upper() in iso3_to_iso2:
            code = iso3_to_iso2[country_input.upper()]
            return COUNTRY_MAPPING[code]['en'], code
    
    # Buscar por nombre (inglés o español)
    country_input_lower = country_input.lower()
    
    for code, names in COUNTRY_MAPPING.items():
        if (names['en'].lower() == country_input_lower or 
            names['es'].lower() == country_input_lower):
            return names['en'], code
    
    # Búsqueda parcial (por si hay variaciones)
    for code, names in COUNTRY_MAPPING.items():
        if (country_input_lower in names['en'].lower() or 
            names['en'].lower() in country_input_lower or
            country_input_lower in names['es'].lower() or 
            names['es'].lower() in country_input_lower):
            return names['en'], code
    
    # Si no se encuentra, devolver el input original
    return country_input, None

def get_country_variants(country_input):
    """
    Obtiene todas las variantes de un país (inglés, español, código ISO)
    
    Args:
        country_input: Código ISO, nombre en inglés o español
        
    Returns:
        Dict con 'en', 'es', 'code' o None si no se encuentra
    """
    normalized, code = normalize_country_name(country_input)
    
    if not normalized or not code:
        return None
    
    return {
        'en': COUNTRY_MAPPING[code]['en'],
        'es': COUNTRY_MAPPING[code]['es'],
        'code': code
    }

def countries_match(country1, country2):
    """
    Verifica si dos nombres de países se refieren al mismo país
    
    Args:
        country1: Primer país (cualquier formato)
        country2: Segundo país (cualquier formato)
        
    Returns:
        True si son el mismo país, False en caso contrario
    """
    if not country1 or not country2:
        return False
    
    # Normalizar ambos
    norm1, code1 = normalize_country_name(country1)
    norm2, code2 = normalize_country_name(country2)
    
    # Comparar nombres normalizados o códigos
    if norm1 and norm2:
        return norm1.lower() == norm2.lower()
    
    if code1 and code2:
        return code1 == code2
    
    # Comparación directa como fallback
    return str(country1).lower() == str(country2).lower()

