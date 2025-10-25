# Guía de Despliegue - Team Time Management

## Tabla de Contenidos
- [Despliegue en Render (Backend)](#despliegue-en-render-backend)
- [Despliegue en Vercel (Frontend)](#despliegue-en-vercel-frontend)
- [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
- [Verificación Post-Despliegue](#verificación-post-despliegue)
- [Rollback en Caso de Problemas](#rollback-en-caso-de-problemas)
- [Monitoreo y Logs](#monitoreo-y-logs)

---

## Despliegue en Render (Backend)

### 1. Preparación del Repositorio

```bash
# Asegúrate de que el código esté en la rama main
git checkout main
git pull origin main

# Verifica que el Procfile esté en la raíz del proyecto
cat Procfile
# Debe contener: web: cd backend && gunicorn main:app --bind 0.0.0.0:$PORT
```

### 2. Crear Servicio en Render

1. **Accede a Render Dashboard**: https://dashboard.render.com/
2. **Crear nuevo Web Service**:
   - Conecta tu repositorio de GitHub
   - Selecciona la rama `main`
   - Configuración básica:
     - **Name**: `team-time-management`
     - **Runtime**: `Python 3`
     - **Build Command**: `cd backend && pip install -r requirements.txt`
     - **Start Command**: *(dejar vacío para usar Procfile)*

### 3. Configurar Variables de Entorno

En Render Dashboard > Environment:

```env
# Configuración básica
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
SECURITY_PASSWORD_SALT=tu-salt-para-contraseñas
FLASK_ENV=production
FLASK_DEBUG=false

# Base de datos Supabase
SUPABASE_HOST=aws-0-eu-west-3.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_DB=postgres
SUPABASE_USER=postgres.xmaxohyxgsthligskjvg
SUPABASE_DB_PASSWORD=tu-password-de-supabase

# Google OAuth
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret
GOOGLE_REDIRECT_URI=https://team-time-management.onrender.com/api/auth/google/callback

# Email SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password-de-gmail
MOCK_EMAIL_MODE=false

# CORS
CORS_ORIGINS=https://team-time-management.vercel.app

# Logging
LOG_LEVEL=INFO
```

### 4. Configuración Avanzada

- **Plan**: Starter (gratuito) o Standard (recomendado para producción)
- **Region**: Oregon (más cercano a Supabase)
- **Auto-Deploy**: Habilitado para rama `main`

---

## Despliegue en Vercel (Frontend)

### 1. Preparación del Frontend

```bash
# Asegúrate de estar en el directorio frontend
cd frontend

# Instala dependencias
npm install

# Construye el proyecto localmente para verificar
npm run build
```

### 2. Conectar con Vercel

1. **Accede a Vercel Dashboard**: https://vercel.com/dashboard
2. **Import Project**:
   - Conecta tu repositorio de GitHub
   - Selecciona el directorio `frontend`
   - Framework: `Vite`

### 3. Configurar Variables de Entorno

En Vercel Dashboard > Settings > Environment Variables:

```env
# API Backend
VITE_API_BASE_URL=https://team-time-management.onrender.com

# Google OAuth
VITE_GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com

# Entorno
VITE_IS_PRODUCTION=true
```

### 4. Configuración de Build

- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

---

## Configuración de Variables de Entorno

### Script de Validación

Antes del despliegue, valida tu configuración:

```bash
# En el directorio backend
python scripts/validate_env.py
```

Este script verificará:
- ✅ Variables de Flask configuradas
- ✅ Conexión a base de datos
- ✅ Configuración de Google OAuth
- ✅ Configuración de SMTP
- ✅ Variables de CORS
- ✅ Configuración de logging

### Generación de Datos Realistas

Después del despliegue, genera datos de prueba:

```bash
# En el directorio backend
python scripts/create_realistic_data.py
```

Esto creará:
- 10 equipos realistas
- 10 managers
- 50+ empleados
- Actividades de calendario
- Notificaciones
- Festivos por país

---

## Verificación Post-Despliegue

### 1. Verificar Backend

```bash
# Health check
curl https://team-time-management.onrender.com/api/health

# Información de la aplicación
curl https://team-time-management.onrender.com/api/info
```

**Respuesta esperada**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.1",
  "environment": "production",
  "diagnostics": {
    "sqlalchemy": "healthy",
    "psycopg2": {"status": "healthy"},
    "google_oauth": {"status": "configured"},
    "email": {"status": "configured"}
  }
}
```

### 2. Verificar Frontend

1. **Accede a la URL**: https://team-time-management.vercel.app
2. **Verifica funcionalidades**:
   - ✅ Página de login carga correctamente
   - ✅ Botón de Google OAuth visible
   - ✅ Formulario de login funcional
   - ✅ Redirección a dashboard después del login

### 3. Pruebas de Integración

```bash
# Login con credenciales de prueba
curl -X POST https://team-time-management.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ana.garcia@company.com", "password": "password123"}'

# Verificar Google OAuth
curl https://team-time-management.onrender.com/api/auth/google/config
```

---

## Rollback en Caso de Problemas

### Backend (Render)

1. **Rollback automático**:
   - Render mantiene las últimas 5 versiones
   - Ve a Dashboard > Deploys
   - Selecciona una versión anterior
   - Click "Redeploy"

2. **Rollback manual**:
   ```bash
   # Revertir a commit anterior
   git revert HEAD
   git push origin main
   ```

### Frontend (Vercel)

1. **Rollback automático**:
   - Vercel mantiene historial de deploys
   - Ve a Dashboard > Deployments
   - Selecciona versión anterior
   - Click "Promote to Production"

2. **Rollback manual**:
   ```bash
   # Revertir cambios
   git revert HEAD
   git push origin main
   ```

---

## Monitoreo y Logs

### Render Dashboard

1. **Logs en tiempo real**:
   - Ve a tu servicio en Render
   - Click en "Logs" tab
   - Monitorea errores y warnings

2. **Métricas**:
   - CPU y memoria
   - Requests por minuto
   - Response times

### Vercel Analytics

1. **Performance**:
   - Core Web Vitals
   - Page load times
   - User experience

2. **Usage**:
   - Page views
   - Unique visitors
   - Geographic distribution

### Endpoints de Monitoreo

```bash
# Health check detallado
curl https://team-time-management.onrender.com/api/health

# Métricas del sistema (requiere autenticación admin)
curl -H "Authorization: Bearer <token>" \
  https://team-time-management.onrender.com/api/admin/metrics

# Logs del sistema (requiere autenticación admin)
curl -H "Authorization: Bearer <token>" \
  https://team-time-management.onrender.com/api/admin/logs
```

---

## Troubleshooting Común

### Backend no inicia

**Problema**: Error 500 en Render
**Solución**:
1. Verificar logs en Render Dashboard
2. Comprobar variables de entorno
3. Ejecutar `python scripts/validate_env.py`

### Frontend no carga

**Problema**: Error 404 en Vercel
**Solución**:
1. Verificar configuración de build
2. Comprobar variables de entorno
3. Revisar `vercel.json`

### Base de datos no conecta

**Problema**: Error de conexión a Supabase
**Solución**:
1. Verificar credenciales en Supabase Dashboard
2. Comprobar Transaction Pooler habilitado
3. Verificar variables de entorno

### Google OAuth no funciona

**Problema**: Error de autenticación
**Solución**:
1. Verificar URLs autorizadas en Google Cloud Console
2. Comprobar CLIENT_ID y CLIENT_SECRET
3. Verificar REDIRECT_URI

---

## Checklist de Despliegue

### Pre-Despliegue
- [ ] Código en rama `main`
- [ ] Tests pasando localmente
- [ ] Variables de entorno configuradas
- [ ] Script de validación ejecutado
- [ ] Documentación actualizada

### Despliegue Backend
- [ ] Servicio creado en Render
- [ ] Variables de entorno configuradas
- [ ] Build exitoso
- [ ] Health check respondiendo
- [ ] Logs sin errores críticos

### Despliegue Frontend
- [ ] Proyecto importado en Vercel
- [ ] Variables de entorno configuradas
- [ ] Build exitoso
- [ ] Página carga correctamente
- [ ] Login funcional

### Post-Despliegue
- [ ] Datos realistas generados
- [ ] Pruebas de integración pasando
- [ ] Monitoreo configurado
- [ ] Documentación actualizada
- [ ] Equipo notificado

---

## Contacto y Soporte

- **Documentación**: Ver `README.md` y `PLAN_DESARROLLO_FASES_FUTURAS.md`
- **Issues**: Crear issue en GitHub para problemas técnicos
- **Logs**: Revisar logs en Render/Vercel Dashboard
- **Monitoreo**: Usar endpoints `/api/health` y `/api/admin/metrics`
