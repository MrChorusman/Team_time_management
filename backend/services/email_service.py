from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from typing import List, Dict, Optional
import logging
import os
from datetime import datetime

from models.notification import Notification
from models.user import User
from .mock_email_service import MockEmailService

# SendGrid Web API (no SMTP - Render bloquea puerto 587)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail as SendGridMail, Email, To, Content
    HAS_SENDGRID = True
except ImportError:
    HAS_SENDGRID = False

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.mail = None
        self.mock_service = MockEmailService()
        self._use_mock_mode = None
    
    def init_app(self, app):
        """Inicializa el servicio con la aplicación Flask"""
        try:
            self.mail = Mail(app)
            logger.info(f"Flask-Mail inicializado: {self.mail is not None}")
        except Exception as e:
            logger.error(f"Error inicializando Flask-Mail: {e}")
            self.mail = None
        
        # Determinar si usar modo mock leyendo directamente MOCK_EMAIL_MODE
        # No podemos usar app.config.get('should_use_mock_email') porque es una @property
        mock_email_mode = app.config.get('MOCK_EMAIL_MODE', False)
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        email_configured = all([mail_username, mail_password])
        
        # Usar modo mock si está explícitamente activado O si no hay credenciales
        self._use_mock_mode = mock_email_mode or not email_configured
        
        # Log de configuración
        logger.info(f"MOCK_EMAIL_MODE: {mock_email_mode}")
        logger.info(f"MAIL_USERNAME configurado: {bool(mail_username)}")
        logger.info(f"MAIL_PASSWORD configurado: {bool(mail_password)}")
        logger.info(f"email_configured: {email_configured}")
        logger.info(f"_use_mock_mode calculado: {self._use_mock_mode}")
        
        if self._use_mock_mode:
            logger.info("📧 EmailService inicializado en modo MOCK - emails se simularán en logs")
        else:
            logger.info("📧 EmailService inicializado en modo REAL - emails se enviarán por SMTP via SendGrid")
    
    @property
    def use_mock_mode(self):
        """Determina si debe usar modo mock"""
        if self._use_mock_mode is None:
            # Fallback: verificar configuración directamente
            return current_app.config.get('should_use_mock_email', False)
        return self._use_mock_mode
    
    def _send_via_sendgrid_api(self, to_email: str, subject: str, plain_text: str, html_content: str) -> bool:
        """
        Envía email usando SendGrid Web API (no SMTP)
        Render bloquea puerto 587, por eso usamos API (HTTPS)
        """
        try:
            api_key = os.environ.get('MAIL_PASSWORD')  # La API key está en MAIL_PASSWORD
            from_email = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@teamtime.com')
            
            if not api_key:
                logger.error("MAIL_PASSWORD (SendGrid API Key) no configurada")
                return False
            
            # Crear mensaje usando SendGrid SDK
            message = SendGridMail(
                from_email=Email(from_email),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", plain_text),
                html_content=Content("text/html", html_content)
            )
            
            # Enviar usando SendGrid Web API
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            logger.info(f"✅ SendGrid Web API response: {response.status_code}")
            
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"❌ Error con SendGrid API: {e}")
            logger.exception(e)
            return False
    
    def send_notification_email(self, notification: Notification) -> bool:
        """Envía un email basado en una notificación"""
        try:
            # Usar modo mock si está configurado
            if self.use_mock_mode:
                return self.mock_service.send_notification_email(notification)
            
            # Modo real - enviar por SMTP
            if not self.mail:
                logger.error("Servicio de email no inicializado")
                return False
            
            user = User.query.get(notification.user_id)
            if not user:
                logger.error(f"Usuario {notification.user_id} no encontrado para notificación {notification.id}")
                return False
            
            # Generar contenido del email según el tipo
            subject, html_body, text_body = self._generate_email_content(notification, user)
            
            # Crear mensaje
            msg = Message(
                subject=subject,
                recipients=[user.email],
                html=html_body,
                body=text_body
            )
            
            # Enviar email
            self.mail.send(msg)
            logger.info(f"Email enviado exitosamente a {user.email} para notificación {notification.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email para notificación {notification.id}: {e}")
            return False
    
    def _generate_email_content(self, notification: Notification, user: User) -> tuple:
        """Genera el contenido del email según el tipo de notificación"""
        
        # Mapear tipos de notificación
        notification_type_names = {
            'system_alert': 'Alerta del Sistema',
            'reminder': 'Recordatorio',
            'holiday_alert': 'Alerta de Festivo',
            'vacation_reminder': 'Recordatorio de Vacaciones',
            'hours_report': 'Reporte de Horas',
            'admin_notification': 'Notificación Administrativa'
        }
        
        # Generar contenido HTML usando plantilla
        html_body = render_template('emails/notification.html',
                                  user_name=user.first_name or user.email,
                                  title=notification.title,
                                  message=notification.message,
                                  priority=notification.priority.value,
                                  notification_type=notification.notification_type.value,
                                  notification_type_name=notification_type_names.get(notification.notification_type.value, 'Notificación'),
                                  action_url=getattr(notification, 'action_url', None),
                                  additional_info=getattr(notification, 'description', None),
                                  sent_date=datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        # Generar contenido texto plano
        text_body = f"""
Team Time Management - {notification.title}

Hola {user.first_name or user.email},

{notification.message}

Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Este email fue enviado automáticamente por Team Time Management.
Si tienes preguntas, contacta con tu administrador del sistema.
        """
        
        return notification.title, html_body, text_body
    
    def send_verification_email(self, user: User, token: str) -> bool:
        """Envía email de verificación de cuenta"""
        try:
            # Usar modo mock si está configurado
            if self.use_mock_mode:
                return self.mock_service.send_verification_email(user, token)
            
            # Modo real - enviar por SMTP
            if not self.mail:
                logger.error("Servicio de email no inicializado")
                return False
            
            # Generar URL de verificación
            verification_url = url_for('auth.confirm_email', token=token, _external=True)
            
            # Renderizar plantilla
            html_body = render_template('emails/verification.html',
                                      user_name=user.first_name or user.email,
                                      verification_url=verification_url,
                                      sent_date=datetime.now().strftime('%d/%m/%Y %H:%M'))
            
            # Crear mensaje
            msg = Message(
                subject="Verifica tu cuenta - Team Time Management",
                recipients=[user.email],
                html=html_body
            )
            
            # Enviar email
            self.mail.send(msg)
            logger.info(f"Email de verificación enviado a {user.email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de verificación a {user.email}: {e}")
            return False
    
    def send_password_reset_email(self, user: User, token: str) -> bool:
        """Envía email de restablecimiento de contraseña"""
        try:
            # Usar modo mock si está configurado
            if self.use_mock_mode:
                return self.mock_service.send_password_reset_email(user, token)
            
            # Modo real - enviar por SMTP
            if not self.mail:
                logger.error("Servicio de email no inicializado")
                return False
            
            # Generar URL de restablecimiento
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # Renderizar plantilla
            html_body = render_template('emails/password_reset.html',
                                      user_name=user.first_name or user.email,
                                      reset_url=reset_url,
                                      sent_date=datetime.now().strftime('%d/%m/%Y %H:%M'))
            
            # Crear mensaje
            msg = Message(
                subject="Restablecer contraseña - Team Time Management",
                recipients=[user.email],
                html=html_body
            )
            
            # Enviar email
            self.mail.send(msg)
            logger.info(f"Email de restablecimiento enviado a {user.email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de restablecimiento a {user.email}: {e}")
            return False
    
    def send_welcome_email(self, user: User) -> bool:
        """Envía email de bienvenida"""
        try:
            if not self.mail:
                logger.error("Servicio de email no inicializado")
                return False
            
            # Renderizar plantilla
            html_body = render_template('emails/base.html',
                                      user_name=user.first_name or user.email,
                                      title="¡Bienvenido a Team Time Management!",
                                      message="Tu cuenta ha sido creada exitosamente. Ya puedes comenzar a usar el sistema.",
                                      priority="low",
                                      sent_date=datetime.now().strftime('%d/%m/%Y %H:%M'),
                                      additional_info="<p>Si tienes alguna pregunta, no dudes en contactar con tu administrador.</p>")
            
            # Crear mensaje
            msg = Message(
                subject="¡Bienvenido a Team Time Management!",
                recipients=[user.email],
                html=html_body
            )
            
            # Enviar email
            self.mail.send(msg)
            logger.info(f"Email de bienvenida enviado a {user.email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de bienvenida a {user.email}: {e}")
            return False
    
    def send_bulk_notifications(self, notifications: List[Notification]) -> Dict:
        """Envía múltiples notificaciones por email"""
        results = {
            'total': len(notifications),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for notification in notifications:
            try:
                if self.send_notification_email(notification):
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Error enviando notificación {notification.id}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error enviando notificación {notification.id}: {e}")
        
        logger.info(f"Envío masivo completado: {results['sent']}/{results['total']} exitosos")
        return results
    
    def test_email_configuration(self) -> Dict:
        """Prueba la configuración de email"""
        try:
            # Si está en modo mock, devolver información del mock
            if self.use_mock_mode:
                stats = self.mock_service.get_email_stats()
                return {
                    'success': True,
                    'mode': 'mock',
                    'message': f'Modo mock activo - {stats["total_emails"]} emails simulados',
                    'stats': stats
                }
            
            # Modo real - probar SMTP
            if not self.mail:
                return {
                    'success': False,
                    'error': 'Servicio de email no inicializado'
                }
            
            # Verificar configuración SMTP
            mail_username = current_app.config.get('MAIL_USERNAME')
            if not mail_username:
                return {
                    'success': False,
                    'error': 'MAIL_USERNAME no configurado'
                }
            
            # Intentar enviar un email de prueba
            test_msg = Message(
                subject="Test - Team Time Management",
                recipients=[mail_username],
                html=render_template('emails/base.html',
                                   user_name="Administrador",
                                   title="Prueba de configuración SMTP",
                                   message="Este es un email de prueba del sistema Team Time Management. Si recibes este email, la configuración SMTP está funcionando correctamente.",
                                   priority="medium",
                                   sent_date=datetime.now().strftime('%d/%m/%Y %H:%M'))
            )
            
            self.mail.send(test_msg)
            
            return {
                'success': True,
                'mode': 'real',
                'message': f'Email de prueba enviado exitosamente a {mail_username}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en configuración de email: {e}'
            }
    
    def get_mock_email_stats(self) -> Dict:
        """Obtiene estadísticas del servicio mock (solo disponible en modo mock)"""
        if not self.use_mock_mode:
            return {'error': 'Servicio no está en modo mock'}
        
        return self.mock_service.get_email_stats()
    
    def get_mock_sent_emails(self, limit: int = 50) -> List[Dict]:
        """Obtiene emails enviados en modo mock (solo disponible en modo mock)"""
        if not self.use_mock_mode:
            return []
        
        return self.mock_service.get_sent_emails(limit)
    
    def clear_mock_emails(self):
        """Limpia la lista de emails mock (solo disponible en modo mock)"""
        if self.use_mock_mode:
            self.mock_service.clear_sent_emails()
    
    def send_custom_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """
        Envía un email genérico
        
        Args:
            to_email: Email destino
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Usar modo mock si está configurado
            if self.use_mock_mode:
                return self.mock_service.send_custom_email(to_email, subject, body, html_body)
            
            # Modo real - enviar por SMTP
            if not self.mail:
                logger.error("Servicio de email no inicializado")
                return False
            
            # Crear mensaje
            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=body,
                html=html_body
            )
            
            # Enviar email
            self.mail.send(msg)
            logger.info(f"Email genérico enviado exitosamente a {to_email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email genérico a {to_email}: {e}")
            return False
    
    def send_invitation_email(self, to_email: str, invitation_link: str, inviter_name: str, expires_days: int = 7) -> bool:
        """
        Envía un email de invitación para unirse a la plataforma
        
        Args:
            to_email: Email del destinatario
            invitation_link: Link único de invitación
            inviter_name: Nombre de quien invita
            expires_days: Días hasta que expire la invitación
        
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            # Usar modo mock si está configurado
            if self.use_mock_mode:
                return self.mock_service.send_invitation_email(
                    to_email, invitation_link, inviter_name, expires_days
                )
            
            subject = f"{inviter_name} te ha invitado a Team Time Management"
            
            # Modo real - intentar SendGrid Web API primero (Render bloquea SMTP)
            if HAS_SENDGRID and os.environ.get('MAIL_PASSWORD', '').startswith('SG.'):
                logger.info("📧 Usando SendGrid Web API (no SMTP)")
            
            # Cuerpo del email en texto plano
            body = f"""
Hola,

{inviter_name} te ha invitado a unirte a Team Time Management, la plataforma de gestión de tiempo y horarios.

Para completar tu registro, haz clic en el siguiente enlace:

{invitation_link}

Esta invitación expirará en {expires_days} días.

Si no esperabas este email, puedes ignorarlo.

Saludos,
Equipo de Team Time Management
            """
            
            # Cuerpo del email en HTML
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Invitación a Team Time Management</title>
</head>
<body style="margin:0; padding:0; background:#f8f9fa; font-family:Arial,Helvetica,sans-serif;">
  
  <!-- Contenedor principal -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center" style="padding:40px 20px;">
        
        <!-- Email content -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff; border-radius:8px;">
          
          <!-- Header con logo -->
          <tr>
            <td align="center" style="padding:40px 40px 32px; background:#0066cc;">
              <h1 style="margin:0; font-size:28px; color:#ffffff; font-weight:700; letter-spacing:0.5px;">
                Team Time Management
              </h1>
            </td>
          </tr>
          
          <!-- Contenido principal -->
          <tr>
            <td style="padding:40px 40px 32px;">
              
              <p style="margin:0 0 24px; font-size:16px; line-height:1.6; color:#333;">
                <strong>{inviter_name}</strong> te invita a unirte a su equipo en <strong>Team Time Management</strong>, la plataforma de gestión de tiempo y horarios.
              </p>
              
              <!-- CTA Principal -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="padding:24px 0 32px;">
                    <a href="{invitation_link}" style="display:inline-block; padding:16px 40px; background:#0066cc; color:#ffffff; text-decoration:none; border-radius:6px; font-size:16px; font-weight:bold;">
                      Aceptar invitación
                    </a>
                  </td>
                </tr>
              </table>
              
              <!-- Funcionalidades -->
              <p style="margin:0 0 20px; font-size:18px; font-weight:bold; color:#1a1a1a;">
                Con esta plataforma podrás:
              </p>
              
              <!-- Lista de funcionalidades con iconos SVG -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:24px;">
                
                <!-- Funcionalidad 1: Registro de tiempo -->
                <tr>
                  <td width="40" valign="top" style="padding:0 16px 16px 0;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="#0066cc" stroke-width="2"/>
                      <path d="M12 6V12L16 14" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </td>
                  <td style="padding-bottom:16px;">
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px; font-size:15px;">
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
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="4" width="18" height="18" rx="2" stroke="#0066cc" stroke-width="2"/>
                      <path d="M3 10H21" stroke="#0066cc" stroke-width="2"/>
                      <path d="M8 2V6M16 2V6" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </td>
                  <td style="padding-bottom:16px;">
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px; font-size:15px;">
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
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="9" cy="7" r="4" stroke="#0066cc" stroke-width="2"/>
                      <path d="M2 21C2 17.134 5.134 14 9 14C12.866 14 16 17.134 16 21" stroke="#0066cc" stroke-width="2"/>
                      <circle cx="17" cy="7" r="3" stroke="#0066cc" stroke-width="2"/>
                      <path d="M22 21C22 18.791 20.209 17 18 17" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </td>
                  <td style="padding-bottom:16px;">
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px; font-size:15px;">
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
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 3V21H21" stroke="#0066cc" stroke-width="2" stroke-linecap="round"/>
                      <rect x="7" y="12" width="3" height="7" fill="#0066cc"/>
                      <rect x="12" y="8" width="3" height="11" fill="#0066cc"/>
                      <rect x="17" y="14" width="3" height="5" fill="#0066cc"/>
                    </svg>
                  </td>
                  <td>
                    <strong style="display:block; color:#1a1a1a; margin-bottom:4px; font-size:15px;">
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
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#fff3cd; border-left:4px solid #ffc107; border-radius:4px;">
                <tr>
                  <td width="36" valign="top" style="padding:16px 0 16px 16px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 2H18V6L12 12L18 18V22H6V18L12 12L6 6V2Z" stroke="#856404" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M6 2H18M6 22H18" stroke="#856404" stroke-width="2"/>
                    </svg>
                  </td>
                  <td style="padding:16px 16px 16px 8px;">
                    <strong style="color:#856404; font-size:14px;">
                      Tu invitación expira en {expires_days} días
                    </strong>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px; border-top:1px solid #e0e0e0; text-align:center; background:#f8f9fa;">
              <p style="margin:0 0 8px; font-size:12px; color:#666;">
                ¿No esperabas este correo? Puedes ignorarlo de forma segura.
              </p>
              <p style="margin:16px 0 0; font-size:12px; color:#999;">
                Team Time Management &copy; {datetime.now().year} - Todos los derechos reservados
              </p>
            </td>
          </tr>
          
        </table>
        
      </td>
    </tr>
  </table>
  
</body>
</html>
            """
            
            # Enviar usando SendGrid Web API si está disponible
            if HAS_SENDGRID and os.environ.get('MAIL_PASSWORD', '').startswith('SG.'):
                logger.info("📧 Enviando vía SendGrid Web API")
                return self._send_via_sendgrid_api(to_email, subject, body, html_body)
            
            # Fallback: SMTP (puede fallar en Render)
            if not self.mail:
                logger.error("Servicio de email no inicializado y SendGrid no disponible")
                return False
            
            logger.info("📧 Enviando vía SMTP (puede fallar en Render)")
            
            # Crear mensaje
            msg = Message(
                subject=subject,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@teamtime.com'),
                recipients=[to_email],
                body=body,
                html=html_body
            )
            
            # Enviar email
            self.mail.send(msg)
            logger.info(f"Email de invitación enviado exitosamente a {to_email} vía SMTP")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de invitación a {to_email}: {e}")
            return False


# Instancia global del servicio
email_service = EmailService()


# Funciones wrapper para facilitar el uso
def send_notification_email(notification: Notification) -> bool:
    """Wrapper para enviar email de notificación"""
    return email_service.send_notification_email(notification)


def send_invitation_email(to_email: str, invitation_link: str, inviter_name: str, expires_days: int = 7) -> bool:
    """Wrapper para enviar email de invitación"""
    return email_service.send_invitation_email(to_email, invitation_link, inviter_name, expires_days)