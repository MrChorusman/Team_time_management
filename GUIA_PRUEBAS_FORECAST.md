# 🧪 **GUÍA DE PRUEBAS - SISTEMA DE FORECAST**

## 📋 **OBJETIVO**

Verificar que el sistema de Forecast funciona correctamente con:
- Gestión de empresas y períodos de facturación personalizados
- Cálculo de horas teóricas vs reales (excluyendo guardias)
- Cálculo de eficiencia y valor económico
- Vistas por empleado, equipo y global
- Gestión de tarifas por hora

---

## ✅ **PREPARACIÓN**

### 1. Verificar Despliegue

**Backend (Render):**
- Verificar que el último commit `feature-forecast-system` esté desplegado
- Verificar que la migración de base de datos se haya aplicado correctamente
- URL: `https://19hninc0y7nk.manus.space` (o la URL actual de Render)

**Frontend (Vercel):**
- Verificar que el último commit `feature-forecast-system` esté desplegado
- URL: `https://team-time-management.vercel.app` (o la URL actual de Vercel)

**Verificación rápida:**
```bash
# Verificar backend
curl https://19hninc0y7nk.manus.space/api/health

# Verificar que el endpoint de empresas existe (requiere autenticación)
# Esto se probará desde el navegador
```

---

## 🧪 **PRUEBAS PASO A PASO**

### **FASE 1: Gestión de Empresas (Admin)**

#### **Prueba 1.1: Crear Empresa**

1. **Acción:**
   - Iniciar sesión como administrador (`admin@teamtime.com`)
   - Navegar a **Administración** → **Empresas**
   - Hacer clic en **"Nueva Empresa"**

2. **Datos de prueba:**
   ```
   Nombre: Cliente ABC S.L.
   Día de Inicio: 1
   Día de Fin: 31
   Estado: Activa ✓
   ```

3. **Resultado esperado:**
   - ✅ Empresa creada exitosamente
   - ✅ Aparece en la tabla de empresas
   - ✅ Mensaje de éxito: "Empresa creada exitosamente"

#### **Prueba 1.2: Crear Empresa con Período que Cruza Meses**

1. **Acción:**
   - Crear nueva empresa con período que cruza meses

2. **Datos de prueba:**
   ```
   Nombre: Cliente XYZ S.A.
   Día de Inicio: 26
   Día de Fin: 25
   Estado: Activa ✓
   ```

3. **Resultado esperado:**
   - ✅ Alerta visual indicando que el período cruza meses
   - ✅ Empresa creada exitosamente
   - ✅ En la tabla muestra "(cruza meses)"

#### **Prueba 1.3: Editar Empresa**

1. **Acción:**
   - Hacer clic en **"Acciones"** (3 puntos) → **"Editar"** en una empresa existente
   - Modificar el nombre o el período

2. **Resultado esperado:**
   - ✅ Cambios guardados correctamente
   - ✅ Mensaje de éxito: "Empresa actualizada exitosamente"

#### **Prueba 1.4: Desactivar Empresa**

1. **Acción:**
   - Hacer clic en **"Acciones"** → **"Desactivar"**
   - Confirmar en el diálogo

2. **Resultado esperado:**
   - ✅ Empresa marcada como "Inactiva"
   - ✅ No aparece en el selector de empresas del Forecast (si se filtra `active_only=true`)

---

### **FASE 2: Configuración de Tarifas (Admin)**

#### **Prueba 2.1: Configurar Tarifa de Empleado**

1. **Acción:**
   - Navegar a **Empleados**
   - Hacer clic en el icono del ojo para ver detalles de un empleado
   - Verificar que aparece "Tarifa por hora" en la sección "Configuración Horaria"
   - **Nota:** Por ahora solo se muestra, la edición se puede hacer desde el backend directamente o añadir un campo editable

2. **Verificación Backend (opcional):**
   ```bash
   # Actualizar tarifa de un empleado (requiere autenticación)
   curl -X PUT https://19hninc0y7nk.manus.space/api/employees/1/hourly-rate \
     -H "Content-Type: application/json" \
     -H "Cookie: session=..." \
     -d '{"hourly_rate": 45.50}'
   ```

3. **Resultado esperado:**
   - ✅ La tarifa se muestra en el perfil del empleado (solo para admin)
   - ✅ Si no hay tarifa, muestra "No configurada"

---

### **FASE 3: Pruebas de Forecast (Empleado)**

#### **Prueba 3.1: Acceso a Forecast como Empleado**

1. **Acción:**
   - Iniciar sesión como empleado aprobado
   - Navegar a **Forecast** en el menú lateral

2. **Resultado esperado:**
   - ✅ Página de Forecast se carga
   - ✅ Selector de empresa visible
   - ✅ Vista por defecto: "Por Empleado" (su propio forecast)
   - ✅ Selector de mes/año visible

#### **Prueba 3.2: Seleccionar Empresa y Ver Forecast**

1. **Acción:**
   - Seleccionar una empresa del dropdown
   - Seleccionar un mes/año (ej: Enero 2025)
   - Esperar a que se carguen los datos

2. **Resultado esperado:**
   - ✅ Se muestran las métricas principales:
     - Horas Teóricas
     - Horas Reales
     - Eficiencia (%)
     - Valor Económico (si tiene tarifa configurada)
   - ✅ Se muestra el período de facturación correcto según la empresa seleccionada
   - ✅ Desglose de actividades visible

#### **Prueba 3.3: Verificar Cálculo de Horas (Sin Guardias)**

1. **Preparación:**
   - Asegurarse de que el empleado tiene actividades en el calendario:
     - Días normales trabajados
     - Días de vacaciones (V)
     - Días de ausencia (A)
     - Horas de HLD
     - Horas de formación (F)
     - **Horas de guardias (G)** ← IMPORTANTE

2. **Verificación:**
   - Calcular manualmente las horas teóricas del período
   - Calcular manualmente las horas reales:
     - Días normales: horas teóricas
     - Vacaciones: 0 horas
     - Ausencias: 0 horas
     - HLD: horas teóricas - horas HLD
     - Formación: horas teóricas - horas formación
     - **Guardias: NO se suman a horas reales** (solo informativas)

3. **Resultado esperado:**
   - ✅ Horas reales = horas teóricas - vacaciones - ausencias - HLD - formación
   - ✅ Las guardias aparecen en el desglose pero NO se suman a horas reales
   - ✅ Eficiencia = (horas reales / horas teóricas) × 100

#### **Prueba 3.4: Verificar Valor Económico**

1. **Preparación:**
   - Configurar tarifa del empleado (ej: 45.50 €/h)

2. **Verificación:**
   - Valor Económico = Horas Reales × Tarifa

3. **Resultado esperado:**
   - ✅ Valor económico calculado correctamente
   - ✅ Si no hay tarifa, muestra "N/A"

---

### **FASE 4: Pruebas de Forecast (Manager)**

#### **Prueba 4.1: Vista por Equipo**

1. **Acción:**
   - Iniciar sesión como manager
   - Navegar a **Forecast**
   - Seleccionar vista "Por Equipo"
   - Seleccionar su equipo del dropdown

2. **Resultado esperado:**
   - ✅ Se muestra forecast consolidado del equipo
   - ✅ Tabla con todos los empleados del equipo
   - ✅ Métricas agregadas del equipo

#### **Prueba 4.2: Vista por Empleado Individual**

1. **Acción:**
   - Cambiar vista a "Por Empleado"
   - Seleccionar un empleado de su equipo

2. **Resultado esperado:**
   - ✅ Se muestra forecast individual del empleado seleccionado
   - ✅ No puede ver empleados de otros equipos

---

### **FASE 5: Pruebas de Forecast (Admin)**

#### **Prueba 5.1: Vista Global**

1. **Acción:**
   - Iniciar sesión como admin
   - Navegar a **Forecast**
   - Seleccionar vista "Vista Global"

2. **Resultado esperado:**
   - ✅ Se muestra forecast consolidado de todos los empleados
   - ✅ Tabla de equipos con métricas agregadas
   - ✅ Tabla de empleados con forecast individual

#### **Prueba 5.2: Cambiar Período**

1. **Acción:**
   - Usar los botones de navegación (◀ ▶) para cambiar de mes
   - Probar con diferentes meses y años

2. **Resultado esperado:**
   - ✅ El forecast se recalcula para el nuevo período
   - ✅ Las fechas del período de facturación se ajustan correctamente
   - ✅ Si el período cruza meses, se calcula correctamente

---

### **FASE 6: Validación de Cálculos**

#### **Prueba 6.1: Período Normal (1-31)**

1. **Empresa:** Cliente ABC S.L. (Día 1 - Día 31)
2. **Mes:** Enero 2025
3. **Período esperado:** 2025-01-01 a 2025-01-31

#### **Prueba 6.2: Período que Cruza Meses**

1. **Empresa:** Cliente XYZ S.A. (Día 26 - Día 25)
2. **Mes:** Enero 2025
3. **Período esperado:** 2024-12-26 a 2025-01-25

#### **Prueba 6.3: Verificar que Guardias NO se Suman**

1. **Empleado con actividades:**
   - 20 días normales trabajados (8h/día) = 160h teóricas
   - 5 días de vacaciones = 0h
   - 2 días de HLD (4h cada uno) = 160h - 8h = 152h reales
   - 3 días de guardias (2h cada uno) = 6h de guardias

2. **Cálculo esperado:**
   - Horas teóricas: 160h
   - Horas reales: 152h (NO incluye las 6h de guardias)
   - Guardias: 6h (solo informativo)
   - Eficiencia: (152 / 160) × 100 = 95%

---

## 🐛 **CASOS DE ERROR A PROBAR**

### **Error 1: Sin Empresas**

1. **Acción:** Acceder a Forecast sin empresas creadas
2. **Resultado esperado:** Mensaje indicando que no hay empresas disponibles

### **Error 2: Sin Actividades en el Período**

1. **Acción:** Seleccionar un período sin actividades del empleado
2. **Resultado esperado:** 
   - Horas teóricas calculadas correctamente
   - Horas reales = horas teóricas (días normales)
   - Eficiencia = 100%

### **Error 3: Empresa Inactiva**

1. **Acción:** Intentar seleccionar una empresa inactiva
2. **Resultado esperado:** No aparece en el selector (si se filtra `active_only=true`)

---

## 📊 **CHECKLIST DE VALIDACIÓN**

### **Backend:**
- [ ] Endpoint `/api/forecast` responde correctamente
- [ ] Endpoint `/api/admin/companies` permite CRUD completo
- [ ] Endpoint `/api/employees/<id>/hourly-rate` permite actualizar tarifa
- [ ] Los cálculos excluyen guardias de las horas reales
- [ ] Los períodos que cruzan meses se calculan correctamente

### **Frontend:**
- [ ] Página ForecastPage se carga correctamente
- [ ] Selector de empresa funciona
- [ ] Selector de vista funciona según rol
- [ ] Navegación de meses funciona
- [ ] Métricas se muestran correctamente
- [ ] Desglose de actividades es correcto
- [ ] Panel admin de empresas funciona (CRUD)
- [ ] Campo hourly_rate visible solo para admin

### **Cálculos:**
- [ ] Horas teóricas correctas según período
- [ ] Horas reales NO incluyen guardias
- [ ] Eficiencia calculada correctamente
- [ ] Valor económico = horas reales × tarifa
- [ ] Períodos que cruzan meses funcionan

---

## 🔍 **VERIFICACIÓN MANUAL DE CÁLCULOS**

### **Ejemplo de Cálculo Manual:**

**Empleado:**
- Horario: L-J 8h, V 7h
- Tarifa: 45.50 €/h

**Período:** Enero 2025 (1-31)
- Días laborables: 23 días (L-V)
- Horas teóricas: (19 días × 8h) + (4 viernes × 7h) = 152h + 28h = 180h

**Actividades:**
- 5 días vacaciones (V)
- 2 días HLD (4h cada uno)
- 3 días guardias (2h cada uno)
- 1 día formación (4h)

**Cálculo esperado:**
- Horas teóricas: 180h
- Horas reales: 180h - (5 días × 8h) - 8h HLD - 4h formación = 180h - 40h - 8h - 4h = **128h**
- Guardias: 6h (solo informativo, NO se suman)
- Eficiencia: (128 / 180) × 100 = **71.11%**
- Valor económico: 128h × 45.50 €/h = **5,824.00 €**

---

## 📝 **NOTAS IMPORTANTES**

1. **Guardias:** Las guardias NO se suman a las horas reales. Solo aparecen en el desglose como información para el manager.

2. **Períodos que cruzan meses:** Si `billing_period_start_day > billing_period_end_day`, el período va del día de inicio del mes anterior al día de fin del mes actual.

3. **Tarifas:** Solo los administradores pueden ver y configurar las tarifas de los empleados.

4. **Permisos:** 
   - Empleados: Solo pueden ver su propio forecast
   - Managers: Pueden ver forecast de su equipo y empleados individuales de su equipo
   - Admins: Pueden ver todo (vista global, equipos, empleados)

---

## 🚀 **SIGUIENTE PASO**

Una vez completadas todas las pruebas, si todo funciona correctamente:
1. Hacer merge de `feature-forecast-system` a `main`
2. Verificar despliegue automático en producción
3. Realizar pruebas finales en producción

