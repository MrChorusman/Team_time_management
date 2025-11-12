# Guía de Diseño - Email Invitación Team Time Management

## 📋 Tabla de Contenidos
1. [Estructura y Jerarquía Visual](#estructura-y-jerarquía-visual)
2. [Llamada a la Acción (CTA)](#llamada-a-la-acción-cta)
3. [Contenido y Microcopy](#contenido-y-microcopy)
4. [Diseño Responsive](#diseño-responsive)
5. [Elementos de Confianza y Urgencia](#elementos-de-confianza-y-urgencia)
6. [Footer](#footer)
7. [Paleta de Colores](#paleta-de-colores-recomendada)
8. [Accesibilidad](#accesibilidad)
9. [Iconos SVG](#iconos-svg---sistema-de-diseño)
10. [Código de Ejemplo](#código-de-ejemplo---estructura-html)
11. [Testing](#testing-recomendado)

---

## Estructura y Jerarquía Visual

### Header
- **Logo prominente**: Incluir el logo de "Team Time Management" en la parte superior con buen tamaño (mínimo 40-50px altura)
- **Diseño centrado**: Usar un layout de una columna centrado con ancho máximo de 600px
- **Espaciado**: Añadir padding generoso (40-60px) arriba del contenido principal

### Saludo y Contexto
- **Personalización**: Usar el nombre del destinatario si está disponible: "Hola [Nombre]," en lugar de solo "Hola,"
- **Tipografía**: 
  - Título principal (H1): 24-28px, bold, color oscuro (#1a1a1a)
  - Cuerpo de texto: 16px, line-height 1.6, color gris oscuro (#333333)

---

## Llamada a la Acción (CTA)

### Botón Principal

**Especificaciones del botón:**
- Tamaño: Mínimo 44x44px (táctil móvil)
- Texto: "Aceptar invitación" o "Unirse al equipo"
- Color: Usar un color de acento destacado (ej: #0066cc, #28a745)
- Padding: 16px 32px
- Border-radius: 6-8px
- Efecto hover: Oscurecer 10-15%
- Posición: Centrado, después de la descripción

### Jerarquía de acciones
1. **CTA primario**: Botón grande y destacado
2. **Información secundaria**: Lista de funcionalidades más abajo
3. **CTA secundario opcional**: Enlace de texto "Más información" al final

---

## Contenido y Microcopy

### Mejorar el mensaje principal

**Antes:**
```
Administrador te ha invitado a unirte a Team Time Management
```

**Después:**
```
[Nombre Admin] te invita a unirte a su equipo en Team Time Management
```

### Reorganizar las funcionalidades

Usar iconos SVG + texto descriptivo:

1. **Registra tu tiempo** - Controla tus horas de forma sencilla e intuitiva
2. **Gestiona vacaciones y permisos** - Solicita y aprueba ausencias desde un solo lugar
3. **Colabora con tu equipo** - Mantén la sincronización con tus compañeros
4. **Visualiza tu rendimiento** - Accede a estadísticas detalladas de tu productividad

---

## Diseño Responsive

### Mobile-first

```css
/* Contenedor principal */
max-width: 600px;
margin: 0 auto;
padding: 20px;

/* En móvil (<600px) */
@media (max-width: 600px) {
  padding: 16px;
  font-size: 14px; /* reducir ligeramente */
}
```

---

## Elementos de Confianza y Urgencia

### Mejorar el aviso de caducidad

**Antes:**
```
⚠️ Importante: Esta invitación expirará en 7 días
```

**Después:**
Sección destacada con:
- Icono SVG de reloj de arena
- "Tu invitación expira el [fecha exacta]"
- Fondo suave (ej: #fff3cd con borde #ffc107)
- Padding de 16px

### Agregar elementos de seguridad
- Incluir el nombre del administrador real
- Mostrar el nombre de la empresa/equipo
- Añadir texto: "¿No esperabas este correo? [Enlace: Reportar problema]"

---

## Footer

### Información esencial

**Estructura:**
1. Separador sutil (línea gris clara)
2. Información legal compacta
3. Enlaces útiles: Política de privacidad | Términos | Ayuda
4. Opción de cancelar suscripción si aplica
5. Dirección de la empresa (requisito legal)

---

## Paleta de Colores Recomendada

```css
:root {
  --primary: #0066cc;      /* Azul profesional */
  --success: #28a745;      /* Verde para acciones positivas */
  --warning: #ffc107;      /* Amarillo para alertas */
  --text-primary: #1a1a1a; /* Negro suave */
  --text-secondary: #666;  /* Gris para texto secundario */
  --background: #f8f9fa;   /* Gris muy claro de fondo */
  --border: #e0e0e0;       /* Bordes sutiles */
}
```

---

## Accesibilidad

### Checklist
- [ ] Ratio de contraste mínimo 4.5:1 para texto normal
- [ ] Tamaño de fuente mínimo 14px
- [ ] Áreas táctiles mínimo 44x44px
- [ ] Texto alternativo en imágenes
- [ ] Estructura semántica HTML correcta
- [ ] Funciona sin imágenes activadas

---

## Iconos SVG - Sistema de Diseño

### Especificaciones técnicas

```css
/* Tamaño estándar de iconos */
width: 24px;
height: 24px;
display: inline-block;
vertical-align: middle;

/* Para contextos más pequeños (footer, etc) */
width: 16px;
height: 16px;
```

### Set de iconos recomendado

#### 1. Reloj/Tiempo (para registro de horas)
```html
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10" stroke="#0066cc" stroke-width="2"/>
  <path d="M12 6V12L16 14" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
</svg>
```

#### 2. Calendario (para vacaciones/permisos)
```html
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="4" width="18" height="18" rx="2" stroke="#0066cc" stroke-width="2"/>
  <path d="M3 10H21" stroke="#0066cc" stroke-width="2"/>
  <path d="M8 2V6M16 2V6" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
</svg>
```

#### 3. Usuarios/Equipo (para colaboración)
```html
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="9" cy="7" r="4" stroke="#0066cc" stroke-width="2"/>
  <path d="M2 21C2 17.134 5.134 14 9 14C12.866 14 16 17.134 16 21" stroke="#0066cc" stroke-width="2"/>
  <circle cx="17" cy="7" r="3" stroke="#0066cc" stroke-width="2"/>
  <path d="M22 21C22 18.791 20.209 17 18 17" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
</svg>
```

#### 4. Gráfico de barras (para estadísticas)
```html
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 3V21H21" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
  <rect x="7" y="12" width="3" height="7" fill="#0066cc"/>
  <rect x="12" y="8" width="3" height="11" fill="#0066cc"/>
  <rect x="17" y="14" width="3" height="5" fill="#0066cc"/>
</svg>
```

#### 5. Reloj de arena (para alerta de caducidad)
```html
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 2H18V6L12 12L18 18V22H6V18L12 12L6 6V2Z" stroke="#856404" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M6 2H18M6 22H18" stroke="#856404" stroke-width="2"/>
</svg>
```

#### 6. Escudo/Seguridad (para footer)
```html
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="#666" stroke-width="2" stroke-linejoin="round"/>
</svg>
```

### Sistema de colores para iconos

```css
/* Iconos principales (funcionalidades) */
stroke: #0066cc; /* Azul primario */

/* Iconos de alerta/advertencia */
stroke: #856404; /* Marrón oscuro (complementa el amarillo #fff3cd) */

/* Iconos secundarios (footer, etc) */
stroke: #666666; /* Gris medio */

/* Iconos de éxito (si aplica) */
stroke: #28a745; /* Verde */
```

---

## Código de Ejemplo - Estructura HTML

### Estructura completa del email

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Invitación a Team Time Management</title>
</head>
<body style="margin:0; padding:0; background:#f8f9fa; font-family:Arial,sans-serif;">
  
  <!-- Contenedor principal -->
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 20px;">
        
        <!-- Email content -->
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
          
          <!-- Header con logo -->
          <tr>
            <td align="center" style="padding:40px 40px 20px;">
              <img src="[LOGO_URL]" alt="Team Time Management" height="50">
            </td>
          </tr>
          
          <!-- Contenido principal -->
          <tr>
            <td style="padding:20px 40px;">
              
              <h1 style="margin:0 0 16px; font-size:24px; color:#1a1a1a;">
                ¡Has sido invitado!
              </h1>
              
              <p style="margin:0 0 24px; font-size:16px; line-height:1.6; color:#333;">
                <strong>[Nombre Admin]</strong> te invita a unirte a su equipo en <strong>Team Time Management</strong>, la plataforma de gestión de tiempo y horarios.
              </p>
              
              <!-- CTA Principal -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:24px 0;">
                    <a href="[LINK_INVITACION]" style="display:inline-block; padding:16px 40px; background:#0066cc; color:#ffffff; text-decoration:none; border-radius:6px; font-size:16px; font-weight:bold;">
                      Aceptar invitación
                    </a>
                  </td>
                </tr>
              </table>
              
              <!-- Funcionalidades -->
              <p style="margin:32px 0 16px; font-size:18px; font-weight:bold; color:#1a1a1a;">
                Con esta plataforma podrás:
              </p>
              
              <!-- Lista de funcionalidades con iconos SVG -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:24px;">
                
                <!-- Funcionalidad 1: Registro de tiempo -->
                <tr>
                  <td width="40" valign="top" style="padding:0 16px 16px 0;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="#0066cc" stroke-width="2"/>
                      <path d="M12 6V12L16 14" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </td>
                  <td style="padding-bottom:16px;">
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px;">
                      Registra tu tiempo
                    </strong>
                    <span style="color:#666; font-size:14px; line-height:1.5;">
                      Controla tus horas de forma sencilla e intuitiva
                    </span>
                  </td>
                </tr>
                
                <!-- Funcionalidad 2: Vacaciones -->
                <tr>
                  <td width="40" valign="top" style="padding:0 16px 16px 0;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <rect x="3" y="4" width="18" height="18" rx="2" stroke="#0066cc" stroke-width="2"/>
                      <path d="M3 10H21" stroke="#0066cc" stroke-width="2"/>
                      <path d="M8 2V6M16 2V6" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </td>
                  <td style="padding-bottom:16px;">
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px;">
                      Gestiona vacaciones y permisos
                    </strong>
                    <span style="color:#666; font-size:14px; line-height:1.5;">
                      Solicita y aprueba ausencias desde un solo lugar
                    </span>
                  </td>
                </tr>
                
                <!-- Funcionalidad 3: Colaboración -->
                <tr>
                  <td width="40" valign="top" style="padding:0 16px 16px 0;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <circle cx="9" cy="7" r="4" stroke="#0066cc" stroke-width="2"/>
                      <path d="M2 21C2 17.134 5.134 14 9 14C12.866 14 16 17.134 16 21" stroke="#0066cc" stroke-width="2"/>
                      <circle cx="17" cy="7" r="3" stroke="#0066cc" stroke-width="2"/>
                      <path d="M22 21C22 18.791 20.209 17 18 17" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </td>
                  <td style="padding-bottom:16px;">
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px;">
                      Colabora con tu equipo
                    </strong>
                    <span style="color:#666; font-size:14px; line-height:1.5;">
                      Mantén la sincronización con tus compañeros
                    </span>
                  </td>
                </tr>
                
                <!-- Funcionalidad 4: Estadísticas -->
                <tr>
                  <td width="40" valign="top" style="padding:0 16px 0 0;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M3 3V21H21" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                      <rect x="7" y="12" width="3" height="7" fill="#0066cc"/>
                      <rect x="12" y="8" width="3" height="11" fill="#0066cc"/>
                      <rect x="17" y="14" width="3" height="5" fill="#0066cc"/>
                    </svg>
                  </td>
                  <td>
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px;">
                      Visualiza tu rendimiento
                    </strong>
                    <span style="color:#666; font-size:14px; line-height:1.5;">
                      Accede a estadísticas detalladas de tu productividad
                    </span>
                  </td>
                </tr>
                
              </table>
              
            </td>
          </tr>
          
          <!-- Alerta de caducidad -->
          <tr>
            <td style="padding:0 40px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff3cd; border-left:4px solid #ffc107; border-radius:4px;">
                <tr>
                  <td width="36" valign="top" style="padding:16px 0 16px 16px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path d="M6 2H18V6L12 12L18 18V22H6V18L12 12L6 6V2Z" stroke="#856404" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M6 2H18M6 22H18" stroke="#856404" stroke-width="2"/>
                    </svg>
                  </td>
                  <td style="padding:16px 16px 16px 8px;">
                    <strong style="color:#856404; font-size:14px;">
                      Tu invitación expira el [FECHA_EXACTA]
                    </strong>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px; border-top:1px solid #e0e0e0; text-align:center;">
              <p style="margin:0 0 8px; font-size:12px; color:#666;">
                ¿No esperabas este correo? Puedes ignorarlo de forma segura.
              </p>
              <p style="margin:8px 0; font-size:12px; color:#666;">
                <a href="[URL_PRIVACIDAD]" style="color:#0066cc; text-decoration:none;">Política de privacidad</a> | 
                <a href="[URL_TERMINOS]" style="color:#0066cc; text-decoration:none;">Términos</a> | 
                <a href="[URL_AYUDA]" style="color:#0066cc; text-decoration:none;">Ayuda</a>
              </p>
              <p style="margin:16px 0 0; font-size:12px; color:#999;">
                Team Time Management © 2025 - Todos los derechos reservados
              </p>
            </td>
          </tr>
          
        </table>
        
      </td>
    </tr>
  </table>
  
</body>
</html>
```

---

## Alternativas de Bibliotecas de Iconos

Si prefieres no crear cada SVG manualmente, puedes usar iconos inline de bibliotecas populares:

### Opción 1: Heroicons (recomendado para emails)
- Los SVG están optimizados y son muy ligeros
- Descarga desde: https://heroicons.com

### Opción 2: Feather Icons
- Estilo minimalista y consistente
- Descarga desde: https://feathericons.com

### Opción 3: Material Icons (SVG inline)
- Más reconocibles para usuarios
- Descarga desde: https://fonts.google.com/icons

---

## Consideraciones Técnicas Importantes

### Para compatibilidad con clientes de email:

1. **Siempre inline**: Los SVG deben estar directamente en el HTML, no como archivos externos
2. **Tamaño fijo**: Especifica width y height explícitamente
3. **Sin JavaScript**: Los SVG deben ser estáticos
4. **Fallback opcional**: Considera agregar un alt descriptivo en un span oculto para lectores de pantalla
5. **Testing**: Outlook tiene soporte limitado de SVG, considera una alternativa con imágenes PNG para versiones antiguas

### Fallback para Outlook

```html
<!--[if mso]>
  <img src="[URL_ICONO_PNG]" width="24" height="24" alt="Reloj">
<![endif]-->
<!--[if !mso]><!-->
  <svg width="24" height="24">...</svg>
<!--<![endif]-->
```

---

## Testing Recomendado

### Probar el email en:
- Gmail (web y móvil)
- Outlook (web y desktop)
- Apple Mail (iOS y macOS)
- Modo oscuro
- Con imágenes desactivadas

### Herramientas de testing:
- **Litmus**: https://litmus.com
- **Email on Acid**: https://www.emailonacid.com
- **Mailtrap**: https://mailtrap.io
- **Preview en navegador**: Siempre hacer una vista previa manual

---

## Notas Finales

### Mejores prácticas adicionales:
- Mantener el peso total del email bajo 100KB
- Usar imágenes optimizadas (WebP con fallback JPG)
- Incluir texto alternativo en todas las imágenes
- Validar HTML en https://validator.w3.org
- Probar enlaces antes de enviar
- Usar un servicio de email transaccional confiable (SendGrid, Mailgun, AWS SES)

### Variables a reemplazar en el código:
- `[LOGO_URL]`: URL del logo de la empresa
- `[Nombre Admin]`: Nombre del administrador que invita
- `[LINK_INVITACION]`: URL única de invitación
- `[FECHA_EXACTA]`: Fecha de expiración de la invitación
- `[URL_PRIVACIDAD]`: Enlace a política de privacidad
- `[URL_TERMINOS]`: Enlace a términos y condiciones
- `[URL_AYUDA]`: Enlace a centro de ayuda
- `[URL_ICONO_PNG]`: URL de fallback para iconos (Outlook)