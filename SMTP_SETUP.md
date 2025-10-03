# 📧 **CONFIGURACIÓN SMTP - TEAM TIME MANAGEMENT**

Este documento detalla los pasos necesarios para configurar el sistema de envío de emails en Team Time Management.

---

## 📋 **VARIABLES DE ENTORNO REQUERIDAS**

Para que la aplicación envíe emails correctamente, se deben configurar las siguientes variables de entorno en el archivo `.env`:

### **Variables Básicas**
- **`MAIL_SERVER`**: Servidor SMTP
- **`MAIL_PORT`**: Puerto del servidor SMTP
- **`MAIL_USE_TLS`**: Usar TLS (true/false)
- **`MAIL_USERNAME`**: Usuario del servidor SMTP
- **`MAIL_PASSWORD`**: Contraseña del servidor SMTP
- **`MAIL_DEFAULT_SENDER`**: Email remitente por defecto

---

## 🔧 **CONFIGURACIONES SMTP SOPORTADAS**

### **1. Gmail (Recomendado)**

**Configuración:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion
MAIL_DEFAULT_SENDER=tu-email@gmail.com
```

**Pasos para configurar:**
1. Habilita la **verificación en 2 pasos** en tu cuenta de Google
2. Ve a **Configuración de la cuenta** → **Seguridad**
3. Genera una **"Contraseña de aplicación"** específica
4. Usa esta contraseña en lugar de tu contraseña normal

### **2. SendGrid (Para producción)**

**Configuración:**
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=apikey
MAIL_PASSWORD=tu-api-key-de-sendgrid
MAIL_DEFAULT_SENDER=noreply@tu-dominio.com
```

**Pasos para configurar:**
1. Crea una cuenta en [SendGrid](https://sendgrid.com)
2. Ve al dashboard y obtén tu **API Key**
3. Configura la autenticación de dominio (opcional pero recomendado)

### **3. Outlook/Hotmail**

**Configuración:**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@outlook.com
MAIL_PASSWORD=tu-contraseña
MAIL_DEFAULT_SENDER=tu-email@outlook.com
```

### **4. Yahoo Mail**

**Configuración:**
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@yahoo.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion
MAIL_DEFAULT_SENDER=tu-email@yahoo.com
```

---

## 📝 **EJEMPLO DE ARCHIVO `.env`**

```env
# ===========================================
# CONFIGURACIÓN DE EMAIL (SMTP)
# ===========================================

# Configuración SMTP - Gmail (recomendado)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion
MAIL_DEFAULT_SENDER=tu-email@gmail.com

# Otras variables de entorno...
SECRET_KEY=tu_secret_key_segura
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-supabase-key
SUPABASE_DB_PASSWORD=tu-database-password
```

---

## 🧪 **VERIFICACIÓN DE LA CONFIGURACIÓN**

### **1. Script de Prueba**
Ejecuta el script de prueba incluido:

```bash
cd backend
python test_smtp_config.py
```

### **2. Desde la API**
Si tienes acceso de administrador, puedes probar la configuración desde la API:

```bash
# Obtener configuración actual
curl -X GET "http://localhost:5000/api/admin/email-config" \
  -H "Authorization: Bearer tu-token"

# Probar configuración SMTP
curl -X POST "http://localhost:5000/api/admin/test-smtp" \
  -H "Authorization: Bearer tu-token"
```

---

## 📧 **TIPOS DE EMAILS IMPLEMENTADOS**

### **1. Emails de Verificación**
- Enviados al registrarse un nuevo usuario
- Incluyen enlace de verificación con expiración de 24 horas

### **2. Emails de Restablecimiento de Contraseña**
- Enviados al solicitar cambio de contraseña
- Incluyen enlace seguro con expiración de 1 hora

### **3. Emails de Notificaciones**
- Notificaciones del sistema
- Recordatorios automáticos
- Alertas de festivos
- Reportes de horas

### **4. Emails de Bienvenida**
- Enviados tras verificación exitosa de cuenta

---

## 🎨 **PLANTILLAS DE EMAIL**

El sistema incluye plantillas profesionales:

- **`base.html`**: Plantilla base para emails generales
- **`verification.html`**: Plantilla para verificación de cuenta
- **`password_reset.html`**: Plantilla para restablecimiento de contraseña
- **`notification.html`**: Plantilla para notificaciones

### **Características de las Plantillas:**
- ✅ Diseño responsivo
- ✅ Compatible con clientes de email
- ✅ Branding consistente
- ✅ Colores por prioridad
- ✅ Enlaces de acción claros

---

## 🔒 **CONSIDERACIONES DE SEGURIDAD**

### **1. Credenciales Seguras**
- Nunca subas el archivo `.env` al repositorio
- Usa contraseñas de aplicación específicas
- Rota las credenciales periódicamente

### **2. Límites de Envío**
- Gmail: 500 emails/día (cuentas gratuitas)
- SendGrid: 100 emails/día (plan gratuito)
- Implementa colas para envíos masivos

### **3. Validación de Emails**
- Verifica direcciones de email antes del envío
- Implementa listas de supresión
- Maneja rebotes correctamente

---

## 🚀 **PRÓXIMOS PASOS**

Una vez configurado SMTP:

1. **Probar envío de emails** usando el script de prueba
2. **Configurar notificaciones automáticas** en la aplicación
3. **Implementar colas de email** para envíos masivos (opcional)
4. **Configurar monitoreo** de emails enviados (opcional)

---

## ❓ **SOLUCIÓN DE PROBLEMAS**

### **Error: "Authentication failed"**
- Verifica que las credenciales sean correctas
- Para Gmail, asegúrate de usar una contraseña de aplicación
- Verifica que la verificación en 2 pasos esté habilitada

### **Error: "Connection refused"**
- Verifica que el servidor SMTP y puerto sean correctos
- Comprueba que tu firewall permita conexiones salientes al puerto 587/465

### **Error: "TLS/SSL required"**
- Asegúrate de que `MAIL_USE_TLS=true`
- Para algunos proveedores, usa puerto 465 con SSL

### **Emails van a spam**
- Configura SPF, DKIM y DMARC en tu dominio
- Usa un remitente reconocido
- Evita palabras que activen filtros de spam

---

## 📞 **SOPORTE**

Si tienes problemas con la configuración SMTP:

1. Revisa los logs de la aplicación
2. Ejecuta el script de prueba
3. Verifica la configuración con tu proveedor de email
4. Consulta la documentación específica de tu proveedor SMTP
