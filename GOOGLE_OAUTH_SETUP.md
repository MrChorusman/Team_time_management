# 🔐 **CONFIGURACIÓN GOOGLE OAUTH - TEAM TIME MANAGEMENT**

Este documento detalla los pasos necesarios para configurar la autenticación con Google OAuth 2.0 en Team Time Management.

---

## 📋 **VARIABLES DE ENTORNO REQUERIDAS**

Para que la aplicación permita autenticación con Google, se deben configurar las siguientes variables de entorno en el archivo `.env`:

### **Variables de Google OAuth**
- **`GOOGLE_CLIENT_ID`**: ID del cliente OAuth de Google
- **`GOOGLE_CLIENT_SECRET`**: Secreto del cliente OAuth de Google
- **`GOOGLE_REDIRECT_URI`**: URI de redirección autorizada

---

## 🔧 **CONFIGURACIÓN EN GOOGLE CLOUD CONSOLE**

### **1. Crear Proyecto en Google Cloud Console**

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Nombra el proyecto (ej: "Team Time Management")

### **2. Habilitar APIs Necesarias**

1. Ve a **"APIs y servicios"** → **"Biblioteca"**
2. Busca y habilita:
   - **Google+ API** (o **Google Identity API**)
   - **People API** (opcional, para información adicional)

### **3. Configurar Pantalla de Consentimiento OAuth**

1. Ve a **"APIs y servicios"** → **"Pantalla de consentimiento OAuth"**
2. Selecciona **"Externo"** para desarrollo
3. Completa la información requerida:
   - **Nombre de la aplicación**: Team Time Management
   - **Email de soporte**: tu-email@empresa.com
   - **Dominio autorizado**: localhost (desarrollo) o tu-dominio.com (producción)
4. Agrega **usuarios de prueba** para desarrollo
5. Guarda y continúa

### **4. Crear Credenciales OAuth 2.0**

1. Ve a **"APIs y servicios"** → **"Credenciales"**
2. Haz clic en **"+ CREAR CREDENCIALES"** → **"ID de cliente OAuth 2.0"**
3. Selecciona **"Aplicación web"**
4. Configura:
   - **Nombre**: Team Time Management Web Client
   - **URIs de redirección autorizados**:
     ```
     http://localhost:3000/auth/google/callback
     https://tu-dominio.com/auth/google/callback
     ```

### **5. Obtener Credenciales**

1. Después de crear, copia:
   - **Client ID**
   - **Client Secret**
2. **⚠️ IMPORTANTE**: Mantén el Client Secret privado

---

## 📝 **CONFIGURACIÓN EN EL PROYECTO**

### **Variables de Entorno**

Agrega al archivo `.env`:

```env
# ===========================================
# CONFIGURACIÓN DE GOOGLE OAUTH
# ===========================================

# Google OAuth 2.0
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Para producción, cambiar a:
# GOOGLE_REDIRECT_URI=https://tu-dominio.com/auth/google/callback
```

---

## 🌐 **ENDPOINTS DISPONIBLES**

### **1. Obtener URL de Autorización**
```http
GET /api/auth/google/url
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

### **2. Manejar Callback**
```http
GET /api/auth/google/callback?code=...&state=...
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Autenticación con Google exitosa",
  "user": {
    "id": 1,
    "email": "usuario@gmail.com",
    "full_name": "Juan Pérez",
    "roles": ["viewer"]
  },
  "employee": null,
  "redirect_url": "/employee/register"
}
```

### **3. Verificar Configuración**
```http
GET /api/auth/google/config
```

**Respuesta:**
```json
{
  "success": true,
  "configured": true,
  "client_id": "123456789...",
  "redirect_uri": "http://localhost:3000/auth/google/callback"
}
```

### **4. Desconectar Cuenta**
```http
POST /api/auth/google/disconnect
Authorization: Bearer <token>
```

---

## 🔄 **FLUJO DE AUTENTICACIÓN**

### **Flujo Completo:**

1. **Frontend solicita URL de autorización**
   ```javascript
   const response = await fetch('/api/auth/google/url');
   const { auth_url } = await response.json();
   ```

2. **Usuario es redirigido a Google**
   ```javascript
   window.location.href = auth_url;
   ```

3. **Usuario autoriza la aplicación en Google**

4. **Google redirige al callback con código**
   ```
   http://localhost:3000/auth/google/callback?code=...&state=...
   ```

5. **Backend intercambia código por token y obtiene información del usuario**

6. **Se crea/inicia sesión del usuario automáticamente**

---

## 🧪 **VERIFICACIÓN DE LA CONFIGURACIÓN**

### **1. Script de Prueba**
Ejecuta el script de prueba incluido:

```bash
cd backend
python test_google_oauth.py
```

### **2. Verificación Manual**
1. Inicia la aplicación
2. Ve a `/api/auth/google/config`
3. Verifica que `configured` sea `true`

---

## 🎨 **INTEGRACIÓN EN EL FRONTEND**

### **Componente de Login con Google**

```jsx
import React from 'react';

const GoogleLoginButton = () => {
  const handleGoogleLogin = async () => {
    try {
      // Obtener URL de autorización
      const response = await fetch('/api/auth/google/url');
      const { auth_url } = await response.json();
      
      if (auth_url) {
        // Redirigir a Google
        window.location.href = auth_url;
      }
    } catch (error) {
      console.error('Error iniciando login con Google:', error);
    }
  };

  return (
    <button 
      onClick={handleGoogleLogin}
      className="google-login-button"
    >
      <img src="/google-icon.svg" alt="Google" />
      Continuar con Google
    </button>
  );
};

export default GoogleLoginButton;
```

### **Manejo del Callback**

```jsx
// En tu componente de callback
useEffect(() => {
  const handleCallback = async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    
    if (code && state) {
      try {
        const response = await fetch(`/api/auth/google/callback?code=${code}&state=${state}`);
        const data = await response.json();
        
        if (data.success) {
          // Usuario autenticado exitosamente
          localStorage.setItem('user', JSON.stringify(data.user));
          window.location.href = data.redirect_url;
        } else {
          console.error('Error en autenticación:', data.message);
        }
      } catch (error) {
        console.error('Error procesando callback:', error);
      }
    }
  };
  
  handleCallback();
}, []);
```

---

## 🔒 **CONSIDERACIONES DE SEGURIDAD**

### **1. Protección de Credenciales**
- Nunca subas el archivo `.env` al repositorio
- Usa variables de entorno en producción
- Rota las credenciales periódicamente

### **2. Validación de Estado**
- El sistema usa `state` para prevenir ataques CSRF
- Cada solicitud genera un estado único
- Se verifica en el callback

### **3. Límites y Cuotas**
- Google tiene límites de solicitudes por día
- Configura alertas de cuota en Google Cloud Console
- Implementa manejo de errores apropiado

### **4. URLs de Redirección**
- Solo URLs autorizadas pueden recibir callbacks
- Verifica que las URLs coincidan exactamente
- Usa HTTPS en producción

---

## 🚀 **CONFIGURACIÓN PARA PRODUCCIÓN**

### **1. Dominio Verificado**
- Verifica tu dominio en Google Search Console
- Agrega el dominio en Google Cloud Console

### **2. Pantalla de Consentimiento**
- Cambia de "Externo" a "Interno" si aplica
- Completa toda la información requerida
- Configura políticas de privacidad y términos

### **3. URLs de Producción**
```env
GOOGLE_REDIRECT_URI=https://tu-dominio.com/auth/google/callback
```

### **4. Configuración de Seguridad**
- Usa HTTPS obligatorio
- Configura headers de seguridad
- Implementa rate limiting

---

## ❓ **SOLUCIÓN DE PROBLEMAS**

### **Error: "redirect_uri_mismatch"**
- Verifica que la URI en `.env` coincida exactamente con la configurada en Google Cloud Console
- Asegúrate de usar el protocolo correcto (http/https)

### **Error: "invalid_client"**
- Verifica que `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` sean correctos
- Asegúrate de que no haya espacios en blanco

### **Error: "access_denied"**
- El usuario canceló la autorización
- Verifica que la pantalla de consentimiento esté configurada

### **Error: "unauthorized_client"**
- El tipo de aplicación no coincide
- Verifica que hayas configurado "Aplicación web"

---

## 📞 **SOPORTE**

Si tienes problemas con la configuración Google OAuth:

1. Revisa los logs de la aplicación
2. Ejecuta el script de prueba
3. Verifica la configuración en Google Cloud Console
4. Consulta la [documentación oficial de Google OAuth](https://developers.google.com/identity/protocols/oauth2)

---

## 🎯 **PRÓXIMOS PASOS**

Una vez configurado Google OAuth:

1. **Probar autenticación** con usuarios de prueba
2. **Integrar en el frontend** con el componente de login
3. **Configurar para producción** con dominio verificado
4. **Implementar logout** con revocación de tokens (opcional)
