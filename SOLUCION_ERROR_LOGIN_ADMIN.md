# Solución: Error de Conexión en Login Admin

## Problema Identificado

El login con el usuario admin está dando error de conexión porque **el backend no está corriendo**. El frontend intenta conectarse a `http://localhost:5001/api` pero el servidor no está disponible.

## Causa Raíz

1. **Backend no iniciado**: El servidor Flask no está corriendo en el puerto 5001
2. **Error de conexión**: El frontend no puede establecer conexión con el backend

## Solución

### Paso 1: Iniciar el Backend

Para iniciar el backend en desarrollo:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

El backend debería iniciarse en `http://localhost:5001`

### Paso 2: Verificar el Usuario Admin

El usuario admin debería tener:
- **Email**: `admin@teamtime.com`
- **Contraseña**: `Admin2025!` (o la que se haya configurado)
- **Estado**: Activo (`active = true`)
- **Email confirmado**: `confirmed_at` no debe ser `null`
- **Rol**: Debe tener el rol `admin`

### Paso 3: Verificar Configuración

1. **Variables de entorno**: Asegúrate de que `.env.development` esté configurado correctamente
2. **Base de datos**: Verifica que la conexión a Supabase esté funcionando
3. **CORS**: El backend está configurado para aceptar conexiones desde `http://localhost:5173` y `http://localhost:3000`

## Mejoras Implementadas

1. **Manejo de errores mejorado**: El frontend ahora muestra mensajes más descriptivos cuando el backend no está disponible
2. **Logs mejorados**: Se agregaron logs más detallados para diagnosticar problemas de conexión

## Verificación

Una vez que el backend esté corriendo:

1. Abre el navegador en `http://localhost:5173` (o el puerto que uses para el frontend)
2. Intenta hacer login con:
   - Email: `admin@teamtime.com`
   - Contraseña: `Admin2025!`
3. Si el login falla, verifica:
   - Que el backend esté corriendo (deberías ver logs en la consola)
   - Que el usuario admin exista en la base de datos
   - Que el usuario tenga el rol `admin` y esté activo

## Scripts de Diagnóstico

Se crearon scripts para diagnosticar problemas:

- `backend/diagnose_admin_login.py`: Verifica el estado del usuario admin
- `backend/check_admin_user.py`: Verifica la configuración del usuario admin

## Notas Adicionales

- Si estás en **producción**, el backend debería estar corriendo en Render (`https://team-time-management.onrender.com`)
- Si estás en **desarrollo**, necesitas iniciar el backend localmente
- El frontend detecta automáticamente el entorno y se conecta al backend correspondiente
