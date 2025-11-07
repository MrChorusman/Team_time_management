# 📋 **ANÁLISIS: FUNCIONALIDAD DE MARCADO EN CALENDARIO**

**Fecha**: 07/11/2025  
**Documento Fuente**: `ANALISIS_COMPLETO_CONTROL_HORARIO`  
**Objetivo**: Definir cómo implementar la funcionalidad de marcar/editar actividades en el calendario

---

## 📖 **LO QUE ESPECIFICA EL DOCUMENTO ORIGINAL**

### **Información Clave Encontrada**:

**Línea 448**: 
> "**Marcado rápido con clic derecho**"

**Líneas 379-382**: 
> "CÓMO USAR EL CALENDARIO
> - Paso 1: Navegación
> - Paso 2: Marcar Actividades
> - Paso 3: Actividades con Horas
> - Paso 4: Eliminar Actividades"

**Líneas 410-413**: 
> "Validaciones Inteligentes:
> - No puedes marcar actividades en festivos o fines de semana
> - Solo puedes marcar en días laborables (blancos)
> - El sistema previene errores automáticamente"

**Línea 417**: 
> "Actualización en tiempo real: Los números se actualizan al marcar actividades"

**Líneas 424-427**: 
> "Para Empleados:
> - Marca las actividades tan pronto como sepas que vas a faltar
> - Usa HLD para salir antes o llegar tarde (más flexible que vacaciones)
> - Usa Guardia para horas extra que hagas
> - Revisa el resumen para ver cómo vas de vacaciones y ausencias"

---

## 🎯 **REQUISITOS FUNCIONALES IDENTIFICADOS**

### **1. Método de Interacción**
- ✅ **Clic derecho en celda** → Menú contextual

### **2. Validaciones**
- ❌ NO permitir marcar en festivos
- ❌ NO permitir marcar en fines de semana
- ✅ SOLO permitir marcar en días laborables (blancos)

### **3. Tipos de Actividades**
- **Día completo** (sin horas): V (Vacaciones), A (Ausencias), C (Permiso/Otro)
- **Con horas** (requieren número): HLD, G (Guardia), F (Formación)

### **4. Flujo de Trabajo**
1. **Click derecho** en celda de día laborable
2. **Menú contextual** con 6 opciones: V, A, HLD, G, F, C
3. Si elige opción con horas → **Modal/Input para ingresar horas**
4. **Guardar** en backend
5. **Actualización inmediata** del resumen (Vac, Aus)
6. **Cambio visual** de la celda (color + código)

### **5. Eliminar Actividades**
- **Click derecho** en celda con actividad existente
- **Opción adicional en menú**: "Eliminar"
- Confirmación antes de eliminar
- Actualización inmediata del resumen

---

## 💡 **MI OPINIÓN Y RECOMENDACIÓN DE IMPLEMENTACIÓN**

### **🏆 OPCIÓN RECOMENDADA: Click Derecho con Menú Contextual**

#### **¿Por qué esta es la mejor opción?**

1. **✅ Cumple con el requisito original**: "Marcado rápido con clic derecho"
2. **✅ UX Excel-like**: Similar a Excel/Google Sheets (familiar para usuarios)
3. **✅ Rápido y eficiente**: 2 clicks para marcar actividad simple
4. **✅ Intuitivo**: El usuario entiende inmediatamente cómo funciona
5. **✅ Menos código**: No requiere arrastrar, dropdowns complejos, etc.

#### **Flujo de Interacción Propuesto**:

**CASO 1: Marcar Vacaciones (V) o Ausencias (A)**
```
Usuario → Click derecho en celda día 15
       → Aparece menú: [V] [A] [HLD] [G] [F] [C]
       → Click en [V]
       → Se marca inmediatamente (celda verde + código "V")
       → Resumen Vac se actualiza: 5 → 6
       → Toast: "✅ Vacaciones marcadas para el 15 de noviembre"
```

**CASO 2: Marcar HLD con horas**
```
Usuario → Click derecho en celda día 18
       → Aparece menú: [V] [A] [HLD] [G] [F] [C]
       → Click en [HLD]
       → Se abre mini-modal: "¿Cuántas horas? [___] h" 
       → Usuario escribe: "2"
       → Click [Guardar]
       → Se marca: celda verde oscuro + código "HLD -2h"
       → Toast: "✅ HLD de 2 horas marcado para el 18 de noviembre"
```

**CASO 3: Eliminar actividad existente**
```
Usuario → Click derecho en celda con "V"
       → Aparece menú: [V] [A] [HLD] [G] [F] [C] | [🗑️ Eliminar]
       → Click en [🗑️ Eliminar]
       → Confirmación: "¿Eliminar Vacaciones del 15 de noviembre?"
       → Click [Eliminar]
       → Celda vuelve a blanco
       → Resumen Vac se actualiza: 6 → 5
       → Toast: "✅ Actividad eliminada"
```

**CASO 4: Intento de marcar festivo o fin de semana**
```
Usuario → Click derecho en celda roja (festivo)
       → NO aparece menú
       → Toast: "⚠️ No puedes marcar actividades en festivos"
```

---

## 🛠️ **COMPONENTES A DESARROLLAR**

### **1. ContextMenu Component** (Nuevo)
```jsx
<ContextMenu
  position={x, y}
  onSelect={handleMenuSelect}
  hasActivity={boolean}
  isHoliday={boolean}
  isWeekend={boolean}
>
  {/* Opciones: V, A, HLD, G, F, C */}
  {hasActivity && <MenuItem icon="🗑️">Eliminar</MenuItem>}
</ContextMenu>
```

### **2. HoursInputModal Component** (Nuevo)
```jsx
<HoursInputModal
  activityType={'hld' | 'guard' | 'training'}
  date={date}
  onSave={handleSaveActivity}
  onCancel={handleCancel}
/>
```

### **3. Modificar CalendarTableView**
- Agregar manejo de `onContextMenu` en celdas
- Estado para menú contextual abierto
- Estado para modal de horas
- Callbacks para crear/eliminar actividades

---

## 🔄 **INTEGRACIÓN CON BACKEND**

### **Endpoints Necesarios**:

**POST /api/calendar/activities**
```json
{
  "employee_id": 1,
  "date": "2025-11-15",
  "activity_type": "vacation",
  "hours": null,
  "notes": ""
}
```

**DELETE /api/calendar/activities/:id**
```json
{
  "activity_id": 123
}
```

**GET /api/calendar/data**
```json
{
  "employees": [...],
  "activities": [...],
  "holidays": [...]
}
```

---

## 🎨 **DISEÑO DEL MENÚ CONTEXTUAL**

### **Propuesta Visual**:

```
┌──────────────────────────┐
│  V  Vacaciones          │  ← Opción 1
├──────────────────────────┤
│  A  Ausencias           │  ← Opción 2
├──────────────────────────┤
│ HLD Horas Libre Disp.   │  ← Opción 3 (abre modal)
├──────────────────────────┤
│  G  Guardia             │  ← Opción 4 (abre modal)
├──────────────────────────┤
│  F  Formación           │  ← Opción 5 (abre modal)
├──────────────────────────┤
│  C  Permiso/Otro        │  ← Opción 6
├──────────────────────────┤
│ 🗑️  Eliminar            │  ← Solo si hay actividad
└──────────────────────────┘
```

**Estilo**:
- Fondo blanco con sombra
- Border gris claro
- Hover: fondo gris muy claro
- Iconos de color según tipo
- Separador antes de "Eliminar"

### **Modal de Horas**:

```
┌────────────────────────────────┐
│  HLD - Horas Libre Disposición │
├────────────────────────────────┤
│                                │
│  ¿Cuántas horas?               │
│  ┌──────┐                      │
│  │  2   │  horas                │
│  └──────┘                      │
│                                │
│  [Cancelar]      [Guardar]     │
│                                │
└────────────────────────────────┘
```

---

## 🔐 **PERMISOS Y ROLES**

### **¿Quién puede marcar qué?**

**Empleados** (role: employee):
- ✅ Pueden marcar sus propios días
- ❌ NO pueden marcar días de otros empleados
- ✅ Pueden ver calendario de todo su equipo

**Managers** (role: manager):
- ✅ Pueden marcar días de sus empleados
- ✅ Pueden ver calendario de todo su equipo
- ✅ Pueden aprobar/rechazar actividades

**Administradores** (role: admin):
- ✅ Pueden hacer todo
- ✅ Pueden ver todos los calendarios
- ✅ Pueden editar cualquier actividad

---

## ⚡ **FLUJO TÉCNICO PROPUESTO**

### **1. Click Derecho en Celda**
```javascript
const handleContextMenu = (e, employeeId, date, existingActivity) => {
  e.preventDefault() // Prevenir menú del navegador
  
  // Validar si es día laborable
  if (isHoliday(date) || isWeekend(date)) {
    toast.warning('No puedes marcar actividades en festivos o fines de semana')
    return
  }
  
  // Mostrar menú contextual
  setContextMenu({
    visible: true,
    x: e.clientX,
    y: e.clientY,
    employeeId,
    date,
    existingActivity
  })
}
```

### **2. Selección de Opción**
```javascript
const handleMenuSelect = (activityType) => {
  // Si requiere horas, abrir modal
  if (['hld', 'guard', 'training'].includes(activityType)) {
    setHoursModal({
      visible: true,
      activityType,
      employeeId: contextMenu.employeeId,
      date: contextMenu.date
    })
    setContextMenu({ visible: false })
    return
  }
  
  // Si no requiere horas, guardar directamente
  createActivity({
    employeeId: contextMenu.employeeId,
    date: contextMenu.date,
    activityType,
    hours: null
  })
  
  setContextMenu({ visible: false })
}
```

### **3. Guardar con Horas**
```javascript
const handleSaveWithHours = (hours) => {
  createActivity({
    employeeId: hoursModal.employeeId,
    date: hoursModal.date,
    activityType: hoursModal.activityType,
    hours: parseFloat(hours)
  })
  
  setHoursModal({ visible: false })
}
```

### **4. Actualización Optimista**
```javascript
const createActivity = async (activityData) => {
  // 1. Actualizar UI inmediatamente (optimistic update)
  const newActivity = {
    id: `temp-${Date.now()}`,
    ...activityData,
    status: 'approved'
  }
  setActivities([...activities, newActivity])
  
  // 2. Enviar al backend
  try {
    const response = await api.post('/calendar/activities', activityData)
    
    // 3. Reemplazar temporal con real
    setActivities(prev => prev.map(a => 
      a.id === newActivity.id ? response.data : a
    ))
    
    toast.success('✅ Actividad guardada')
  } catch (error) {
    // 4. Revertir si falla
    setActivities(prev => prev.filter(a => a.id !== newActivity.id))
    toast.error('❌ Error guardando actividad')
  }
}
```

---

## 🎯 **COMPARACIÓN DE OPCIONES**

### **Opción A: Click Derecho + Menú Contextual** ⭐ **RECOMENDADO**

**Ventajas**:
- ✅ Cumple requisito original: "Marcado rápido con clic derecho"
- ✅ UX familiar (Excel, Google Sheets)
- ✅ Rápido: 2 clicks para actividades simples
- ✅ Menos espacio en pantalla
- ✅ Intuitivo y natural

**Desventajas**:
- ⚠️ Algunos usuarios no conocen clic derecho en móvil
- ⚠️ Necesita adaptación para touch devices

**Complejidad**: Media  
**Tiempo estimado**: 2-3 horas

---

### **Opción B: Click Simple + Modal**

**Ventajas**:
- ✅ Funciona igual en desktop y móvil
- ✅ Formulario completo con validaciones
- ✅ Opción para agregar notas

**Desventajas**:
- ❌ NO cumple requisito de "clic derecho"
- ❌ Más lento: 3-4 clicks mínimo
- ❌ Modal ocupa toda la pantalla

**Complejidad**: Media  
**Tiempo estimado**: 2-3 horas

---

### **Opción C: Doble Click + Dropdown Inline**

**Ventajas**:
- ✅ Rápido en desktop
- ✅ Edición inline sin modal

**Desventajas**:
- ❌ NO cumple requisito de "clic derecho"
- ❌ Difícil en móviles
- ❌ Puede ser confuso (usuarios pueden hacer doble click por accidente)

**Complejidad**: Alta  
**Tiempo estimado**: 3-4 horas

---

## 🏆 **MI RECOMENDACIÓN: OPCIÓN A (Click Derecho + Menú Contextual)**

### **¿Por qué?**

1. **✅ Cumple con el documento original**: Línea 448 especifica "Marcado rápido con clic derecho"

2. **✅ UX Excel-like**: Los usuarios están acostumbrados a clic derecho en hojas de cálculo

3. **✅ Eficiente**: 
   - Vacaciones: 2 clicks (derecho → V)
   - HLD: 3 clicks (derecho → HLD → ingresar horas)

4. **✅ Adaptable a móvil**: En touch devices, un "long press" (presión larga) funciona como clic derecho

5. **✅ Escalable**: Fácil agregar más opciones al menú después

---

## 📱 **ADAPTACIÓN PARA MÓVILES**

### **Solución Híbrida**:

**Desktop**:
- Click derecho → Menú contextual

**Móvil/Tablet**:
- **Long press** (tocar y mantener 500ms) → Menú contextual
- **Alternativa**: Botón "+" flotante en cada celda en móvil

```javascript
const handleTouchStart = (e, employeeId, date) => {
  longPressTimer = setTimeout(() => {
    // Simular clic derecho después de 500ms
    handleContextMenu(e, employeeId, date)
    navigator.vibrate?.(50) // Feedback háptico
  }, 500)
}

const handleTouchEnd = () => {
  clearTimeout(longPressTimer)
}
```

---

## 🎨 **DISEÑO VISUAL DEL MENÚ CONTEXTUAL**

### **Colores de las Opciones**:

```
┌─────────────────────────────────┐
│ 🟢  V  Vacaciones              │  Verde claro
├─────────────────────────────────┤
│ 🟡  A  Ausencias               │  Amarillo
├─────────────────────────────────┤
│ 🟢  HLD Horas Libre Disp. →    │  Verde oscuro + flecha
├─────────────────────────────────┤
│ 🔵  G  Guardia →               │  Azul + flecha
├─────────────────────────────────┤
│ 🟣  F  Formación →             │  Morado + flecha
├─────────────────────────────────┤
│ 🔵  C  Permiso/Otro            │  Azul claro
├─────────────────────────────────┤
│ 🗑️  Eliminar                   │  Rojo (solo si hay actividad)
└─────────────────────────────────┘
```

La **flecha →** indica que abrirá un modal para ingresar horas.

---

## 🔄 **ESTADOS Y FEEDBACK VISUAL**

### **Estados de las Celdas**:

1. **Vacía + Hover**: Borde azul suave
2. **Con actividad + Hover**: Borde más oscuro del color de la actividad
3. **Click derecho activo**: Sombra y resaltado
4. **Guardando**: Mini spinner en la celda
5. **Error al guardar**: Borde rojo parpadeante

### **Feedback Visual**:

- **Toast Notifications**:
  - ✅ "Vacaciones marcadas para el 15 de noviembre"
  - ✅ "HLD de 2 horas guardado"
  - ❌ "Error: No puedes marcar este día"
  - 🗑️ "Actividad eliminada"

- **Actualización Inmediata**:
  - Celda cambia de color instantáneamente
  - Código aparece en la celda
  - Resumen Vac/Aus se actualiza
  - Sin recargar la página (optimistic update)

---

## 🔐 **VALIDACIONES Y SEGURIDAD**

### **Frontend**:
1. ✅ Validar que es día laborable (no festivo, no fin de semana)
2. ✅ Validar que el usuario puede editar ese empleado
3. ✅ Validar horas (0.5 a 12 horas)
4. ✅ Validar que no haya ya una actividad (o mostrar opción eliminar)

### **Backend**:
1. ✅ Verificar autenticación
2. ✅ Verificar permisos (empleado solo sus días, manager su equipo)
3. ✅ Validar fecha (no en pasado lejano, no muy futuro)
4. ✅ Validar tipo de actividad
5. ✅ Validar horas si aplica
6. ✅ Prevenir duplicados

---

## 📊 **ESTRUCTURA DE DATOS**

### **Activity Model**:
```javascript
{
  id: 123,
  employee_id: 1,
  date: "2025-11-15",
  activity_type: "vacation", // v, a, hld, guard, training, other
  hours: 2.0, // null para vacaciones/ausencias
  notes: "",
  status: "approved", // pending, approved, rejected
  created_at: "2025-11-07T12:00:00Z",
  created_by: 1
}
```

---

## ⏱️ **ESTIMACIÓN DE DESARROLLO**

### **Componentes a Crear**:
1. **ContextMenu.jsx** - 150 líneas - 45 min
2. **HoursInputModal.jsx** - 100 líneas - 30 min
3. **Modificar CalendarTableView** - 200 líneas - 60 min
4. **Estilos CSS** - 50 líneas - 15 min
5. **Testing** - 60 min

**Total estimado**: **3-3.5 horas**

---

## 🚀 **PLAN DE IMPLEMENTACIÓN PROPUESTO**

### **Fase 1: Componentes Base** (1.5h)
1. Crear ContextMenu component
2. Crear HoursInputModal component
3. Agregar estilos

### **Fase 2: Integración** (1h)
1. Modificar CalendarTableView para manejar eventos
2. Estado para menú contextual
3. Estado para modal de horas
4. Callbacks de crear/eliminar

### **Fase 3: Backend Integration** (0.5h)
1. Conectar con endpoints API
2. Manejo de errores
3. Toast notifications

### **Fase 4: Testing** (1h)
1. Probar en browser cada tipo de actividad
2. Probar validaciones
3. Probar eliminación
4. Probar actualización de resumen

---

## ✅ **CONCLUSIÓN Y RECOMENDACIÓN**

### **Recomiendo implementar: OPCIÓN A - Click Derecho + Menú Contextual**

**Razones**:
1. ✅ Cumple 100% con documento original
2. ✅ UX familiar y eficiente
3. ✅ Rápido de implementar
4. ✅ Fácil de mantener
5. ✅ Escalable para futuras mejoras

### **Beneficios Adicionales**:
- 🎯 Marcado rápido (2 clicks)
- 🎨 Feedback visual inmediato
- 🔄 Actualización en tiempo real
- ✅ Validaciones automáticas
- 📱 Adaptable a móvil (long press)

---

## ❓ **PREGUNTAS PARA TI, MIGUEL**

Antes de comenzar a implementar, necesito tu confirmación en:

1. **¿Confirmas que quieres click derecho + menú contextual?** (según documento original)

2. **¿Los empleados pueden editar solo sus días, o también de sus compañeros de equipo?**

3. **¿Las actividades se guardan inmediatamente, o necesitan aprobación de manager?**
   - Si es inmediato → más rápido para el empleado
   - Si necesita aprobación → más control para el manager

4. **¿Implementamos también la funcionalidad para móvil (long press)?**

5. **¿Prefieres que cree los componentes en esta misma rama o hacemos merge primero y luego otra rama?**

---

**Esperando tus respuestas para proceder con la implementación.** 🚀

