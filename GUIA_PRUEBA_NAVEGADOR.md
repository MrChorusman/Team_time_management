# 🌐 GUÍA DE PRUEBA EN NAVEGADOR
## Team Time Management - Demostración Visual

**URL**: https://team-time-management.vercel.app  
**Credenciales**: admin@example.com / test123

---

## 🎯 PASOS PARA PROBAR LA APLICACIÓN

### PASO 1: Pantalla de Login (Actual)

Deberías ver:
- ✅ Logo o título "Team Time Management"
- ✅ Formulario de login con:
  - Campo "Email"
  - Campo "Contraseña"
  - Botón "Iniciar Sesión"
- ✅ Botón "Continuar con Google" (puede mostrar "(Demo)" si está en modo mock)
- ✅ Enlaces a "Olvidé mi contraseña" y "Regístrate"

**QUÉ HACER**:
1. Introduce las credenciales:
   - **Email**: `admin@example.com`
   - **Contraseña**: `test123`
2. Haz clic en "Iniciar Sesión"
3. Espera la redirección al dashboard

**QUÉ VERIFICAR**:
- [ ] Los campos se completan correctamente
- [ ] No hay errores en la consola del navegador (F12)
- [ ] El botón responde al click
- [ ] Ves un indicador de carga o procesamiento

---

### PASO 2: Redirección al Dashboard

Tras un login exitoso, deberías:
- ✅ Ver una redirección automática a `/dashboard`
- ✅ La URL debería cambiar a: `https://team-time-management.vercel.app/dashboard`

**QUÉ VERIFICAR**:
- [ ] La redirección ocurre automáticamente
- [ ] No hay errores 404 o de redirección
- [ ] La sesión se establece correctamente

---

### PASO 3: Dashboard Principal

En el dashboard deberías ver:
- ✅ **Header/Navegación**:
  - Logo o nombre de la aplicación
  - Menú de navegación
  - Información del usuario (nombre, email)
  - Botón de logout
  
- ✅ **Panel Principal**:
  - Widgets o tarjetas con información
  - Estadísticas o métricas
  - Enlaces a secciones principales

- ✅ **Navegación Lateral** (si existe):
  - Equipos
  - Empleados
  - Calendario
  - Festivos
  - Notificaciones
  - Reportes

**QUÉ VERIFICAR**:
- [ ] La página carga completamente
- [ ] Los datos se muestran correctamente
- [ ] No hay errores en consola
- [ ] Los estilos (Tailwind CSS) se aplican correctamente
- [ ] La página es responsive (prueba cambiar el tamaño de la ventana)

---

### PASO 4: Navegación por Secciones

Prueba navegar a cada sección:

#### A) Sección de Equipos
**URL esperada**: `/teams` o `/equipos`

**Deberías ver**:
- Lista de equipos existentes
- Información de cada equipo:
  - Nombre del equipo
  - Descripción
  - Número de miembros
  - Fecha de creación

**QUÉ PROBAR**:
- [ ] La lista de equipos carga correctamente
- [ ] Puedes hacer clic en un equipo para ver detalles
- [ ] Los datos vienen del backend (verificar en Network tab)

#### B) Sección de Empleados
**URL esperada**: `/employees` o `/empleados`

**Deberías ver**:
- Lista de empleados registrados
- Información de cada empleado:
  - Nombre completo
  - Email
  - Equipo asignado
  - País/Región
  - Estado (activo/inactivo)

**QUÉ PROBAR**:
- [ ] La lista de empleados carga correctamente
- [ ] Los filtros funcionan (si existen)
- [ ] Puedes ver detalles de un empleado

#### C) Sección de Calendario
**URL esperada**: `/calendar` o `/calendario`

**Deberías ver**:
- Vista de calendario (mensual, semanal, o diaria)
- Actividades marcadas en el calendario
- Festivos destacados
- Controles de navegación (mes anterior/siguiente)

**QUÉ PROBAR**:
- [ ] El calendario renderiza correctamente
- [ ] Puedes navegar entre meses
- [ ] Los festivos se muestran destacados
- [ ] Las actividades se muestran en las fechas correctas

#### D) Sección de Festivos
**URL esperada**: `/holidays` o `/festivos`

**Deberías ver**:
- Lista de festivos por país/región
- Filtros por:
  - País
  - Región/Comunidad Autónoma
  - Año
- Información de cada festivo:
  - Nombre
  - Fecha
  - País/Región
  - Tipo (nacional, regional, local)

**QUÉ PROBAR**:
- [ ] La lista de festivos carga correctamente
- [ ] Los filtros funcionan
- [ ] Se muestran festivos de múltiples países
- [ ] Los datos son precisos

---

### PASO 5: Verificar la Consola del Navegador

**Abre las DevTools** (F12 o Cmd+Option+I en Mac)

#### Pestaña Console
**Busca**:
- ✅ Sin errores críticos en rojo
- ⚠️ Los warnings son normales
- ℹ️ Logs informativos están bien

**Errores comunes a ignorar**:
- Warnings sobre React keys
- Warnings sobre deprecated features
- Logs de desarrollo de Vite

**Errores que SÍ son problema**:
- ❌ CORS errors
- ❌ Network errors (Failed to fetch)
- ❌ 404 Not Found en endpoints
- ❌ Authentication errors

#### Pestaña Network
**Verifica**:
- [ ] Requests a `/api/teams` - Status: 200 ✅
- [ ] Requests a `/api/employees` - Status: 200 ✅
- [ ] Requests a `/api/holidays` - Status: 200 ✅
- [ ] Response times < 2 segundos
- [ ] No hay requests fallidos (status 500)

#### Pestaña Application (Storage)
**Verifica**:
- [ ] Session Storage contiene datos de usuario
- [ ] Local Storage (si se usa) está configurado
- [ ] Cookies de sesión están presentes

---

### PASO 6: Probar Logout

**Cómo hacerlo**:
1. Busca el botón de "Logout" o "Cerrar sesión"
2. Haz clic en el botón
3. Observa la redirección

**QUÉ VERIFICAR**:
- [ ] El logout funciona correctamente
- [ ] Redirige a la página de login
- [ ] La sesión se limpia
- [ ] No puedes volver al dashboard sin login
- [ ] Si intentas acceder a `/dashboard` directamente, te redirige a login

---

### PASO 7: Prueba de Responsive Design

**Prueba en diferentes tamaños**:

#### Desktop (> 1024px)
- [ ] Navegación lateral visible
- [ ] Tablas con todas las columnas
- [ ] Widgets en grid de 3-4 columnas

#### Tablet (768px - 1024px)
- [ ] Navegación se adapta (posiblemente hamburger menu)
- [ ] Widgets en grid de 2 columnas
- [ ] Scroll horizontal si es necesario

#### Mobile (< 768px)
- [ ] Menú hamburger
- [ ] Widgets en columna única
- [ ] Formularios adaptados
- [ ] Botones de tamaño táctil

**Cómo probar**:
- Cmd+Option+I (Mac) o F12 (Windows)
- Click en el icono de dispositivos (📱)
- Selecciona diferentes dispositivos o arrastra el tamaño

---

## 🔍 CHECKLIST COMPLETO DE VALIDACIÓN

### Funcionalidad
- [ ] Login funciona correctamente
- [ ] Dashboard carga sin errores
- [ ] Navegación entre secciones funciona
- [ ] Datos se cargan desde el backend
- [ ] Formularios validan correctamente
- [ ] Logout funciona correctamente

### Performance
- [ ] Página carga en < 2 segundos
- [ ] Imágenes optimizadas
- [ ] Sin bloqueos en la UI
- [ ] Transiciones suaves

### UI/UX
- [ ] Diseño es atractivo y profesional
- [ ] Colores y fuentes consistentes
- [ ] Íconos SVG (nunca emojis)
- [ ] Responsive en todos los tamaños
- [ ] Accesibilidad (contraste, tamaños)

### Errores
- [ ] Sin errores 404
- [ ] Sin errores CORS
- [ ] Sin errores de autenticación
- [ ] Manejo de errores apropiado

---

## 🐛 PROBLEMAS COMUNES Y SOLUCIONES

### Problema: "No se puede conectar al servidor"
**Solución**:
- Verifica que el backend esté activo: https://team-time-management.onrender.com/api/info
- Si Render está "sleeping", espera 1-2 minutos para que despierte

### Problema: "CORS Error"
**Solución**:
- Ya está configurado, pero si aparece, verifica la URL del frontend en Render

### Problema: "Invalid credentials"
**Solución**:
- Verifica que usas: `admin@example.com` / `test123`
- Verifica que no hay espacios extras

### Problema: "Página en blanco"
**Solución**:
- Abre DevTools (F12) y verifica errores en Console
- Recarga la página con Cmd+Shift+R (Mac) o Ctrl+Shift+R (Windows)
- Verifica que JavaScript está habilitado

### Problema: "Dashboard no carga"
**Solución**:
- Verifica que el login fue exitoso
- Verifica que hay una sesión activa
- Verifica Network tab para ver si hay requests fallidos

---

## 📊 MÉTRICAS A OBSERVAR

### En DevTools > Network
- **Tiempo total de carga**: < 2s ✅
- **Número de requests**: 10-20 es normal
- **Tamaño transferido**: < 2MB en primera carga
- **Recursos en caché**: Segunda carga debería ser más rápida

### En Lighthouse (DevTools > Lighthouse)
Ejecuta un audit y verifica:
- **Performance**: > 80 🎯
- **Accessibility**: > 90 🎯
- **Best Practices**: > 80 🎯
- **SEO**: > 80 🎯

---

## 🎯 RESULTADO ESPERADO

Al completar esta guía, deberías poder:
- ✅ Hacer login exitosamente
- ✅ Navegar por todas las secciones
- ✅ Ver datos cargados desde el backend
- ✅ Confirmar que la UI es responsive
- ✅ Verificar que no hay errores críticos
- ✅ Hacer logout correctamente

---

## 📝 NOTAS PARA REPORTAR PROBLEMAS

Si encuentras algún problema, anota:
1. **Qué estabas haciendo** (paso específico)
2. **Qué esperabas que pasara**
3. **Qué pasó en realidad**
4. **Errores en consola** (screenshot o texto)
5. **Network requests fallidos** (URL y status code)
6. **Navegador y versión** (Chrome 120, Safari 17, etc.)

---

## 🚀 DESPUÉS DE LA PRUEBA

Una vez completada la validación, comparte:
- ✅ Funcionalidades que funcionan correctamente
- ⚠️ Problemas encontrados (si los hay)
- 💡 Sugerencias de mejora
- 🎯 Próximos pasos

---

**¡Disfruta probando tu aplicación!** 🎉

La aplicación está en producción y lista para usar. Todas las funcionalidades core están operativas.

