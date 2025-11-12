# 📧 SendGrid: Verificación de Remitente Requerida

## ⚠️ Problema Actual

La aplicación **NO puede enviar emails** porque SendGrid requiere que verifiques tu email de remitente antes de permitir envíos.

### Estado Actual:
- ✅ Variables SMTP configuradas correctamente en Render
- ✅ `MOCK_EMAIL_MODE=false` 
- ✅ Código del backend configurado para usar SendGrid
- ❌ **SendGrid está rechazando los envíos porque `miguelchis@gmail.com` no está verificado**

---

## 🔧 Solución: Verificar el Remitente en SendGrid

Sigue estos pasos para verificar tu email y habilitar el envío de emails:

### 1️⃣ **Accede a SendGrid Dashboard**
- Ve a: https://app.sendgrid.com/
- Inicia sesión con tu cuenta

### 2️⃣ **Navega a Sender Authentication**
- En el menú lateral izquierdo, busca **"Settings"**
- Click en **"Sender Authentication"**

### 3️⃣ **Opción A: Verificar Single Sender (Recomendado para desarrollo)**

Esta es la opción más rápida para empezar:

1. En "Sender Authentication", haz click en **"Verify a Single Sender"**
2. Haz click en **"Create New Sender"**
3. Completa el formulario:
   - **From Name:** Team Time Management (o el nombre que quieras)
   - **From Email Address:** `miguelchis@gmail.com`
   - **Reply To:** `miguelchis@gmail.com` (puede ser el mismo)
   - **Company Address:** Tu dirección
   - **City, State, Zip:** Tu ciudad, estado, código postal
   - **Country:** España (o tu país)
   - **Nickname:** Production Sender (cualquier nombre interno)
4. Haz click en **"Create"**
5. **Revisa tu Gmail (`miguelchis@gmail.com`)**:
   - Recibirás un email de SendGrid con asunto: **"Please Verify Your SendGrid Sender Identity"**
   - Haz click en el botón **"Verify Single Sender"**
6. Confirma la verificación en la página que se abre

**⏱️ Tiempo:** 2-3 minutos
**✅ Estado:** Listo para enviar emails inmediatamente

---

### 3️⃣ **Opción B: Domain Authentication (Recomendado para producción)**

Si tienes tu propio dominio (ej: `teamtime.com`), esta es la mejor opción a largo plazo:

1. En "Sender Authentication", haz click en **"Authenticate Your Domain"**
2. Selecciona tu proveedor de DNS (ej: Cloudflare, GoDaddy, etc.)
3. Introduce tu dominio (ej: `teamtime.com`)
4. SendGrid te dará 3 registros DNS (CNAME) para añadir a tu dominio
5. Añade esos registros en la configuración DNS de tu dominio
6. Vuelve a SendGrid y haz click en **"Verify"**

**⏱️ Tiempo:** 10-30 minutos (depende de propagación DNS)
**✅ Estado:** Podrás enviar desde cualquier email de tu dominio (ej: `noreply@teamtime.com`)

---

## ✅ Verificar que Funciona

Una vez que hayas verificado el sender:

1. **Prueba en la aplicación:**
   - Ve a https://team-time-management.vercel.app/employees
   - Haz click en **"Invitar Empleado"**
   - Ingresa tu email: `miguelchis@gmail.com`
   - Haz click en **"Enviar Invitación"**

2. **Revisa tu Gmail:**
   - Deberías recibir un email con asunto:
     **"admin@teamtime.com te ha invitado a Team Time Management"**
   - El email incluirá un link de invitación válido por 7 días

3. **Verifica en SendGrid Dashboard:**
   - Ve a **"Activity"** en el menú lateral
   - Deberías ver el email enviado con estado **"Delivered"**

---

## 📝 Notas Importantes

### Límite de Envíos (Plan Free de SendGrid):
- **100 emails/día** máximo
- Suficiente para desarrollo y pruebas
- Para producción, considera actualizar a un plan de pago

### Remitentes Verificados:
- Cada email desde el que quieras enviar **DEBE** estar verificado
- Si cambias `MAIL_DEFAULT_SENDER`, tendrás que verificarlo también
- Puedes tener múltiples remitentes verificados

### Problemas Comunes:
1. **Email no llega:** Revisa la carpeta de SPAM
2. **SendGrid rechaza:** Verifica que el sender esté verificado
3. **Error "Forbidden":** La API key puede estar revocada

---

## 🔄 Próximos Pasos Recomendados

### Para Desarrollo (AHORA):
✅ **Verifica Single Sender** (`miguelchis@gmail.com`) - Opción A arriba

### Para Producción (FUTURO):
1. Registra un dominio profesional (ej: `teamtime.com`)
2. Usa **Domain Authentication** - Opción B arriba  
3. Cambia `MAIL_DEFAULT_SENDER` a `noreply@teamtime.com`
4. Actualiza la variable en Render

---

## 🆘 Si Necesitas Ayuda

- **SendGrid Docs:** https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication
- **SendGrid Support:** https://support.sendgrid.com/

---

**Última actualización:** 12 de noviembre de 2025  
**Estado del sistema:** Configuración SMTP completa, pendiente verificación de sender

