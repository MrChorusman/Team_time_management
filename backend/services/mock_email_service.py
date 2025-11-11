"""
Servicio mock para emails en desarrollo
Simula el envío de emails guardándolos en logs
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from flask import current_app

from models.notification import Notification
from models.user import User

logger = logging.getLogger(__name__)

class MockEmailService:
    """Servicio mock para simular envío de emails en desarrollo"""
    
    def __init__(self):
        self.sent_emails = []  # Lista para almacenar emails "enviados"
    
    def send_notification_email(self, notification: Notification) -> bool:
        """Simula el envío de un email basado en una notificación"""
        try:
            user = User.query.get(notification.user_id)
            if not user:
                logger.error(f"Usuario {notification.user_id} no encontrado para notificación {notification.id}")
                return False
            
            # Generar contenido del email
            subject, html_body, text_body = self._generate_email_content(notification, user)
            
            # Simular envío guardando en logs y lista interna
            email_data = {
                'timestamp': datetime.now().isoformat(),
                'to': user.email,
                'subject': subject,
                'html_body': html_body,
                'text_body': text_body,
                'notification_id': notification.id,
                'notification_type': notification.notification_type.value,
                'priority': notification.priority.value
            }
            
            self.sent_emails.append(email_data)
            
            # Log estructurado
            logger.info(f"[MOCK EMAIL] Enviado a {user.email} - {subject}", extra={
                'email_type': 'notification',
                'user_id': user.id,
                'notification_id': notification.id,
                'priority': notification.priority.value
            })
            
            # Log detallado del contenido
            logger.debug(f"[MOCK EMAIL CONTENT] {subject}\nTo: {user.email}\n\n{text_body}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error simulando email para notificación {notification.id}: {e}")
            return False
    
    def send_verification_email(self, user: User, token: str) -> bool:
        """Simula el envío de email de verificación"""
        try:
            subject = "Verificación de cuenta - Team Time Management"
            text_body = f"""
Hola {user.first_name or user.email},

Para verificar tu cuenta, haz clic en el siguiente enlace:
http://localhost:5173/verify-email?token={token}

Si no solicitaste esta verificación, puedes ignorar este email.

Saludos,
Equipo Team Time Management
            """
            
            email_data = {
                'timestamp': datetime.now().isoformat(),
                'to': user.email,
                'subject': subject,
                'text_body': text_body,
                'email_type': 'verification',
                'token': token
            }
            
            self.sent_emails.append(email_data)
            
            logger.info(f"[MOCK EMAIL] Verificación enviada a {user.email}", extra={
                'email_type': 'verification',
                'user_id': user.id,
                'token': token[:10] + '...'  # Solo mostrar parte del token por seguridad
            })
            
            logger.debug(f"[MOCK EMAIL CONTENT] {subject}\nTo: {user.email}\n\n{text_body}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error simulando email de verificación para usuario {user.id}: {e}")
            return False
    
    def send_password_reset_email(self, user: User, token: str) -> bool:
        """Simula el envío de email de reset de contraseña"""
        try:
            subject = "Restablecer contraseña - Team Time Management"
            text_body = f"""
Hola {user.first_name or user.email},

Para restablecer tu contraseña, haz clic en el siguiente enlace:
http://localhost:5173/reset-password?token={token}

Este enlace expirará en 1 hora.

Si no solicitaste este cambio, puedes ignorar este email.

Saludos,
Equipo Team Time Management
            """
            
            email_data = {
                'timestamp': datetime.now().isoformat(),
                'to': user.email,
                'subject': subject,
                'text_body': text_body,
                'email_type': 'password_reset',
                'token': token
            }
            
            self.sent_emails.append(email_data)
            
            logger.info(f"[MOCK EMAIL] Reset de contraseña enviado a {user.email}", extra={
                'email_type': 'password_reset',
                'user_id': user.id,
                'token': token[:10] + '...'
            })
            
            logger.debug(f"[MOCK EMAIL CONTENT] {subject}\nTo: {user.email}\n\n{text_body}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error simulando email de reset para usuario {user.id}: {e}")
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
        
        # Generar contenido HTML simple
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Team Time Management</h2>
            <h3 style="color: #666;">{notification.title}</h3>
            <p>Hola {user.first_name or user.email},</p>
            <p>{notification.message}</p>
            <hr style="margin: 20px 0;">
            <p style="font-size: 12px; color: #999;">
                Tipo: {notification_type_names.get(notification.notification_type.value, 'Notificación')}<br>
                Prioridad: {notification.priority.value}<br>
                Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
            <p style="font-size: 12px; color: #999;">
                Este email fue enviado automáticamente por Team Time Management.<br>
                Si tienes preguntas, contacta con tu administrador del sistema.
            </p>
        </body>
        </html>
        """
        
        # Generar contenido texto plano
        text_body = f"""
Team Time Management - {notification.title}

Hola {user.first_name or user.email},

{notification.message}

Tipo: {notification_type_names.get(notification.notification_type.value, 'Notificación')}
Prioridad: {notification.priority.value}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Este email fue enviado automáticamente por Team Time Management.
Si tienes preguntas, contacta con tu administrador del sistema.
        """
        
        return notification.title, html_body, text_body
    
    def get_sent_emails(self, limit: int = 50) -> List[Dict]:
        """Obtiene la lista de emails enviados (para debugging)"""
        return self.sent_emails[-limit:] if limit else self.sent_emails
    
    def clear_sent_emails(self):
        """Limpia la lista de emails enviados"""
        self.sent_emails.clear()
        logger.info("Lista de emails mock limpiada")
    
    def send_custom_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """
        Simula el envío de un email genérico
        
        Args:
            to_email: Email destino
            subject: Asunto del email
            body: Cuerpo en texto plano
            html_body: Cuerpo en HTML (opcional)
        
        Returns:
            bool: True si se "envió" correctamente
        """
        try:
            email_data = {
                'timestamp': datetime.now().isoformat(),
                'to': to_email,
                'subject': subject,
                'text_body': body,
                'html_body': html_body,
                'email_type': 'custom'
            }
            
            self.sent_emails.append(email_data)
            
            logger.info(f"[MOCK EMAIL] Email genérico enviado a {to_email} - {subject}")
            logger.debug(f"[MOCK EMAIL CONTENT] {subject}\nTo: {to_email}\n\n{body}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error simulando email genérico a {to_email}: {e}")
            return False
    
    def get_email_stats(self) -> Dict:
        """Obtiene estadísticas de emails enviados"""
        if not self.sent_emails:
            return {
                'total_emails': 0,
                'by_type': {},
                'by_priority': {},
                'last_email': None
            }
        
        by_type = {}
        by_priority = {}
        
        for email in self.sent_emails:
            email_type = email.get('email_type', 'notification')
            priority = email.get('priority', 'medium')
            
            by_type[email_type] = by_type.get(email_type, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            'total_emails': len(self.sent_emails),
            'by_type': by_type,
            'by_priority': by_priority,
            'last_email': self.sent_emails[-1]['timestamp'] if self.sent_emails else None
        }
