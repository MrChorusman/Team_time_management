from flask import current_app, render_template_string
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
        
        # Plantilla base HTML
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .content { background-color: #ffffff; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; }
                .footer { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px; font-size: 12px; color: #6c757d; }
                .button { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
                .priority-high { border-left: 4px solid #dc3545; }
                .priority-medium { border-left: 4px solid #ffc107; }
                .priority-low { border-left: 4px solid #28a745; }
                .priority-urgent { border-left: 4px solid #dc3545; background-color: #f8d7da; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Team Time Management</h2>
                <p>Hola {{ user_name }},</p>
            </div>
            
            <div class="content priority-{{ priority }}">
                <h3>{{ title }}</h3>
                <p>{{ message }}</p>
                
                {% if action_url %}
                <p>
                    <a href="{{ action_url }}" class="button">Ver detalles</a>
                </p>
                {% endif %}
                
                {% if additional_info %}
                <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                    {{ additional_info | safe }}
                </div>
                {% endif %}
            </div>
            
            <div class="footer">
                <p>Este email fue enviado automáticamente por Team Time Management.</p>
                <p>Fecha: {{ sent_date }}</p>
                <p>Si tienes preguntas, contacta con tu administrador del sistema.</p>
            </div>
        </body>
        </html>
        """
        
        # Plantilla base texto plano
        text_template = """
        Team Time Management
        
        Hola {{ user_name }},
        
        {{ title }}
        
        {{ message }}
        
        {% if action_url %}
        Para más detalles, visita: {{ action_url }}
        {% endif %}
        
        {% if additional_info_text %}
        {{ additional_info_text }}
        {% endif %}
        
        ---
        Este email fue enviado automáticamente por Team Time Management.
        Fecha: {{ sent_date }}
        """
        
        # Datos base para las plantillas
        template_data = {
            'user_name': user.full_name,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority.value if notification.priority else 'medium',
            'sent_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'action_url': notification.data.get('action_url') if notification.data else None
        }
        
        # Contenido adicional según el tipo de notificación
        additional_info = ""
        additional_info_text = ""
        
        if notification.notification_type.value == 'employee_registration':
            template_data['subject'] = f"Nueva solicitud de empleado - {notification.data.get('employee_name', '')}"
            additional_info = f"""
            <h4>Detalles de la solicitud:</h4>
            <ul>
                <li><strong>Empleado:</strong> {notification.data.get('employee_name', 'N/A')}</li>
                <li><strong>Equipo:</strong> {notification.data.get('team_name', 'N/A')}</li>
            </ul>
            <p>Por favor, revisa y aprueba esta solicitud lo antes posible.</p>
            """
            additional_info_text = f"""
Detalles de la solicitud:
- Empleado: {notification.data.get('employee_name', 'N/A')}
- Equipo: {notification.data.get('team_name', 'N/A')}

Por favor, revisa y aprueba esta solicitud lo antes posible.
            """
        
        elif notification.notification_type.value == 'employee_approved':
            template_data['subject'] = "¡Tu cuenta ha sido aprobada!"
            additional_info = """
            <p>Ya puedes acceder a todas las funcionalidades de la aplicación:</p>
            <ul>
                <li>Gestionar tu calendario personal</li>
                <li>Marcar vacaciones y ausencias</li>
                <li>Ver el calendario de tu equipo</li>
                <li>Acceder a tus reportes personales</li>
            </ul>
            """
            additional_info_text = """
Ya puedes acceder a todas las funcionalidades de la aplicación:
- Gestionar tu calendario personal
- Marcar vacaciones y ausencias
- Ver el calendario de tu equipo
- Acceder a tus reportes personales
            """
        
        elif notification.notification_type.value == 'vacation_conflict':
            template_data['subject'] = f"Conflicto de vacaciones - {notification.data.get('conflict_date', '')}"
            employees = notification.data.get('employees', [])
            employee_list = ", ".join([emp['name'] for emp in employees])
            
            additional_info = f"""
            <h4>Empleados con vacaciones en conflicto:</h4>
            <ul>
                {''.join([f"<li>{emp['name']}</li>" for emp in employees])}
            </ul>
            <p>Te recomendamos coordinar con tu equipo para resolver este conflicto.</p>
            """
            additional_info_text = f"""
Empleados con vacaciones en conflicto:
{chr(10).join([f"- {emp['name']}" for emp in employees])}

Te recomendamos coordinar con tu equipo para resolver este conflicto.
            """
        
        elif notification.notification_type.value == 'calendar_change':
            template_data['subject'] = f"Cambios en calendario - {notification.data.get('employee_name', '')}"
            additional_info = f"""
            <h4>Resumen de cambios:</h4>
            <p>{notification.data.get('changes', 'No hay detalles disponibles')}</p>
            """
            additional_info_text = f"""
Resumen de cambios:
{notification.data.get('changes', 'No hay detalles disponibles')}
            """
        
        elif notification.notification_type.value == 'weekly_report':
            template_data['subject'] = f"Reporte semanal - Equipo {notification.data.get('team_name', '')}"
            upcoming_vacations = notification.data.get('upcoming_vacations', [])
            
            if upcoming_vacations:
                vacation_list = ""
                vacation_text_list = ""
                for vacation in upcoming_vacations:
                    vacation_list += f"<li>{vacation['employee_name']} - {vacation['date_formatted']}</li>"
                    vacation_text_list += f"- {vacation['employee_name']} - {vacation['date_formatted']}\n"
                
                additional_info = f"""
                <h4>Vacaciones próximas (próximos 10 días):</h4>
                <ul>{vacation_list}</ul>
                """
                additional_info_text = f"""
Vacaciones próximas (próximos 10 días):
{vacation_text_list}
                """
            else:
                additional_info = "<p>No hay vacaciones programadas para los próximos 10 días.</p>"
                additional_info_text = "No hay vacaciones programadas para los próximos 10 días."
        
        else:
            template_data['subject'] = notification.title
        
        # Añadir información adicional a los datos de la plantilla
        template_data['additional_info'] = additional_info
        template_data['additional_info_text'] = additional_info_text
        
        # Renderizar plantillas
        html_body = render_template_string(html_template, **template_data)
        text_body = render_template_string(text_template, **template_data)
        
        return template_data['subject'], html_body, text_body
    
    def send_custom_email(self, recipients: List[str], subject: str, 
                         html_body: str = None, text_body: str = None) -> bool:
        """Envía un email personalizado"""
        try:
            if not self.mail:
                logger.error("Servicio de email no inicializado")
                return False
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                body=text_body
            )
            
            self.mail.send(msg)
            logger.info(f"Email personalizado enviado a {len(recipients)} destinatarios")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email personalizado: {e}")
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
                success = self.send_notification_email(notification)
                if success:
                    notification.mark_email_sent()
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error en notificación {notification.id}: {e}")
                logger.error(f"Error enviando notificación {notification.id}: {e}")
        
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
            
            # Intentar enviar un email de prueba
            test_msg = Message(
                subject="Test - Team Time Management",
                recipients=[current_app.config.get('MAIL_USERNAME')],
                body="Este es un email de prueba del sistema Team Time Management."
            )
            
            self.mail.send(test_msg)
            
            return {
                'success': True,
                'message': 'Email de prueba enviado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en configuración de email: {e}'
            }
