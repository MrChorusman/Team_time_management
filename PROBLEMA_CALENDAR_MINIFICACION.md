# Problema: Error de Inicialización en CalendarTableView durante Minificación

## 1. Contexto del Proyecto

**Aplicación**: Team Time Management - Sistema de gestión de tiempo y equipos  
**Tipo**: Aplicación web full-stack (React + Flask)  
**Entorno**: Producción en Vercel (frontend) y Render (backend)

## 2. Funcionalidad que Estamos Implementando

Estamos implementando un **calendario tipo tabla/spreadsheet** para visualizar las actividades de los empleados. La funcionalidad incluye:

### Características Principales:
- **Vista mensual y anual**: Los usuarios pueden alternar entre ver un mes específico o todo el año
- **Estructura tipo tabla**:
  - **Filas**: Empleados
  - **Columnas**: Equipo | Empleado | Vac (Vacaciones) | Aus (Ausencias) | Días 1-31
- **Marcado de actividades**: Los usuarios pueden hacer clic derecho en cualquier día para marcar:
  - Vacaciones (V)
  - Ausencias/Bajas (A)
  - Días Libres con horas (HLD -2h)
  - Guardias con horas (G +4h)
  - Formación con horas (F -2h)
  - Otros (C)
- **Festivos**: El calendario muestra festivos según la ubicación geográfica del empleado (nacionales, regionales, locales)
- **Fines de semana**: Marcados visualmente con fondo gris
- **Resumen mensual**: Muestra totales de vacaciones y ausencias por empleado

### Componentes Involucrados:
- `CalendarTableView.jsx`: Componente principal que renderiza la tabla del calendario
- `calendarHelpers.js`: Archivo con funciones helper para cálculos y formateo
- `AdminCalendarsPage.jsx`: Página de administración que usa `CalendarTableView`
- `CalendarPage.jsx`: Página de empleados que usa `CalendarTableView`

## 3. Información Disponible

### 3.1 Estructura de Datos

**Empleados** (`employees`):
```javascript
{
  id: number,
  full_name: string,
  team_name: string,
  country: string,      // Código ISO (ej: "ESP")
  region: string,
  city: string,
  location: {           // Objeto con country, region, city
    country: string,
    region: string,
    city: string
  }
}
```

**Actividades** (`activities`):
```javascript
[
  {
    id: number,
    employee_id: number,
    date: string,              // ISO format: "2025-11-15"
    start_date: string,        // Para rangos
    end_date: string,          // Para rangos
    activity_type: string,     // 'V', 'A', 'HLD', 'G', 'F', 'C'
    type: string,             // 'vacation', 'absence', 'guard', etc.
    hours: number,            // Para actividades con horas
    description: string
  }
]
```

**Festivos** (`holidays`):
```javascript
[
  {
    id: number,
    date: string,              // ISO format: "2025-11-01"
    name: string,             // "Todos los Santos"
    country: string,          // Nombre completo: "España" (no código ISO)
    region: string,
    city: string,
    holiday_type: string      // 'national', 'regional', 'local'
  }
]
```

### 3.2 Mapeo de Códigos ISO a Nombres de Países

Necesitamos convertir códigos ISO de empleados (ej: "ESP") a nombres completos de países (ej: "España") para hacer match con los festivos:

```javascript
const ISO_TO_COUNTRY_NAME = {
  'ESP': 'España',
  'ES': 'España',
  'USA': 'United States',
  'US': 'United States',
  'GBR': 'United Kingdom',
  'GB': 'United Kingdom',
  // ... más países
}
```

## 4. Soporte de la Información

### 4.1 Frontend
- **Framework**: React 18 con Vite
- **Lenguaje**: JavaScript (ES6+)
- **Build Tool**: Vite 5.x
- **Minificación**: esbuild (por defecto en Vite)
- **Deployment**: Vercel (producción)

### 4.2 Backend
- **Framework**: Flask (Python)
- **Base de Datos**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **Deployment**: Render

### 4.3 Archivos Relevantes

**Frontend**:
- `frontend/src/components/calendar/CalendarTableView.jsx` (~500 líneas)
- `frontend/src/components/calendar/calendarHelpers.js` (~290 líneas)
- `frontend/src/pages/admin/AdminCalendarsPage.jsx`
- `frontend/src/pages/CalendarPage.jsx`
- `frontend/vite.config.js`

**Backend**:
- `backend/services/calendar_service.py`
- `backend/models/calendar_activity.py`
- `backend/app/calendar.py`

## 5. Tecnologías Utilizadas

### 5.1 Stack Principal
- **React 18**: Biblioteca UI con hooks (`useState`, `useEffect`, `useRef`)
- **Vite 5**: Build tool y bundler
- **esbuild**: Minificador por defecto de Vite
- **Tailwind CSS**: Estilos
- **Lucide React**: Iconos

### 5.2 Configuración de Vite

```javascript
// vite.config.js
export default defineConfig({
  build: {
    minify: 'esbuild',  // Minificador por defecto
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Separar CalendarTableView en chunk propio
          if (id.includes('CalendarTableView')) {
            return 'calendar'
          }
          // ... otros chunks
        }
      }
    }
  }
})
```

## 6. Problema Encontrado

### 6.1 Error en Producción

**Error**: `ReferenceError: Cannot access '_' before initialization`

**Ubicación**: 
- Ocurre en producción (Vercel) después de la minificación
- No ocurre en desarrollo local (sin minificación)
- El error aparece en el archivo minificado: `index-BaQqSGB4.js:7:258592`

**Stack Trace**:
```
ReferenceError: Cannot access '_' before initialization
    at Ml (https://team-time-management.vercel.app/assets/index-BaQqSGB4.js:7:258592)
    at nu (https://team-time-management.vercel.app/assets/vendor-BrGaYqd6.js:38:17253)
    at oh (https://team-time-management.vercel.app/assets/vendor-BrGaYqd6.js:40:44461)
    ...
```

### 6.2 Síntomas

1. **En desarrollo**: Todo funciona correctamente
2. **En producción**: La página del calendario no carga, error en consola
3. **El error ocurre durante el renderizado inicial** del componente `CalendarTableView`
4. **El símbolo `_`** parece ser una variable minificada que se está usando antes de ser inicializada

### 6.3 Código Problemático

El componente `CalendarTableView` importa funciones helper desde `calendarHelpers.js`:

```javascript
// CalendarTableView.jsx
import {
  getDaysInMonth,
  getMonthsInYear,
  isHolidayHelper,
  getActivityForDayHelper,
  getActivityCodeHelper,
  getCellBackgroundColorHelper,
  getCellTextColorHelper,
  getMonthSummaryHelper,
  getMonthHolidaysHelper,
  ISO_TO_COUNTRY_NAME
} from './calendarHelpers'
```

Y las usa dentro de una IIFE (Immediately Invoked Function Expression) en el render:

```javascript
{(() => {
  let calculatedMonths = []
  try {
    if (viewMode === 'annual') {
      calculatedMonths = getMonthsInYear(currentMonth) || []
    } else {
      const monthDays = getDaysInMonth(currentMonth)
      const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
      calculatedMonths = [{ date: currentMonth, name: monthName, days: monthDays }]
    }
  } catch (error) {
    console.error('Error calculando meses:', error)
    calculatedMonths = []
  }
  
  return calculatedMonths && Array.isArray(calculatedMonths) && calculatedMonths.length > 0 ? (
    calculatedMonths.map((month) => (
      // ... renderizado de la tabla
    ))
  ) : (
    <div>No hay datos</div>
  )
})()}
```

### 6.4 Funciones Helper en calendarHelpers.js

Todas las funciones están exportadas como `export function`:

```javascript
// calendarHelpers.js
export function getDaysInMonth(date) { /* ... */ }
export function getMonthsInYear(date) { 
  // ... 
  days: getDaysInMonth(monthDate)  // Llama a otra función exportada
}
export function isHolidayHelper(dateString, employeeLocation, holidays) {
  // Usa ISO_TO_COUNTRY_NAME
  const employeeCountry = ISO_TO_COUNTRY_NAME[employeeCountryCode] || employeeCountryCode
  // ...
}
// ... más funciones
```

## 7. Intentos de Solución Realizados

### 7.1 Intentos Previos (sin éxito)

1. **Mover funciones helper a archivo separado**
   - ✅ Separamos todas las funciones a `calendarHelpers.js`
   - ❌ El error persiste

2. **Eliminar funciones duplicadas**
   - ✅ Eliminamos todas las funciones duplicadas en `CalendarTableView.jsx`
   - ❌ El error persiste

3. **Eliminar `useCallback`**
   - ✅ Eliminamos todos los `useCallback` hooks
   - ❌ El error persiste

4. **Cambiar `export const` a `export function`**
   - ✅ Cambiamos todas las funciones a `export function` para mejor hoisting
   - ❌ El error persiste

5. **Ajustar configuración de Vite**
   - ✅ Intentamos separar `CalendarTableView` en chunk propio con `manualChunks`
   - ✅ Cambiamos de `terser` a `esbuild` (terser no estaba instalado)
   - ❌ El error persiste

6. **Usar IIFE en el render**
   - ✅ Movimos el cálculo de meses dentro de una IIFE
   - ✅ Añadimos try-catch alrededor del cálculo
   - ❌ El error persiste

### 7.2 Análisis del Problema

El error `Cannot access '_' before initialization` sugiere:

1. **Problema de hoisting durante minificación**: esbuild está reorganizando el código de manera que una variable se usa antes de ser inicializada
2. **Dependencia circular**: Aunque no es evidente, podría haber una dependencia circular entre las funciones helper
3. **Problema con `export function`**: Aunque las funciones `function` tienen mejor hoisting que `const`, podría haber un problema con cómo esbuild las procesa
4. **Problema con la IIFE**: La función inmediatamente invocada podría estar causando problemas de scope durante la minificación

## 8. Preguntas para la Comunidad

1. **¿Es un problema conocido de esbuild/Vite?**
   - ¿Alguien ha experimentado errores similares con `export function` y minificación?
   - ¿Hay alguna configuración específica de esbuild que pueda resolver esto?

2. **¿Hay una mejor forma de estructurar las funciones helper?**
   - ¿Deberíamos usar un objeto con todas las funciones en lugar de exports individuales?
   - ¿Deberíamos usar `export default` con un objeto?

3. **¿Hay una alternativa a la IIFE en el render?**
   - ¿Deberíamos usar `useMemo` o `useEffect` para calcular los meses?
   - ¿Hay una forma más segura de hacer cálculos en el render que no cause problemas de minificación?

4. **¿Deberíamos desactivar la minificación para este componente específico?**
   - ¿Es posible excluir solo `CalendarTableView` de la minificación?
   - ¿Cuáles son las implicaciones de rendimiento?

5. **¿Hay alguna configuración de Vite/esbuild que pueda ayudar?**
   - ¿Algún flag o opción que preserve mejor el orden de inicialización?

## 9. Información Adicional

### 9.1 Versiones de Dependencias

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "vite": "^5.0.0",
  "@vitejs/plugin-react": "^4.2.0"
}
```

### 9.2 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/
│   │   └── calendar/
│   │       ├── CalendarTableView.jsx
│   │       ├── calendarHelpers.js
│   │       ├── ContextMenu.jsx
│   │       └── ActivityModal.jsx
│   └── pages/
│       ├── admin/
│       │   └── AdminCalendarsPage.jsx
│       └── CalendarPage.jsx
└── vite.config.js
```

### 9.3 Comandos de Build

```bash
# Desarrollo (sin minificación)
npm run dev

# Producción (con minificación)
npm run build
```

## 10. Repositorio y Enlaces

- **Repositorio**: [GitHub - Team Time Management](https://github.com/MrChorusman/Team_time_management)
- **Deployment Frontend**: Vercel
- **Deployment Backend**: Render
- **Base de Datos**: Supabase (PostgreSQL)

## 11. Contacto y Contribuciones

Si tienes alguna sugerencia o solución, por favor:
1. Abre un issue en el repositorio
2. Proporciona detalles sobre la solución propuesta
3. Incluye ejemplos de código si es posible

---

**Última actualización**: 14 de noviembre de 2025  
**Estado**: Problema activo, buscando soluciones alternativas

