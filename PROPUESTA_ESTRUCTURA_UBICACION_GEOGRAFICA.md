# 📍 Propuesta: Estructura de Ubicación Geográfica y Festivos

## **FECHA**: 31/10/2025
## **AUTOR**: Análisis técnico del sistema

---

## 🔍 **ANÁLISIS DE LA SITUACIÓN ACTUAL**

### **Estado de Base de Datos**

#### Tablas Relacionales Disponibles:
```
countries (188 países)
├── id, name, code, is_active
└── Ejemplos: España (ES), México (MX), Argentina (AR)

autonomous_communities (74 comunidades)
├── id, name, country_id
└── Incluye: España (17 CCAA), Brasil, Francia, Argentina, Chile, Venezuela

provinces (52 provincias españolas)
├── id, name, autonomous_community_id
└── Ejemplos: Madrid, Barcelona, Valencia, Sevilla

cities (201 ciudades)
├── id, name, autonomous_community_id, postal_code
└── **IMPORTANTE**: Cities apunta a CA, NO a Province
```

### **Problema Actual**

#### 1. **Modelo Employee usa TEXT en lugar de IDs:**
```python
# backend/models/employee.py (ACTUAL)
country = db.Column(db.String(100))   # ❌ Texto libre
region = db.Column(db.String(100))    # ❌ Texto libre
city = db.Column(db.String(100))      # ❌ Texto libre
```

**Problemas:**
- ❌ Sin integridad referencial
- ❌ Posibles inconsistencias: "España" vs "España " vs "ESPAÑA"
- ❌ No aprovecha estructura relacional
- ❌ Difícil de mantener

#### 2. **Frontend con datos hardcodeados:**
```javascript
// frontend/src/pages/employee/EmployeeRegisterPage.jsx
const regions = {
  'ES': ['Madrid', 'Cataluña', 'Andalucía', 'Valencia', 'País Vasco'], // ❌ Solo 5 de 17
  'MX': ['Ciudad de México', 'Jalisco', ...],
  // ...
}
```

**Problemas:**
- ❌ Solo 5 CCAA de España (faltan 12)
- ❌ Datos duplicados (BD vs Frontend)
- ❌ Difícil de actualizar
- ❌ No escala para otros países

#### 3. **Modelo Holiday también usa TEXT:**
```python
# backend/models/holiday.py (ACTUAL)
country = db.Column(db.String(100))   # ❌ Texto libre
region = db.Column(db.String(100))    # ❌ Texto libre
city = db.Column(db.String(100))      # ❌ Texto libre
```

---

## 🎯 **PROPUESTA DE SOLUCIÓN**

### **Opción A: Mantener TEXT (Más Rápida)** ⭐ **RECOMENDADA para MVP**

**Ventajas:**
- ✅ No requiere migración de BD
- ✅ Compatible con holidays existentes
- ✅ Rápida implementación
- ✅ Funciona con la estructura actual

**Cambios necesarios:**

#### 1. **Backend: Crear endpoints para ubicación**

```python
# backend/app/locations.py (NUEVO)

from flask import Blueprint, jsonify, request
from models.country import Country
from models.autonomous_community import AutonomousCommunity
from models.province import Province
from models.city import City

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('/countries', methods=['GET'])
def get_countries():
    """Lista todos los países activos"""
    countries = Country.query.filter_by(is_active=True).order_by(Country.name).all()
    return jsonify({
        'success': True,
        'countries': [{'id': c.id, 'name': c.name, 'code': c.code} for c in countries]
    })

@locations_bp.route('/countries/<int:country_id>/autonomous-communities', methods=['GET'])
def get_autonomous_communities(country_id):
    """Lista comunidades autónomas de un país"""
    communities = AutonomousCommunity.query.filter_by(
        country_id=country_id
    ).order_by(AutonomousCommunity.name).all()
    
    return jsonify({
        'success': True,
        'communities': [{'id': c.id, 'name': c.name} for c in communities]
    })

@locations_bp.route('/autonomous-communities/<int:community_id>/provinces', methods=['GET'])
def get_provinces(community_id):
    """Lista provincias de una comunidad autónoma"""
    provinces = Province.query.filter_by(
        autonomous_community_id=community_id
    ).order_by(Province.name).all()
    
    return jsonify({
        'success': True,
        'provinces': [{'id': p.id, 'name': p.name} for p in provinces]
    })

@locations_bp.route('/autonomous-communities/<int:community_id>/cities', methods=['GET'])
def get_cities(community_id):
    """Lista ciudades de una comunidad autónoma"""
    cities = City.query.filter_by(
        autonomous_community_id=community_id,
        is_active=True
    ).order_by(City.name).all()
    
    return jsonify({
        'success': True,
        'cities': [{'id': c.id, 'name': c.name, 'postal_code': c.postal_code} for c in cities]
    })
```

#### 2. **Backend: Crear modelos si no existen**

```python
# backend/models/country.py (si no existe)
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

# backend/models/autonomous_community.py (si no existe)
class AutonomousCommunity(db.Model):
    __tablename__ = 'autonomous_communities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))

# backend/models/province.py (si no existe)
class Province(db.Model):
    __tablename__ = 'provinces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    autonomous_community_id = db.Column(db.Integer, db.ForeignKey('autonomous_communities.id'))

# backend/models/city.py (si no existe)
class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    autonomous_community_id = db.Column(db.Integer, db.ForeignKey('autonomous_communities.id'))
    postal_code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
```

#### 3. **Frontend: Cascading Selects Dinámicos**

```javascript
// frontend/src/pages/employee/EmployeeRegisterPage.jsx

const [countries, setCountries] = useState([])
const [communities, setCommunities] = useState([])
const [cities, setCities] = useState([])

const [selectedCountry, setSelectedCountry] = useState(null)
const [selectedCommunity, setSelectedCommunity] = useState(null)

// Cargar países al montar
useEffect(() => {
  const loadCountries = async () => {
    try {
      const response = await apiClient.get('/locations/countries')
      setCountries(response.data.countries)
    } catch (error) {
      console.error('Error cargando países:', error)
    }
  }
  loadCountries()
}, [])

// Cargar comunidades cuando se selecciona país
useEffect(() => {
  if (selectedCountry) {
    const loadCommunities = async () => {
      try {
        const response = await apiClient.get(
          `/locations/countries/${selectedCountry}/autonomous-communities`
        )
        setCommunities(response.data.communities)
        setCities([]) // Reset cities
        setSelectedCommunity(null)
      } catch (error) {
        console.error('Error cargando comunidades:', error)
      }
    }
    loadCommunities()
  }
}, [selectedCountry])

// Cargar ciudades cuando se selecciona comunidad
useEffect(() => {
  if (selectedCommunity) {
    const loadCities = async () => {
      try {
        const response = await apiClient.get(
          `/locations/autonomous-communities/${selectedCommunity}/cities`
        )
        setCities(response.data.cities)
      } catch (error) {
        console.error('Error cargando ciudades:', error)
      }
    }
    loadCities()
  }
}, [selectedCommunity])
```

#### 4. **Frontend: Formulario con Cascading Selects**

```jsx
{/* País */}
<div>
  <Label htmlFor="country">País *</Label>
  <Select
    value={selectedCountry}
    onValueChange={(value) => {
      setSelectedCountry(value)
      setValue('country', countries.find(c => c.id === parseInt(value))?.name)
    }}
  >
    <SelectTrigger>
      <SelectValue placeholder="Selecciona país" />
    </SelectTrigger>
    <SelectContent>
      {countries.map((country) => (
        <SelectItem key={country.id} value={country.id.toString()}>
          {country.name}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
</div>

{/* Comunidad Autónoma / Región */}
<div>
  <Label htmlFor="region">Comunidad Autónoma / Región *</Label>
  <Select
    value={selectedCommunity}
    onValueChange={(value) => {
      setSelectedCommunity(value)
      setValue('region', communities.find(c => c.id === parseInt(value))?.name)
    }}
    disabled={!selectedCountry || communities.length === 0}
  >
    <SelectTrigger>
      <SelectValue placeholder={
        !selectedCountry 
          ? "Primero selecciona un país" 
          : communities.length === 0 
          ? "No hay regiones disponibles"
          : "Selecciona comunidad/región"
      } />
    </SelectTrigger>
    <SelectContent>
      {communities.map((community) => (
        <SelectItem key={community.id} value={community.id.toString()}>
          {community.name}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
</div>

{/* Ciudad */}
<div>
  <Label htmlFor="city">Ciudad</Label>
  <Select
    value={watch('city')}
    onValueChange={(value) => setValue('city', value)}
    disabled={!selectedCommunity || cities.length === 0}
  >
    <SelectTrigger>
      <SelectValue placeholder={
        !selectedCommunity 
          ? "Primero selecciona una región" 
          : cities.length === 0
          ? "No hay ciudades disponibles"
          : "Selecciona ciudad (opcional)"
      } />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="">Ninguna (usar comunidad)</SelectItem>
      {cities.map((city) => (
        <SelectItem key={city.id} value={city.name}>
          {city.name} {city.postal_code ? `(${city.postal_code})` : ''}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
  <p className="text-sm text-muted-foreground mt-1">
    Opcional: Solo si necesitas festivos locales específicos
  </p>
</div>
```

---

### **Opción B: Migrar a IDs (Más Robusta)** 

**Solo si hay tiempo y recursos para hacer migración**

```python
# backend/models/employee.py (NUEVO)
class Employee(db.Model):
    # ... otros campos ...
    
    # Ubicación geográfica (con IDs)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    autonomous_community_id = db.Column(db.Integer, db.ForeignKey('autonomous_communities.id'))
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    
    # Relaciones
    country_rel = db.relationship('Country', foreign_keys=[country_id])
    community_rel = db.relationship('AutonomousCommunity', foreign_keys=[autonomous_community_id])
    province_rel = db.relationship('Province', foreign_keys=[province_id])
    city_rel = db.relationship('City', foreign_keys=[city_id])
    
    @property
    def country(self):
        return self.country_rel.name if self.country_rel else None
    
    @property
    def region(self):
        return self.community_rel.name if self.community_rel else None
    
    @property
    def city(self):
        return self.city_rel.name if self.city_rel else None
```

**Ventajas:**
- ✅ Integridad referencial
- ✅ Más robusto
- ✅ Escalable

**Desventajas:**
- ❌ Requiere migración de datos existentes
- ❌ Más complejo
- ❌ Necesita script de migración

---

## 🎉 **GESTIÓN DE FESTIVOS**

### **Cómo funcionan los festivos con la estructura propuesta**

#### Jerarquía de Festivos:
```
1. Nacional    → Solo país
2. Regional    → País + Comunidad Autónoma
3. Local       → País + Comunidad Autónoma + Ciudad
```

#### Ejemplo de Festivos en España:
```
🇪🇸 España
│
├── 📅 Festivos NACIONALES (aplican a todos)
│   ├── 1 enero - Año Nuevo
│   ├── 6 enero - Reyes Magos
│   ├── 1 mayo - Día del Trabajo
│   └── 25 diciembre - Navidad
│
├── 🏛️ Festivos REGIONALES (solo una CA)
│   ├── Madrid → 2 mayo - Día de la Comunidad
│   ├── Cataluña → 11 sept - Diada Nacional
│   └── Andalucía → 28 febrero - Día de Andalucía
│
└── 🏙️ Festivos LOCALES (solo una ciudad)
    ├── Madrid (ciudad) → 15 mayo - San Isidro
    └── Barcelona → 24 sept - La Mercè
```

#### Lógica de is_holiday() (ACTUAL - ya funciona):
```python
def is_holiday(self, target_date):
    holidays = Holiday.query.filter(
        Holiday.date == target_date,
        Holiday.country == self.country  # ✅ Compara texto
    ).filter(
        (Holiday.region.is_(None)) |           # Festivo nacional
        (Holiday.region == self.region) |      # Festivo regional
        (Holiday.city == self.city)            # Festivo local
    ).first()
    
    return holidays is not None
```

**Ejemplo práctico:**

```
Empleado en Barcelona, Cataluña, España:
- country: "España"
- region: "Cataluña"
- city: "Barcelona"

Festivos que recibirá:
✅ Todos los nacionales de España (country = "España", region = NULL)
✅ Todos los de Cataluña (country = "España", region = "Cataluña")
✅ Todos los de Barcelona (country = "España", city = "Barcelona")

Festivos que NO recibirá:
❌ Festivos de Madrid (region = "Madrid")
❌ Festivos de Valencia (region = "Valencia")
```

---

## 📋 **FLUJO DE REGISTRO RECOMENDADO**

### **Paso a Paso en el Formulario:**

```
1. Usuario selecciona PAÍS
   └─> Se cargan dinámicamente las COMUNIDADES AUTÓNOMAS de ese país

2. Usuario selecciona COMUNIDAD AUTÓNOMA
   └─> Se cargan dinámicamente las CIUDADES de esa comunidad

3. Usuario selecciona CIUDAD (opcional)
   └─> Solo si necesita festivos locales específicos
   
4. Al guardar:
   └─> Se guarda el NOMBRE (texto) de cada nivel en Employee
       - country: "España"
       - region: "Cataluña"
       - city: "Barcelona" (o NULL si no seleccionó)
```

### **Ventajas de este flujo:**

✅ **Para el Usuario:**
- No necesita escribir, solo seleccionar (evita typos)
- Ve solo opciones válidas
- Interfaz intuitiva con cascading selects
- Feedback visual claro

✅ **Para el Sistema:**
- Datos consistentes (siempre desde la BD)
- Fácil de mantener (un solo lugar para actualizar)
- Escalable (agregar país nuevo = agregar a BD)
- Compatible con festivos existentes

✅ **Para los Festivos:**
- La lógica actual (text matching) sigue funcionando
- Admin puede crear festivos con los mismos nombres
- Sistema reconoce automáticamente qué festivos aplican

---

## 🚀 **PLAN DE IMPLEMENTACIÓN**

### **Fase 1: Backend API (2-3 horas)**
1. ✅ Crear modelos de ubicación (Country, AutonomousCommunity, Province, City)
2. ✅ Crear endpoints `/api/locations/*`
3. ✅ Probar endpoints con Supabase

### **Fase 2: Frontend Cascading Selects (3-4 horas)**
1. ✅ Reemplazar datos hardcodeados
2. ✅ Implementar cascading selects
3. ✅ Agregar loading states
4. ✅ Mejorar UX con placeholders dinámicos

### **Fase 3: Testing (1-2 horas)**
1. ✅ Probar con España (17 CCAA, 52 provincias, 201 ciudades)
2. ✅ Probar con otros países
3. ✅ Verificar que festivos siguen funcionando

### **Fase 4: Documentación (30 min)**
1. ✅ Documentar estructura de ubicación
2. ✅ Documentar cómo agregar nuevo país
3. ✅ Documentar jerarquía de festivos

---

## 📊 **COMPARATIVA DE OPCIONES**

| Aspecto | Opción A (TEXT) | Opción B (IDs) |
|---------|-----------------|----------------|
| **Tiempo de implementación** | 6-9 horas | 15-20 horas |
| **Migración necesaria** | ❌ No | ✅ Sí |
| **Compatibilidad con Holidays** | ✅ Total | ⚠️ Requiere adaptación |
| **Integridad referencial** | ⚠️ Baja | ✅ Alta |
| **Facilidad de mantenimiento** | ✅ Alta | ✅ Muy Alta |
| **Riesgo** | 🟢 Bajo | 🟡 Medio |
| **Escalabilidad** | ✅ Buena | ✅ Excelente |

---

## ✅ **RECOMENDACIÓN FINAL**

### **Para MVP/Producción inmediata → OPCIÓN A (TEXT)** ⭐

**Razones:**
1. ✅ Rápida implementación (1 día)
2. ✅ Sin migración de datos
3. ✅ Compatible con sistema actual de festivos
4. ✅ Mejora inmediata (de 5 a 74 CCAA)
5. ✅ Bajo riesgo

**Mejoras inmediatas:**
- Todos los 188 países disponibles
- Las 74 comunidades autónomas (no solo 5)
- 201 ciudades con código postal
- Datos siempre actualizados desde BD
- Cascading selects intuitivos

### **Para Refactorización futura → OPCIÓN B (IDs)**

**Cuándo implementarla:**
- Después de estabilizar sistema actual
- Cuando haya tiempo para migración
- Si se detectan problemas de consistencia
- Para agregar features avanzadas

---

**Preparado por**: Claude (Cursor AI)  
**Fecha**: 31 de Octubre, 2025  
**Estado**: ✅ Listo para implementación


