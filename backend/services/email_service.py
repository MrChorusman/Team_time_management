from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from typing import List, Dict, Optional
import logging
from datetime import datetime

from models.notification import Notification
from models.user import User

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.mail = None
    
    def init_app(self, app):
        """Inicializa el servicio con la aplicación Flask"""
        self.mail = Mail(app)
    
    def send_notification_email(self, notification: Notification) -> bool:
        """Envía un email basado en una notificación"""
        try:
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
                'message': f'Email de prueba enviado exitosamente a {mail_username}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en configuración de email: {e}'
            }