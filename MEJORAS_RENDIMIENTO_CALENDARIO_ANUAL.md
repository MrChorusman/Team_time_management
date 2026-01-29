# 🚀 Propuestas de Mejora: Rendimiento Calendario Anual

## 📊 Situación Actual

**Problema**: La vista anual del calendario tarda **~50-55 segundos** en cargar completamente.

**Causas identificadas**:
1. **12 requests paralelas** al endpoint `/calendar?year=X&month=Y` (una por mes)
2. **Múltiples requests paginadas** para festivos (hasta 12 páginas)
3. **Espera bloqueante**: No se muestra nada hasta que TODAS las peticiones terminen
4. **Sin caché**: Cada cambio de vista recarga todo desde cero
5. **Sin feedback visual**: El usuario solo ve "Cargando..." durante 50+ segundos

---

## 🎯 Soluciones Propuestas (ordenadas por impacto)

### 1. ⭐ **Carga Incremental con Indicador de Progreso** (ALTA PRIORIDAD)

**Descripción**: Cargar meses de forma progresiva y mostrar cada mes conforme se carga, con indicador de progreso.

**Beneficios**:
- ✅ El usuario ve contenido inmediatamente (primeros meses en ~5-10s)
- ✅ Feedback visual claro del progreso
- ✅ Mejor percepción de rendimiento
- ✅ No requiere cambios en backend

**Implementación**:
- Estado para tracking de meses cargados: `{ 1: true, 2: true, ... }`
- Barra de progreso: "Cargando 3/12 meses..."
- Renderizar meses conforme se cargan (no esperar todos)
- Cargar meses prioritarios primero (enero-marzo)

**Tiempo estimado de implementación**: 2-3 horas
**Mejora esperada**: De 50s a 10-15s para ver primeros meses, 50s total para todos

---

### 2. 💾 **Caché en Memoria** (ALTA PRIORIDAD)

**Descripción**: Guardar datos cargados por año/empleado para evitar recargas innecesarias.

**Beneficios**:
- ✅ Recargas instantáneas si los datos ya están en caché
- ✅ Reduce carga en servidor
- ✅ Mejor experiencia al cambiar entre vistas

**Implementación**:
- Usar `useRef` o `Map` para almacenar datos por clave: `year-employeeId-viewMode`
- Invalidar caché cuando se crea/elimina actividad
- TTL opcional (ej: 5 minutos)

**Tiempo estimado**: 1-2 horas
**Mejora esperada**: Recargas instantáneas (0s) si datos en caché

---

### 3. 🔄 **Carga Prioritaria (Lazy Loading)** (MEDIA PRIORIDAD)

**Descripción**: Cargar primero los meses visibles en viewport, luego el resto en segundo plano.

**Beneficios**:
- ✅ Contenido visible más rápido
- ✅ Reduce carga inicial
- ✅ Mejor para conexiones lentas

**Implementación**:
- Usar `Intersection Observer` para detectar meses visibles
- Cargar meses 1-3 primero, luego 4-12 en segundo plano
- Mostrar placeholder/skeleton mientras carga

**Tiempo estimado**: 3-4 horas
**Mejora esperada**: De 50s a 5-8s para contenido visible

---

### 4. 🎯 **Endpoint Optimizado en Backend** (BAJA PRIORIDAD - requiere backend)

**Descripción**: Crear endpoint específico `/api/calendar/annual?year=2025` que devuelva todo en una sola request optimizada.

**Beneficios**:
- ✅ Una sola request en lugar de 12
- ✅ Backend puede optimizar queries SQL
- ✅ Menos overhead de red

**Implementación**:
- Nuevo endpoint en `backend/app/calendar.py`
- Query optimizada que obtenga todos los meses en una sola consulta
- Agregación de datos en backend

**Tiempo estimado**: 4-6 horas (backend + frontend)
**Mejora esperada**: De 50s a 15-20s (una request optimizada)

---

### 5. 📦 **Virtualización de Renderizado** (BAJA PRIORIDAD)

**Descripción**: Renderizar solo los meses visibles en el viewport usando librerías como `react-window`.

**Beneficios**:
- ✅ Mejor rendimiento con muchos empleados
- ✅ Scroll más fluido
- ✅ Menos DOM nodes

**Implementación**:
- Instalar `react-window` o `react-virtualized`
- Virtualizar lista de meses
- Configurar altura estimada por mes

**Tiempo estimado**: 4-5 horas
**Mejora esperada**: Scroll más fluido, especialmente con 10+ empleados

---

## 🎯 Recomendación: Plan de Implementación

### Fase 1 (Inmediata) - Máximo Impacto, Mínimo Esfuerzo
1. ✅ **Carga Incremental con Progreso** (2-3h)
2. ✅ **Caché en Memoria** (1-2h)

**Resultado esperado**: 
- Primeros meses visibles en 10-15s
- Recargas instantáneas
- Mejor UX con feedback visual

### Fase 2 (Siguiente iteración)
3. **Carga Prioritaria** (3-4h)

**Resultado esperado**: 
- Contenido visible en 5-8s
- Resto carga en segundo plano

### Fase 3 (Futuro - si es necesario)
4. **Endpoint Optimizado** (4-6h)
5. **Virtualización** (4-5h)

---

## 📈 Métricas de Éxito

**Antes**:
- Tiempo hasta primer contenido: 50s
- Tiempo total de carga: 50s
- Feedback visual: "Cargando..." (sin progreso)

**Después (Fase 1)**:
- Tiempo hasta primer contenido: 10-15s ⚡
- Tiempo total de carga: 50s (igual, pero con contenido visible antes)
- Feedback visual: Barra de progreso "3/12 meses"
- Recargas: Instantáneas (caché) ⚡

**Después (Fase 2)**:
- Tiempo hasta primer contenido: 5-8s ⚡⚡
- Tiempo total de carga: 50s (resto en segundo plano)
- Feedback visual: Progreso + skeleton loaders

---

## 🔧 Consideraciones Técnicas

### Caché
- **Clave de caché**: `${year}-${employeeId || 'all'}-${viewMode}`
- **Invalidación**: Al crear/eliminar actividad, cambiar año, cambiar empleado
- **TTL**: Opcional, 5 minutos por defecto

### Progreso
- **Estado**: `{ loadedMonths: Set<number>, totalMonths: 12 }`
- **UI**: Barra de progreso + texto "Cargando 3/12 meses..."
- **Renderizado**: Mostrar meses conforme se cargan (no esperar todos)

### Priorización
- **Meses prioritarios**: 1-3 (enero-marzo) - primeros visibles
- **Meses secundarios**: 4-12 - cargar en segundo plano
- **Estrategia**: `Promise.allSettled` para no bloquear si un mes falla

---

## ✅ Próximos Pasos

1. Implementar **Carga Incremental con Progreso**
2. Implementar **Caché en Memoria**
3. Probar en producción
4. Medir mejoras reales
5. Decidir si continuar con Fase 2

