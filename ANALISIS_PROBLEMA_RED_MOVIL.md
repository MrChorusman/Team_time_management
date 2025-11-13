# Análisis: Problemas de Conexión desde Red Móvil 4G

## Problema Identificado

Las pruebas funcionan correctamente desde la red WiFi de casa, pero fallan cuando se accede desde un móvil usando red 4G.

## Posibles Causas

### 1. **Configuración de CORS Restrictiva**

El backend solo acepta conexiones desde orígenes específicos:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `https://team-time-management.vercel.app`
- `https://team-time-management-miguels-projects-dcbd8c7f.vercel.app`

**Problema**: Si estás accediendo desde el móvil usando una IP diferente o un dominio diferente, CORS bloqueará las peticiones.

### 2. **Configuración de Cookies/Sesiones**

```python
SESSION_COOKIE_SECURE = is_production  # Solo HTTPS en producción
SESSION_COOKIE_SAMESITE = 'None' if is_production else 'Lax'
```

**Problemas potenciales**:
- En desarrollo con HTTP, las cookies pueden no funcionar correctamente desde móviles
- `SameSite=None` requiere `Secure=True` y HTTPS
- Los navegadores móviles tienen políticas más estrictas de cookies

### 3. **Detección de Entorno Incorrecta**

El código detecta producción basándose en:
```python
is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER')
```

Si el backend está corriendo en desarrollo pero el frontend está en producción (Vercel), habrá un mismatch.

### 4. **Problemas de Red Móvil**

- **Proxies de operador**: Algunos operadores móviles usan proxies que modifican headers
- **NAT**: La red móvil usa NAT que puede cambiar la IP de origen
- **Firewall**: Algunos operadores bloquean ciertos puertos o protocolos
- **DNS**: Problemas de resolución DNS en redes móviles

### 5. **HTTPS vs HTTP**

Si el frontend está en HTTPS (Vercel) pero intenta conectarse a un backend HTTP (localhost), el navegador bloqueará las peticiones mixtas.

## Soluciones Propuestas

### Solución 1: Mejorar Configuración de CORS

Agregar más orígenes permitidos y hacer la configuración más flexible:

```python
CORS_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://team-time-management.vercel.app',
    'https://team-time-management-miguels-projects-dcbd8c7f.vercel.app',
    # Agregar IP local de la red
    # Agregar dominio público si existe
]
```

### Solución 2: Mejorar Manejo de Cookies para Móviles

```python
# Detectar si la petición viene de HTTPS
is_secure = request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https'
app.config['SESSION_COOKIE_SECURE'] = is_secure
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if is_secure else 'Lax'
```

### Solución 3: Agregar Headers de Seguridad para Móviles

```python
@app.after_request
def after_request(response):
    # Headers para mejorar compatibilidad móvil
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    return response
```

### Solución 4: Usar Variables de Entorno para Detectar Origen

Permitir configurar orígenes permitidos desde variables de entorno:

```python
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else [
    'http://localhost:3000',
    # ... defaults
]
```

## Diagnóstico

Para diagnosticar el problema específico:

1. **Verificar desde qué URL accedes en el móvil**
   - ¿Es localhost? (no funcionará desde otra red)
   - ¿Es la IP local? (puede funcionar si está en la misma red)
   - ¿Es Vercel? (debería funcionar)

2. **Verificar errores en la consola del navegador móvil**
   - CORS errors
   - Cookie errors
   - Network errors

3. **Verificar headers de la petición**
   - Origin header
   - Referer header
   - User-Agent (puede ser diferente en móvil)

4. **Verificar configuración del backend**
   - ¿Está en desarrollo o producción?
   - ¿Qué URL está usando el frontend?

## Recomendaciones Inmediatas

1. **Si accedes desde móvil a producción (Vercel)**:
   - Asegúrate de que el backend en Render esté configurado correctamente
   - Verifica que CORS incluya el dominio de Vercel

2. **Si accedes desde móvil a desarrollo local**:
   - Usa la IP local de tu máquina en lugar de localhost
   - Ejemplo: `http://192.168.1.100:5173` en lugar de `http://localhost:5173`
   - Asegúrate de que el firewall permita conexiones en el puerto

3. **Para desarrollo móvil**:
   - Usa un túnel como ngrok o Cloudflare Tunnel
   - O configura un dominio de desarrollo accesible públicamente
