# Solución: Problemas de Conexión desde Red Móvil 4G

## Problema

Las pruebas funcionan correctamente desde la red WiFi de casa, pero fallan cuando se accede desde un móvil usando red 4G.

## Causas Identificadas

### 1. **CORS Restrictivo**
- El backend solo acepta conexiones desde orígenes específicos
- Los móviles pueden usar diferentes headers de origen o estar detrás de proxies

### 2. **Configuración de Cookies**
- `SameSite=None` requiere `Secure=True` y HTTPS
- Los navegadores móviles tienen políticas más estrictas
- Las cookies pueden no funcionar correctamente en conexiones HTTP desde móviles

### 3. **Proxies de Operadores Móviles**
- Algunos operadores usan proxies que modifican headers
- Headers como `X-Forwarded-Proto` pueden no estar presentes
- NAT puede cambiar la IP de origen

### 4. **Detección de Entorno**
- Si el frontend está en HTTPS (Vercel) pero el backend en HTTP (localhost), hay problemas de contenido mixto

## Soluciones Implementadas

### 1. **CORS Mejorado**
- ✅ Configuración flexible desde variables de entorno
- ✅ Headers adicionales permitidos (`X-Requested-With`, `Origin`, `Accept`)
- ✅ Cache de preflight requests (1 hora)
- ✅ Exposición de headers necesarios

### 2. **Detección de HTTPS Mejorada**
- ✅ Detección de `X-Forwarded-Proto` header
- ✅ Detección de `X-Forwarded-Ssl` header
- ✅ Soporte para proxies de operadores móviles

### 3. **Configuración de Cookies Mejorada**
- ✅ Tiempo de vida de sesión aumentado (24 horas) para conexiones intermitentes
- ✅ Mejor manejo de `SameSite` según el entorno

### 4. **Headers Adicionales para Móviles**
- ✅ `Access-Control-Allow-Credentials` configurado correctamente
- ✅ `Strict-Transport-Security` para conexiones HTTPS
- ✅ Manejo mejorado de peticiones OPTIONS (preflight)

## Configuración Adicional

### Variables de Entorno Opcionales

Puedes agregar orígenes adicionales usando variables de entorno:

```bash
# En .env.development o .env.production
CORS_ADDITIONAL_ORIGINS=https://tu-dominio.com,https://otro-dominio.com
```

O sobrescribir completamente los orígenes:

```bash
CORS_ORIGINS=https://team-time-management.vercel.app,https://tu-dominio.com
```

## Diagnóstico

Para diagnosticar problemas específicos desde móvil:

1. **Abre las herramientas de desarrollador en el móvil**:
   - Chrome: `chrome://inspect`
   - Safari: Activar "Web Inspector" en configuración

2. **Verifica los errores en la consola**:
   - Errores de CORS
   - Errores de cookies
   - Errores de red

3. **Verifica los headers de la petición**:
   - `Origin` header
   - `Referer` header
   - `User-Agent` (puede ser diferente en móvil)

4. **Verifica la URL del backend**:
   - ¿Está usando HTTPS en producción?
   - ¿Está usando HTTP en desarrollo?
   - ¿El frontend y backend están en el mismo dominio/protocolo?

## Recomendaciones

### Para Desarrollo Local desde Móvil

1. **Usa la IP local en lugar de localhost**:
   ```
   http://192.168.1.100:5173  # En lugar de localhost:5173
   ```

2. **Agrega la IP a CORS_ORIGINS**:
   ```bash
   CORS_ADDITIONAL_ORIGINS=http://192.168.1.100:5173
   ```

3. **O usa un túnel público**:
   - ngrok: `ngrok http 5173`
   - Cloudflare Tunnel: `cloudflared tunnel --url http://localhost:5173`

### Para Producción

1. **Asegúrate de que ambos (frontend y backend) usen HTTPS**
2. **Verifica que el dominio de Vercel esté en CORS_ORIGINS**
3. **Verifica que las cookies tengan `Secure=True` y `SameSite=None`**

## Pruebas

Después de aplicar estos cambios:

1. Reinicia el backend
2. Prueba desde el móvil con 4G
3. Verifica los logs del backend para ver los headers recibidos
4. Si sigue fallando, revisa los errores específicos en la consola del móvil

## Notas Adicionales

- Los cambios son compatibles hacia atrás
- No afectan el funcionamiento en redes WiFi
- Mejoran la compatibilidad con diferentes navegadores móviles
- Son especialmente útiles para conexiones desde redes móviles con proxies
