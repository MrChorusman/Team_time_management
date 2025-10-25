# 🔧 GUÍA DE CONFIGURACIÓN GOOGLE CLOUD CONSOLE

## 📋 **PASOS DETALLADOS PARA CONFIGURAR GOOGLE OAUTH**

### **PASO 1: Crear Proyecto en Google Cloud Console**

1. **Acceder a Google Cloud Console**
   - Ir a: https://console.cloud.google.com/
   - Iniciar sesión con cuenta de Google

2. **Crear nuevo proyecto**
   - Clic en "Seleccionar proyecto" (arriba izquierda)
   - Clic en "NUEVO PROYECTO"
   - Nombre: `Team Time Management`
   - ID: `team-time-management-[número]`
   - Clic en "CREAR"

### **PASO 2: Habilitar APIs Necesarias**

1. **Ir a APIs y Servicios**
   - En el menú lateral: "APIs y servicios" > "Biblioteca"

2. **Habilitar Google+ API**
   - Buscar: "Google+ API"
   - Clic en "HABILITAR"

3. **Habilitar Google Identity API**
   - Buscar: "Google Identity"
   - Clic en "HABILITAR"

### **PASO 3: Configurar Credenciales OAuth 2.0**

1. **Ir a Credenciales**
   - En el menú lateral: "APIs y servicios" > "Credenciales"

2. **Crear credenciales OAuth 2.0**
   - Clic en "+ CREAR CREDENCIALES"
   - Seleccionar "ID de cliente de OAuth 2.0"

3. **Configurar pantalla de consentimiento**
   - Si es la primera vez: "CONFIGURAR PANTALLA DE CONSENTIMIENTO"
   - Tipo de usuario: "Externo"
   - Información de la aplicación:
     - Nombre: `Team Time Management`
     - Email de soporte: `tu-email@ejemplo.com`
     - Dominio autorizado: `team-time-management.onrender.com`
   - Clic en "GUARDAR Y CONTINUAR"

4. **Configurar alcances**
   - Clic en "AGREGAR O QUITAR ALCANCES"
   - Seleccionar:
     - `../auth/userinfo.email`
     - `../auth/userinfo.profile`
     - `openid`
   - Clic en "ACTUALIZAR"

5. **Agregar usuarios de prueba**
   - Clic en "AGREGAR USUARIOS"
   - Agregar emails de administradores
   - Clic en "GUARDAR Y CONTINUAR"

### **PASO 4: Crear ID de Cliente OAuth 2.0**

1. **Configurar aplicación**
   - Tipo de aplicación: "Aplicación web"
   - Nombre: `Team Time Management Web`

2. **Configurar URIs de redirección autorizadas**
   ```
   http://localhost:5001/api/auth/google/callback
   https://team-time-management.onrender.com/api/auth/google/callback
   ```

3. **Crear credenciales**
   - Clic en "CREAR"
   - **GUARDAR** el Client ID y Client Secret

### **PASO 5: Configurar Variables de Entorno**

#### **Backend (.env)**
```bash
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_REDIRECT_URI=https://team-time-management.onrender.com/api/auth/google/callback
```

#### **Frontend (.env.production)**
```bash
VITE_GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
```

#### **Render.com (Variables de Entorno)**
```
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_REDIRECT_URI=https://team-time-management.onrender.com/api/auth/google/callback
VITE_GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
```

### **PASO 6: Verificación**

1. **Ejecutar script de verificación**
   ```bash
   python backend/scripts/pre-deploy-check.py
   ```

2. **Resultado esperado**
   ```
   ✅ LISTO PARA PRODUCCIÓN
   📝 El botón mostrará: 'Continuar con Google'
   🚀 Google OAuth real estará activo
   ```

## 🚨 **PROBLEMAS COMUNES Y SOLUCIONES**

### **Error: "redirect_uri_mismatch"**
- **Causa**: URI de redirección no coincide
- **Solución**: Verificar URIs en Google Cloud Console

### **Error: "invalid_client"**
- **Causa**: Client ID o Secret incorrectos
- **Solución**: Verificar variables de entorno

### **Error: "access_denied"**
- **Causa**: Usuario no autorizado
- **Solución**: Agregar usuario a usuarios de prueba

### **Botón no aparece**
- **Causa**: Variables no configuradas
- **Solución**: Configurar VITE_GOOGLE_CLIENT_ID

## 📞 **SOPORTE**

### **En caso de problemas**:
1. **Verificar configuración**: Ejecutar script de verificación
2. **Revisar logs**: Comprobar errores en Render.com
3. **Probar localmente**: Con credenciales reales
4. **Documentar error**: Para futuras referencias

### **Recursos útiles**:
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Render.com Environment Variables](https://render.com/docs/environment-variables)
