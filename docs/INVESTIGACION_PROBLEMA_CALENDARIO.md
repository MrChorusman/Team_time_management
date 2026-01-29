# Investigación del Problema de Renderizado del Calendario

## Fecha
29 de enero de 2026

## Problema Identificado
El calendario no se renderiza correctamente en producción, mostrando un error en la consola del navegador:
```
ReferenceError: Cannot access 'oe' before initialization
```

## Análisis del Problema

### Síntomas
1. La página del calendario carga pero no muestra contenido
2. Las peticiones API a `/api/calendar` responden correctamente (200 OK)
3. Error en consola: `ReferenceError: Cannot access 'oe' before initialization`
4. El error ocurre en el código minificado de producción

### Causa Raíz
El problema está relacionado con la inicialización del módulo `calendarHelpers.js`:

1. **Problema de inicialización circular/hoisting**: El módulo `calendarHelpers` se está usando antes de estar completamente inicializado, especialmente cuando se minifica el código para producción.

2. **Uso prematuro en `useMemo`**: El componente `CalendarTableView` usa `calendarHelpers` dentro de un `useMemo` que se ejecuta inmediatamente al montar el componente, antes de que el módulo esté completamente cargado.

3. **Falta de validaciones**: No había validaciones para verificar que `calendarHelpers` y sus funciones estuvieran disponibles antes de usarlas.

## Soluciones Implementadas

### 1. Validaciones de Inicialización en CalendarTableView
Se agregaron validaciones en todas las llamadas a `calendarHelpers` para verificar que el módulo y sus funciones estén disponibles antes de usarlas:

```javascript
// Ejemplo de validación agregada
if (calendarHelpers && typeof calendarHelpers.getMonthsInYear !== 'function') {
  // Usar valores por defecto o fallback
}
```

### 2. Fallback en useMemo
Se agregó un fallback en el `useMemo` que calcula los meses para evitar errores cuando `calendarHelpers` no está disponible:

```javascript
const calculatedMonths = useMemo(() => {
  if (!calendarHelpers || typeof calendarHelpers.getMonthsInYear !== 'function') {
    // Retornar estructura básica para evitar errores
    return fallbackMonths
  }
  // ... resto del código
}, [viewMode, currentMonth])
```

### 3. Validaciones en Todas las Llamadas
Se agregaron validaciones en todas las ubicaciones donde se usa `calendarHelpers`:
- `getMonthSummaryHelper`
- `getDaysInMonth`
- `getActivityForDayHelper`
- `isHolidayHelper`
- `getCellBackgroundColorHelper`
- `getCellTextColorHelper`
- `getActivityCodeHelper`
- `getMonthHolidaysHelper`
- `doesHolidayApplyToLocation`

### 4. Exportación Mejorada de calendarHelpers
Se mejoró la exportación del módulo usando `Object.freeze` para asegurar que el objeto esté completamente inicializado:

```javascript
const calendarHelpers = Object.freeze({
  // ... todas las funciones
})

export default calendarHelpers
```

### 5. Validación en CalendarPage
Se agregó una validación adicional en `CalendarPage` para no renderizar `CalendarTableView` si `calendarData` es null:

```javascript
{calendarData ? (
  <CalendarTableView ... />
) : (
  <LoadingSpinner ... />
)}
```

## Archivos Modificados

1. `frontend/src/components/calendar/CalendarTableView.jsx`
   - Validaciones en `useMemo` para `calculatedMonths`
   - Validaciones en `handleContextMenu`
   - Validaciones en el renderizado de la tabla
   - Validaciones en la sección de festivos

2. `frontend/src/components/calendar/calendarHelpers.js`
   - Exportación mejorada con `Object.freeze`

3. `frontend/src/pages/CalendarPage.jsx`
   - Validación adicional antes de renderizar `CalendarTableView`

## Próximos Pasos

1. **Probar en producción**: Verificar que el calendario se renderiza correctamente después de estos cambios
2. **Monitorear logs**: Revisar si hay errores adicionales en la consola
3. **Optimización adicional**: Si el problema persiste, considerar usar lazy loading para `calendarHelpers`

## Notas Adicionales

- El problema es específico de producción debido a la minificación del código
- En desarrollo, el código no minificado puede funcionar correctamente
- Las validaciones agregadas son defensivas y no deberían afectar el rendimiento significativamente
- Si el problema persiste, podría ser necesario revisar la configuración de Vite para la minificación
