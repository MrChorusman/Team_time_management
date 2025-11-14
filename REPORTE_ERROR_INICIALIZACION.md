# REPORTE: Error de Inicialización en CalendarTableView

**Fecha:** 14 de Noviembre 2025  
**Problema:** `ReferenceError: Cannot access 'R' before initialization`  
**Estado:** 🔄 EN RESOLUCIÓN

---

## 🔍 ANÁLISIS DEL PROBLEMA

### Síntomas:
- Error en consola: `ReferenceError: Cannot access 'R' before initialization`
- La letra del error cambia entre deploys: 'F' → 'R' → 'O' → 'R'
- La página del calendario no carga, muestra pantalla en blanco
- El error ocurre durante la compilación/minificación de Vite

### Causa Probable:
El problema parece estar relacionado con cómo Vite está compilando y minificando el código. El cambio de letra ('F' → 'R' → 'O') sugiere que es un problema de orden de inicialización durante la compilación, no un problema específico del código fuente.

---

## ✅ CORRECCIONES APLICADAS

### 1. **Mover constantes fuera del componente**
- ✅ Movido `ISO_TO_COUNTRY_NAME` fuera del componente
- ✅ Movido `getDaysInMonth` fuera del componente
- ✅ Movido `getMonthsInYear` fuera del componente

### 2. **Refactorizar funciones de colores**
- ✅ Reemplazado objetos `colors` con if/else en `getCellBackgroundColor`
- ✅ Reemplazado objetos `colors` con if/else en `getCellTextColor`
- ✅ Reemplazado objeto `codes` con if/else en `getActivityCode`

### 3. **Usar useMemo para cálculos**
- ✅ Usado `useMemo` para calcular `days`
- ✅ Usado `useMemo` para calcular `months`
- ✅ Simplificado lógica de `useMemo` para evitar llamadas anidadas

### 4. **Corregir referencias a columnas inexistentes**
- ✅ Eliminado referencias a `hierarchy_level` (columna no existe en BD)
- ✅ Usado solo `holiday_type` para determinar tipo de festivo
- ✅ Corregido referencia a `holiday.type` en leyenda de festivos

### 5. **Añadir validaciones**
- ✅ Añadido `Array.isArray` checks en múltiples funciones
- ✅ Añadido validaciones null/undefined
- ✅ Añadido validaciones en `getMonthHolidays`

---

## 🔄 PRÓXIMOS PASOS

Si el error persiste después de estas correcciones, considerar:

1. **Revisar configuración de Vite**
   - Verificar configuración de minificación
   - Revisar orden de compilación de módulos

2. **Dividir el componente**
   - Separar `CalendarTableView` en componentes más pequeños
   - Extraer lógica compleja a hooks personalizados

3. **Revisar dependencias**
   - Verificar si hay conflictos de versiones
   - Revisar si hay problemas con imports circulares

4. **Alternativa: Usar lazy loading**
   - Cargar `CalendarTableView` de forma lazy
   - Verificar si el problema persiste con carga diferida

---

## 📊 ESTADO ACTUAL

- **Última corrección:** Simplificar lógica de useMemo
- **Deploy:** Pendiente verificación
- **Estado:** Esperando resultado del deploy

---

**Nota:** El problema parece ser específico de la compilación/minificación de Vite. Las correcciones aplicadas deberían resolver el problema, pero si persiste, puede requerir cambios en la arquitectura del componente o en la configuración de Vite.



