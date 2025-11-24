# 📋 REPORTE DE PRUEBAS DEL CALENDARIO - 21 NOVIEMBRE 2025

## 🎯 OBJETIVO
Realizar pruebas completas del sistema de calendario tras la restauración de producción.

---

## ✅ PRUEBAS REALIZADAS

### 1. Carga Visual de Componentes
**Estado**: ✅ **PASADO**

**Resultados**:
- El calendario se carga correctamente
- Todos los componentes visuales están presentes:
  - Tabla de calendario con columnas de días
  - Filas de empleados por equipo
  - Leyenda de tipos de actividades (V, A, HLD, G, F, C, Festivo, Fin Semana)
  - Controles de navegación (Mensual/Anual, anterior/siguiente)
  - Filtros y vistas (Tabla/Calendario)
- El menú lateral se despliega correctamente
- La barra superior con notificaciones está visible
- El scroll funciona correctamente

**Screenshot**: `calendario-carga-inicial.png`

---

### 2. Carga de Festivos
**Estado**: ✅ **CORREGIDO**

**Problema detectado**:
- ⚠️ Se detectaron festivos duplicados:
  - Día 1 de noviembre: "Todos los Santos (Nacional)" y "All Saints Day (Nacional)"
  - Esto confirmaba el problema de duplicados por variantes de idioma (español/inglés)

**Solución implementada**:
1. ✅ **Backend corregido**: Modificado `calendar_service.py` para deduplicar festivos antes de devolverlos, priorizando:
   - Festivos con país en español
   - Festivos con nombre en español
   - Festivos más antiguos (ID más bajo)
   
2. ✅ **Base de datos limpiada**: Ejecutado script `deduplicate_holidays_final.py` que eliminó **44 festivos duplicados** de **34 grupos**, priorizando festivos en español.

**Resultados**:
- ✅ Los festivos ahora se deduplican automáticamente en el backend
- ✅ Se eliminaron todos los duplicados existentes en la base de datos (44 festivos duplicados eliminados)
- ✅ Los festivos se muestran correctamente sin duplicados en el frontend
- ✅ **Verificado en producción**: Solo aparece "Día 1: Todos los Santos (Nacional)" sin el duplicado "All Saints Day"

---

### 3. Creación y Eliminación de Actividades
**Estado**: ✅ **PARCIALMENTE COMPLETADO**

**Resultados**:
- ✅ Menú contextual funciona correctamente (clic derecho en celda)
- ✅ Creación de Vacaciones (V) funciona correctamente
  - Modal se abre correctamente
  - Muestra fecha, empleado y permite motivo opcional
  - Actividad se crea y aparece en el calendario
  - Estadísticas se actualizan (Vac: 2 → 3)
- ⚠️ **Error encontrado y corregido**: Al intentar eliminar una actividad, se producía un error `TypeError: Cannot read properties of undefined (reading 'toUpperCase')` porque el código intentaba acceder a `activity.type` cuando la actividad puede tener `activity_type` o `type`.
  - **Corrección**: Se actualizó `handleDeleteActivity` para usar `activity.activity_type || activity.type` y `getActivityCodeHelper` para obtener el código correcto.
  - **Commit**: `4936005` - "fix: corregir error al eliminar actividad (usar activity_type o type)"
- ✅ Eliminación de actividades funciona correctamente
  - Menú contextual muestra opción "Eliminar" cuando hay actividad
  - Confirmación funciona correctamente
  - Actividad se elimina y desaparece del calendario
  - Estadísticas se actualizan (Vac: 3 → 2)
  - Calendario se recarga automáticamente
- ✅ Creación de Ausencias (A) funciona correctamente
  - Modal se abre correctamente desde el menú contextual
  - Muestra fecha, empleado y permite motivo opcional
  - Actividad se crea y aparece en el calendario
  - Estadísticas se actualizan (Aus: 0 → 1)
- ✅ Creación de HLD (Horas Libre Disposición) funciona correctamente
  - Modal se abre correctamente desde el botón del menú contextual
  - Permite especificar horas (0.5-12 horas)
  - Muestra fecha, empleado y permite motivo opcional
  - Actividad se crea y aparece en el calendario con formato "HLD -3h"
  - Calendario se recarga correctamente
- ✅ Creación de Guardia (G) funciona correctamente
  - Modal se abre correctamente desde el botón del menú contextual
  - Permite especificar horario de inicio y fin
  - Calcula automáticamente la duración (ej: 8 horas)
  - Muestra fecha, empleado y permite motivo opcional
  - Actividad se crea y aparece en el calendario con formato "G +8h"
  - Calendario se recarga correctamente
- ⏳ Pendiente: Probar otros tipos de actividad (F, C) - Probablemente funcionan de forma similar
- ⏳ Pendiente: Verificar validaciones y mensajes de error

---

### 4. Actualización de Estadísticas
**Estado**: ✅ **PARCIALMENTE VERIFICADO**

**Resultados**:
- ✅ Las estadísticas se actualizan correctamente tras crear actividad de Vacaciones
  - Contador "Vac" se incrementó de 2 a 3 automáticamente
  - El calendario se recarga y refleja los cambios
- ✅ Actualización tras eliminar actividades verificada
  - Contador "Vac" se decrementó de 3 a 2 automáticamente
  - El calendario se recarga y refleja los cambios correctamente
- ✅ Actualización tras crear Ausencias verificada
  - Contador "Aus" se incrementó de 0 a 1 automáticamente
  - El calendario se recarga y refleja los cambios correctamente
- ✅ Actualización tras crear HLD verificada
  - Actividad aparece correctamente en el calendario con formato "HLD -3h"
  - El calendario se recarga y refleja los cambios correctamente
- ✅ Actualización tras crear Guardia verificada
  - Actividad aparece correctamente en el calendario con formato "G +8h"
  - El calendario se recarga y refleja los cambios correctamente
- ⏳ Pendiente: Verificar actualización para otros tipos de actividad (F, C)

---

### 5. Estudio de Rendimiento
**Estado**: ✅ **COMPLETADO**

**Métricas obtenidas**:
- ✅ **Carga inicial**: ~1 segundo (Page Load Time: 1,007 ms)
- ✅ **First Contentful Paint**: ~1.3 segundos (1,348 ms)
- ✅ **Interfaz responsiva**: Respuesta instantánea a interacciones
- ✅ **Renderizado**: Sin problemas visuales, scroll fluido

**Tiempos de API**:
- `/api/auth/me`: ~242 ms (✅ Aceptable)
- `/api/calendar`: ~11-13 segundos (⚠️ Lento cuando servicio hibernado en Render free tier)
- `/api/notifications`: ~400 ms (✅ Aceptable)

**Evaluación**:
- ✅ **Frontend**: Excelente rendimiento, carga rápida y experiencia fluida
- ⚠️ **Backend**: Tiempos altos cuando el servicio está hibernado (limitación del plan gratuito de Render)
- ✅ **Experiencia de usuario**: Ágil y rápida en condiciones normales

**Documentación completa**: Ver `ESTUDIO_RENDIMIENTO_CALENDARIO_21NOV.md`

---

## 📝 NOTAS

- **Login**: Resuelto tras actualizar hash con SALT de producción
- **Festivos duplicados**: ✅ Corregido - Backend deduplica automáticamente y se eliminaron 44 duplicados de la BD
- **Calendario funcional**: El calendario carga y muestra datos correctamente
- **Error de eliminación**: Corregido error al eliminar actividades (usar activity_type o type)

---

---

### 6. Prueba de Vista Anual
**Estado**: ✅ **COMPLETADO (con observaciones de rendimiento)**  

**Resultados**:
- ✅ **Festivos por mes correctos**: los 12 meses muestran su leyenda con los festivos correspondientes
  - Enero: 2 festivos (Año Nuevo, Reyes)  
  - Abril: 7 festivos (Jueves/Viernes Santo, Pascua, Aragón, CyL, etc.)
  - Diciembre: 5 festivos (Constitución, Inmaculada, Navidad, San Esteban…)
- ✅ **Sin duplicados por idioma**: se añadió deduplicación por fecha+país priorizando los nombres en español cuando existen duplicidades (ej.: solo se muestra “Navidad”, desaparece “Christmas Day”)
- ⚠️ **Nombres en inglés residuales**: algunos festivos siguen apareciendo en inglés porque en la BD no hay variante en castellano (ej.: “New Year’s Day”). Se necesita la traducción en origen para mostrarlos en español.
- ⚠️ **Tiempo de carga elevado**: la vista anual tarda ~55‑60 seg en completarse (se lanzan 12 peticiones `/api/calendar` + paginación de festivos). No hay timeouts, pero la UX se resiente.

**Recomendaciones**:
- Añadir barra/progreso mientras se precarga la vista anual y avisar del tiempo estimado.
- Evaluar lazy-loading por bloques (trimestre) o cachear resultados para reducir el tiempo total.
- Completar en la BD los nombres de festivos en castellano para los países con prioridad (España) y así evitar traducciones mixtas.

---

## 🔄 SIGUIENTE PASO
Continuar con pruebas de creación/eliminación de actividades y verificación de estadísticas.

