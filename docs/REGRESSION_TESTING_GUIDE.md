# Guía Manual de Pruebas de Regresión

**Fecha**: 29 de Enero, 2026  
**Versión**: Post-Optimizaciones de Rendimiento

---

## 📋 Índice

1. [Preparación](#preparación)
2. [Pruebas para Usuario Admin](#pruebas-para-usuario-admin)
3. [Pruebas para Usuario Empleado](#pruebas-para-usuario-empleado)
4. [Checklist Completo](#checklist-completo)

---

## Preparación

### Credenciales de Prueba

**Admin**:
- Email: `admin.test@example.com`
- Password: `AdminTest123!`

**Empleado**:
- Email: `employee.test@example.com`
- Password: `EmployeeTest123!`

### URLs de Producción

- Frontend: https://team-time-management.vercel.app
- Backend: https://team-time-management.onrender.com

---

## Pruebas para Usuario Admin

### 1. Login y Autenticación

**Pasos**:
1. Ir a la página de login
2. Ingresar credenciales de admin
3. Verificar redirección al dashboard

**Resultado esperado**: ✅ Login exitoso, dashboard carga correctamente

---

### 2. Dashboard de Admin

**Pasos**:
1. Verificar que el dashboard muestra estadísticas generales
2. Verificar que hay acceso a todas las secciones (empleados, equipos, calendario, etc.)

**Resultado esperado**: ✅ Dashboard completo con todas las opciones

---

### 3. Gestión de Empleados

**Crear Empleado**:
1. Ir a "Empleados" → "Nuevo Empleado"
2. Completar formulario con datos de prueba
3. Guardar

**Resultado esperado**: ✅ Empleado creado exitosamente

**Editar Empleado**:
1. Seleccionar un empleado existente
2. Modificar algún campo
3. Guardar cambios

**Resultado esperado**: ✅ Cambios guardados correctamente

**Eliminar Empleado**:
1. Seleccionar un empleado de prueba
2. Eliminar
3. Confirmar eliminación

**Resultado esperado**: ✅ Empleado eliminado

---

### 4. Gestión de Equipos

**Crear Equipo**:
1. Ir a "Equipos" → "Nuevo Equipo"
2. Completar formulario
3. Guardar

**Resultado esperado**: ✅ Equipo creado

**Editar Equipo**:
1. Seleccionar equipo
2. Modificar nombre o descripción
3. Guardar

**Resultado esperado**: ✅ Cambios guardados

---

### 5. Calendario Mensual (Todos los Empleados)

**Pasos**:
1. Ir a "Calendario" → Vista "Mensual"
2. Verificar que se muestran todos los empleados
3. Navegar entre meses (anterior/siguiente)
4. Verificar carga rápida (< 2 segundos)

**Resultado esperado**: ✅ Calendario carga rápido, muestra todos los empleados

---

### 6. Calendario Anual Optimizado

**Pasos**:
1. Cambiar vista a "Anual"
2. Verificar que carga todo el año de una vez
3. Verificar tiempo de carga (< 3 segundos para año completo)
4. Verificar que se pueden ver todos los meses

**Resultado esperado**: ✅ Vista anual carga rápidamente (optimización funcionando)

---

### 7. Crear Actividad en Calendario

**Pasos**:
1. Click derecho en una celda del calendario
2. Seleccionar tipo de actividad (Vacaciones, Ausencia, etc.)
3. Completar formulario
4. Guardar

**Resultado esperado**: ✅ Actividad creada y visible en calendario

---

### 8. Exportar Reportes

**Pasos**:
1. Ir a sección de reportes
2. Seleccionar rango de fechas
3. Exportar reporte (PDF/Excel)

**Resultado esperado**: ✅ Reporte generado correctamente

---

## Pruebas para Usuario Empleado

### 1. Login y Autenticación

**Pasos**:
1. Ir a página de login
2. Ingresar credenciales de empleado
3. Verificar redirección

**Resultado esperado**: ✅ Login exitoso

---

### 2. Dashboard Personal

**Pasos**:
1. Verificar que solo muestra información personal
2. Verificar que NO hay acceso a gestión de empleados/equipos

**Resultado esperado**: ✅ Dashboard limitado a información personal

---

### 3. Calendario Mensual (Solo Propio)

**Pasos**:
1. Ir a "Calendario" → Vista "Mensual"
2. Verificar que solo muestra su propio calendario
3. Verificar carga rápida

**Resultado esperado**: ✅ Solo ve su propio calendario

---

### 4. Calendario Anual (Solo Propio)

**Pasos**:
1. Cambiar a vista "Anual"
2. Verificar que solo muestra su año personal
3. Verificar carga rápida

**Resultado esperado**: ✅ Vista anual optimizada funciona para empleado

---

### 5. Crear Actividad Propia

**Pasos**:
1. Click derecho en su calendario
2. Crear actividad (Vacaciones, Ausencia, etc.)
3. Guardar

**Resultado esperado**: ✅ Actividad creada solo en su calendario

---

### 6. Editar Actividad Propia

**Pasos**:
1. Seleccionar una actividad existente
2. Modificar detalles
3. Guardar

**Resultado esperado**: ✅ Cambios guardados

---

### 7. Eliminar Actividad Propia

**Pasos**:
1. Seleccionar actividad
2. Eliminar
3. Confirmar

**Resultado esperado**: ✅ Actividad eliminada

---

### 8. Ver Notificaciones

**Pasos**:
1. Ir a sección de notificaciones
2. Verificar que se muestran notificaciones relevantes
3. Marcar como leídas

**Resultado esperado**: ✅ Notificaciones funcionan correctamente

---

### 9. Ver Perfil Personal

**Pasos**:
1. Ir a "Mi Perfil"
2. Verificar información personal
3. Intentar editar (si está permitido)

**Resultado esperado**: ✅ Perfil accesible y editable según permisos

---

## Checklist Completo

### Funcionalidades Críticas

- [ ] Login admin funciona
- [ ] Login empleado funciona
- [ ] Dashboard admin carga correctamente
- [ ] Dashboard empleado carga correctamente
- [ ] Calendario mensual admin (todos los empleados)
- [ ] Calendario anual admin optimizado
- [ ] Calendario mensual empleado (solo propio)
- [ ] Calendario anual empleado optimizado
- [ ] Crear actividad funciona
- [ ] Editar actividad funciona
- [ ] Eliminar actividad funciona
- [ ] Gestión de empleados (admin)
- [ ] Gestión de equipos (admin)
- [ ] Notificaciones funcionan
- [ ] Perfil personal accesible

### Rendimiento

- [ ] Calendario mensual carga en < 2 segundos
- [ ] Calendario anual carga en < 3 segundos
- [ ] Dashboard carga en < 1 segundo
- [ ] No hay errores en consola del navegador
- [ ] No hay errores en Network tab

### Casos Edge

- [ ] Calendario con muchos empleados (> 50)
- [ ] Calendario con año completo de datos
- [ ] Actividades en fechas pasadas
- [ ] Actividades en fechas futuras
- [ ] Festivos se muestran correctamente
- [ ] Fines de semana se muestran correctamente

---

## Notas

- Si alguna prueba falla, documentar el error exacto
- Tomar screenshots de errores si es posible
- Verificar logs del navegador (F12 → Console)
- Verificar Network tab para tiempos de respuesta

---

**Última actualización**: 29 de Enero, 2026
