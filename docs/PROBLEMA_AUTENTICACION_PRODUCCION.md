# Problema de Autenticación en Producción

**Fecha**: 29 de Enero, 2026  
**Estado**: 🔴 CRÍTICO - Bloquea pruebas automatizadas

---

## 📋 Resumen

Los usuarios de prueba han sido creados exitosamente en producción, pero el login falla con error "Credenciales inválidas" aunque:
- Los usuarios existen en la base de datos
- Las contraseñas están hasheadas correctamente
- La verificación funciona localmente

---

## 🔍 Diagnóstico Realizado

### 1. Verificación de Usuarios en Producción

```sql
SELECT email, active, confirmed_at 
FROM "user" 
WHERE email IN ('admin.test@example.com', 'employee.test@example.com');
```

**Resultado**: ✅ Ambos usuarios existen y están activos
- `admin.test@example.com`: activo, confirmado el 2026-01-29 13:02:43
- `employee.test@example.com`: activo, confirmado el 2026-01-29 13:02:44

### 2. Verificación de Hash de Contraseña

**Localmente (con configuración de producción)**:
```python
from flask_security.utils import verify_password
verify_password('AdminTest123!', user.password)  # ✅ Retorna True
```

**En producción (vía HTTP)**:
```bash
curl -X POST https://team-time-management.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin.test@example.com","password":"AdminTest123!"}'
```

**Resultado**: ❌ Retorna `{"success":false,"message":"Credenciales inválidas"}`

### 3. Configuración Verificada

**Local (usando .env.production)**:
- `SECRET_KEY`: `production-secret-key-change-me`
- `SECURITY_PASSWORD_SALT`: `production-salt-change-me`
- `SECURITY_PASSWORD_HASH`: `pbkdf2_sha512`

**Producción (Render)**:
- ⚠️ Desconocido - requiere verificación en Render Dashboard

---

## 🎯 Posibles Causas

### Causa 1: Diferencia en SECRET_KEY

El `SECRET_KEY` en Render podría ser diferente al usado localmente. Aunque el hash de contraseña con `pbkdf2_sha512` no debería depender directamente del `SECRET_KEY`, Flask-Security podría usarlo para otras verificaciones.

### Causa 2: Diferencia en SECURITY_PASSWORD_SALT

El `SECURITY_PASSWORD_SALT` es crítico para la generación y verificación de hashes. Si Render tiene un valor diferente, los hashes no coincidirán.

### Causa 3: Configuración de Flask-Security Diferente

El servidor de Render podría estar usando una configuración diferente de Flask-Security que afecta la verificación de contraseñas.

---

## 🔧 Soluciones Propuestas

### Solución 1: Verificar y Sincronizar Variables de Entorno en Render

1. Acceder a Render Dashboard
2. Ir a Environment Variables del servicio backend
3. Verificar valores de:
   - `SECRET_KEY`
   - `SECURITY_PASSWORD_SALT`
4. Si son diferentes, actualizar para que coincidan con `.env.production`
5. Redeploy del servicio

### Solución 2: Ejecutar Script de Actualización en Render

Crear un script que se ejecute directamente en Render para actualizar las contraseñas usando la configuración exacta del servidor:

```python
# backend/scripts/fix_passwords_in_render.py
# Este script debe ejecutarse en el contexto de Render
# para usar las mismas variables de entorno que el servidor
```

### Solución 3: Actualizar Contraseñas vía SQL Directo

Usar Supabase SQL Editor para actualizar las contraseñas con hashes generados usando la configuración exacta de Render:

1. Obtener `SECRET_KEY` y `SECURITY_PASSWORD_SALT` de Render
2. Generar hash localmente con esos valores
3. Actualizar directamente en Supabase

---

## 📝 Pasos Inmediatos Recomendados

1. **Verificar variables de entorno en Render**:
   - Acceder a Render Dashboard
   - Verificar `SECRET_KEY` y `SECURITY_PASSWORD_SALT`
   - Comparar con valores en `.env.production`

2. **Si los valores son diferentes**:
   - Actualizar variables en Render para que coincidan
   - O actualizar `.env.production` local para que coincida con Render
   - Regenerar hashes de contraseña con la configuración correcta

3. **Probar login nuevamente**:
   ```bash
   curl -X POST https://team-time-management.onrender.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin.test@example.com","password":"AdminTest123!"}'
   ```

4. **Una vez resuelto**:
   - Ejecutar pruebas de regresión automatizadas
   - Ejecutar estudio de rendimiento
   - Continuar con el resto del plan

---

## 🚨 Impacto

Este problema bloquea:
- ❌ Pruebas de regresión automatizadas (`regression_tests.py`)
- ❌ Estudio de rendimiento (`performance_study.py`)
- ⚠️ Pruebas manuales (pueden proceder con usuarios existentes si se resuelve el login)

---

## 📚 Referencias

- Script de creación de usuarios: `backend/scripts/create_test_users.py`
- Configuración de producción: `backend/.env.production`
- Endpoint de login: `backend/app/auth.py` (línea 19)
- Documentación Flask-Security: https://flask-security-too.readthedocs.io/
