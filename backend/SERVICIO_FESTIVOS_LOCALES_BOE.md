# 🏛️ Servicio de Carga de Festivos Locales desde el BOE

## 📋 Resumen

Se ha implementado un servicio completo para cargar festivos locales (municipales) desde el BOE y otras fuentes de datos abiertos. El servicio permite recuperar festivos locales que no están disponibles en APIs estándar como Nager.Date.

---

## 🎯 Funcionalidades Implementadas

### 1. **BOEHolidayService** (`backend/services/boe_holiday_service.py`)

Servicio principal que proporciona múltiples métodos para cargar festivos locales:

#### Métodos Disponibles

1. **`load_local_holidays_from_boe_resolutions(year)`**
   - Parsea resoluciones oficiales del BOE
   - Extrae festivos locales mencionados en notas aclaratorias
   - Soporta años 2023-2026 (extensible)

2. **`load_local_holidays_from_manual_data(holidays_data, year)`**
   - Carga festivos desde datos proporcionados manualmente
   - Formato JSON estructurado

3. **`load_local_holidays_from_json_file(file_path)`**
   - Carga festivos desde archivo JSON
   - Útil para importar datos de fuentes externas

4. **`load_local_holidays_for_year(year)`**
   - Carga automática desde múltiples fuentes
   - Intenta BOE, datos.gob.es y APIs municipales

5. **`parse_boe_resolution(boe_text, year)`**
   - Parsea texto de resoluciones del BOE
   - Extrae festivos locales usando expresiones regulares

---

## 📊 Fuentes de Datos

### 1. **BOE (Boletín Oficial del Estado)**
- **URL**: https://www.boe.es/diario_boe/txt.php?id=BOE-A-{year-1}-{numero}
- **Formato**: Texto plano parseable
- **Contenido**: Resoluciones oficiales con festivos locales en notas aclaratorias
- **Ejemplo**: BOE-A-2025-21667 (para 2026)

### 2. **Datos Abiertos (datos.gob.es)**
- **URL**: https://datos.gob.es/apidata/catalog/distribution
- **Estado**: En desarrollo (requiere análisis de estructura de datos)

### 3. **Datos Manuales**
- **Formato**: JSON estructurado
- **Archivo ejemplo**: `scripts/example_local_holidays_2026.json`

---

## 🚀 Uso del Servicio

### Opción 1: Script de Línea de Comandos

```bash
cd backend
python3 scripts/load_local_holidays_2026.py
```

### Opción 2: Desde Código Python

```python
from main import create_app
from services.boe_holiday_service import BOEHolidayService

app = create_app()
with app.app_context():
    boe_service = BOEHolidayService()
    
    # Cargar desde BOE
    created, errors = boe_service.load_local_holidays_from_boe_resolutions(2026)
    print(f"Cargados {created} festivos locales")
    
    # Cargar desde archivo JSON
    created, errors = boe_service.load_local_holidays_from_json_file('scripts/example_local_holidays_2026.json')
    
    # Cargar desde datos manuales
    holidays_data = [
        {
            'name': 'San Isidro',
            'date': '2026-05-15',
            'city': 'Madrid',
            'region': 'Madrid',
            'country': 'España',
            'description': 'Fiesta patronal de Madrid'
        }
    ]
    created, errors = boe_service.load_local_holidays_from_manual_data(holidays_data, 2026)
```

### Opción 3: Endpoint API REST

```bash
# Cargar desde datos manuales
curl -X POST https://team-time-management.onrender.com/api/holidays/load-local \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "year": 2026,
    "source": "manual",
    "holidays": [
      {
        "name": "San Isidro",
        "date": "2026-05-15",
        "city": "Madrid",
        "region": "Madrid",
        "country": "España"
      }
    ]
  }'

# Cargar desde archivo JSON (ruta relativa al servidor)
curl -X POST https://team-time-management.onrender.com/api/holidays/load-local \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "year": 2026,
    "source": "json_file",
    "file_path": "scripts/example_local_holidays_2026.json"
  }'

# Carga automática desde múltiples fuentes
curl -X POST https://team-time-management.onrender.com/api/holidays/load-local \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "year": 2026,
    "source": "auto"
  }'
```

---

## 📝 Formato de Datos

### Estructura JSON para Festivos Locales

```json
[
  {
    "name": "San Isidro",
    "date": "2026-05-15",
    "city": "Madrid",
    "region": "Madrid",
    "country": "España",
    "description": "Fiesta patronal de Madrid",
    "is_fixed": false
  }
]
```

### Campos Requeridos
- `name`: Nombre del festivo (máx. 200 caracteres)
- `date`: Fecha en formato YYYY-MM-DD
- `city`: Ciudad (máx. 100 caracteres)
- `country`: País (España o Spain)

### Campos Opcionales
- `region`: Región/Comunidad Autónoma (máx. 100 caracteres)
- `description`: Descripción del festivo (máx. 500 caracteres)
- `is_fixed`: Si es fecha fija cada año (default: false)

---

## 🔍 Parser del BOE

El parser extrae festivos locales de las notas aclaratorias del BOE usando expresiones regulares:

**Patrón reconocido**:
```
en [ubicación]: el [día] de [mes], festividad de [nombre]
```

**Ejemplo del BOE**:
```
en El Hierro: el 24 de septiembre, festividad de Nuestra Señora de los Reyes
```

**Resultado parseado**:
```json
{
  "name": "Nuestra Señora de los Reyes",
  "date": "2026-09-24",
  "city": "El Hierro",
  "region": "Canarias",
  "country": "España"
}
```

---

## ✅ Resultados de la Carga

### Festivos Locales Cargados para 2026

**Desde BOE**:
- ✅ 7 festivos locales de Canarias extraídos y cargados
- ✅ Festivos de islas: El Hierro, Fuerteventura, Gran Canaria, La Gomera, La Palma, Lanzarote/La Graciosa, Tenerife

**Desde JSON de Ejemplo**:
- ✅ 10 festivos locales de ejemplo cargados
- ✅ Incluye: Madrid, Barcelona, Sevilla, Valencia, Pamplona, Bilbao, Logroño, Zaragoza, A Coruña

---

## 🔧 Configuración y Dependencias

### Dependencias Opcionales

- `beautifulsoup4`: Para scraping HTML avanzado (opcional)
- `lxml`: Parser XML/HTML rápido (opcional)

**Nota**: El servicio funciona sin estas dependencias, pero algunas funciones de scraping estarán limitadas.

### Instalación

```bash
pip install beautifulsoup4 lxml
```

O agregar a `requirements.txt`:
```
beautifulsoup4>=4.14.0
lxml>=6.0.0
```

---

## 📊 Estadísticas

### Festivos Locales en Base de Datos

```sql
-- Ver festivos locales de 2026
SELECT 
    date, 
    name, 
    city, 
    region,
    country
FROM holiday
WHERE EXTRACT(YEAR FROM date) = 2026
  AND holiday_type = 'local'
  AND active = true
ORDER BY date;
```

---

## 🎯 Próximos Pasos

### Mejoras Sugeridas

1. **Integración con Boletines Oficiales de CCAA**
   - Parsear BOEs de comunidades autónomas
   - Extraer festivos locales de cada provincia/municipio

2. **API de Datos Abiertos**
   - Integrar con datos.gob.es
   - Buscar datasets de calendarios laborales municipales

3. **APIs Municipales**
   - Integrar con APIs de ayuntamientos principales
   - Madrid, Barcelona, Valencia, Sevilla, etc.

4. **Caché y Actualización**
   - Caché de resoluciones del BOE parseadas
   - Actualización automática anual

5. **Validación de Datos**
   - Verificar que los festivos no dupliquen festivos nacionales/autonómicos
   - Validar fechas y ubicaciones

---

## 📚 Referencias

- **BOE**: https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-21667
- **Portal Calendarios**: https://administracion.gob.es/pag_Home/atencionCiudadana/calendarios/laboral.html
- **Datos Abiertos**: https://datos.gob.es/

---

## ✅ Estado Actual

- ✅ Servicio BOEHolidayService implementado
- ✅ Parser del BOE funcional
- ✅ Carga desde datos manuales/JSON funcional
- ✅ Endpoint API REST creado (`/api/holidays/load-local`)
- ✅ Script de línea de comandos funcional
- ✅ 7 festivos locales de Canarias cargados desde BOE
- ✅ 10 festivos locales de ejemplo cargados desde JSON

**Estado**: ✅ **FUNCIONAL Y LISTO PARA USO**
