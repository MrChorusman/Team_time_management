# 🧪 Reporte de Pruebas - Formulario de Registro de Empleado

**Fecha**: 1 de Noviembre de 2025  
**Rama**: `fix-auth-blueprint-regression`  
**Objetivo**: Validar flujo completo de registro según roles y estados

---

## 📋 Plan de Pruebas del Usuario

### **PRUEBA 1: Botón "Volver al Dashboard"**

#### **1a. Usuario Admin sin Registro**
**Resultado esperado**: Debe permitir acceso al dashboard (admin no requiere perfil de empleado)

**Pasos**:
1. Login como admin (`miguelchis@gmail.com`)
2. En `/employee/register`, click en "Volver al Dashboard"
3. Verificar redirección a `/dashboard`

**Resultado**: ✅ **PASADA**
- ✅ Admin detectado correctamente por `useRoles()`
- ✅ `ProtectedRoute` permitió acceso (fix aplicado)
- ✅ Navegó a `/dashboard` exitosamente
- ✅ Dashboard muestra mensaje: "Completa tu registro de empleado para acceder al dashboard completo"

**Fix Crítico Aplicado**:
```javascript
// App.jsx - ProtectedRoute
// ANTES: const isAdminOrManager = isAdmin() || isManager() // ❌ Funciones no exportadas
// AHORA: const userRoles = user.roles || []
//        const isAdminOrManager = userRoles.includes('admin') || userRoles.includes('manager') // ✅
```

---

#### **1b. Usuario NO Admin sin Registro**
**Resultado esperado**: Debe mostrar advertencia indicando que debe completar registro

**Pasos**:
1. Logout como admin
2. Login como employee (`employee.test@example.com`)
3. En `/employee/register`, click en "Volver al Dashboard"
4. Verificar advertencia y permanencia en `/employee/register`

**Resultado**: ✅ **PASADA**
- ✅ Advertencia mostrada correctamente:
  > "No puedes acceder a la aplicación hasta que completes tu registro."
- ✅ Permaneció en `/employee/register`
- ✅ Advertencia desaparece después de 5 segundos (timeout)

---

### **🐛 PROBLEMA ENCONTRADO Y RESUELTO: Dropdown de Equipos Vacío**

**Síntoma**: Al intentar seleccionar un equipo en el formulario de registro, el dropdown aparecía vacío.

**Diagnóstico**:
1. Console del navegador mostraba: `✅ GET /teams {teams: Array(0)}`
2. Base de datos tenía 18 equipos, pero el endpoint devolvía 0
3. Backend tenía código que filtraba por `Team.id == -1` para empleados sin perfil

**Causa Raíz**:
El endpoint `/api/teams` en `backend/app/teams.py` aplicaba un filtro restrictivo cuando un usuario con rol `employee` sin perfil registrado intentaba cargar equipos. El código original:
```python
elif current_user.is_employee() and not current_user.is_manager():
    if current_user.employee and current_user.employee.team_id:
        query = query.filter(Team.id == current_user.employee.team_id)
    else:
        query = query.filter(Team.id == -1)  # ❌ Devolvía 0 equipos
```

**Solución**:
Modificado líneas 40-48 de `backend/app/teams.py` para que empleados **sin perfil registrado** vean **todos los equipos**:
```python
elif current_user.is_employee() and not current_user.is_manager():
    if current_user.employee and current_user.employee.team_id:
        query = query.filter(Team.id == current_user.employee.team_id)
    else:
        # No aplicar filtro → mostrar todos los equipos para registro
        pass  # ✅ Devuelve todos los equipos
```

**Verificación**:
- ✅ Console: `✅ GET /teams {teams: Array(18)}`
- ✅ Dropdown muestra 18 equipos: Marketing, Monitorización, Desarrollo, etc.
- ✅ Commit: `18e9243` - "fix: Permitir a empleados sin perfil ver todos los equipos"

**Nota Técnica**: El backend no se reinició automáticamente después de la modificación porque el puerto 5001 estaba ocupado. Fue necesario reiniciar manualmente

---

### **PRUEBA 2: Guardar Perfil de Empleado**

#### **2a. Usuario NO Admin Rellena y Guarda Formulario**
**Resultado esperado**: 
- Guardar perfil exitosamente
- Mostrar mensaje: "Se ha enviado notificación al manager para su validación"

**Pasos**: ⏳ Pendiente...

---

## 📊 Progreso

| Prueba | Estado | Resultado |
|--------|--------|-----------|
| 1a. Admin → Dashboard | ✅ **PASADA** | Acceso permitido correctamente |
| 1b. No-Admin → Dashboard | ✅ **PASADA** | Advertencia mostrada correctamente |
| 2. Rellenar y Guardar | ⏳ **En Progreso** | Dropdown de equipos funcionando (18 items) |

**Tests Ejecutados**: 2/3  
**Tests Pasados**: 2/2  
**Tasa de Éxito**: 100%

**Problemas Resueltos**: 1 (Dropdown de equipos vacío)

---

**Continuará...**

