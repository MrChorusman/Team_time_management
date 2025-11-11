"""
Invitation Service

Maneja la lógica de negocio para invitaciones de empleados
"""

import os
from datetime import datetime
from models.base import db
from models.employee_invitation import EmployeeInvitation
from models.user import User
from services.email_service import send_email
import logging

logger = logging.getLogger(__name__)


class InvitationService:
    """Servicio para gestionar invitaciones de empleados"""
    
    @staticmethod
    def send_invitation(email, invited_by_id, custom_message=None):
        """
        Envía una invitación por email a un nuevo empleado
        
        Args:
            email: Email del empleado a invitar
            invited_by_id: ID del usuario que envía la invitación
            custom_message: Mensaje personalizado opcional
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar si el usuario ya existe
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {
                    'success': False,
                    'error': 'Este email ya está registrado en el sistema'
                }
            
            # Verificar si ya hay una invitación pendiente
            existing_invitation = EmployeeInvitation.query.filter_by(
                email=email,
                status='pending'
            ).first()
            
            if existing_invitation and existing_invitation.is_valid():
                return {
                    'success': False,
                    'error': 'Ya existe una invitación pendiente para este email'
                }
            
            # Si existe una invitación expirada o usada, cancelarla
            if existing_invitation:
                existing_invitation.cancel()
                db.session.commit()
            
            # Crear nueva invitación
            invitation = EmployeeInvitation.create_invitation(
                email=email,
                invited_by_id=invited_by_id,
                expiry_hours=48
            )
            
            db.session.add(invitation)
            db.session.commit()
            
            # Obtener información del usuario que invita
            invited_by = User.query.get(invited_by_id)
            inviter_name = f"{invited_by.first_name} {invited_by.last_name}".strip() if invited_by.first_name or invited_by.last_name else invited_by.email
            
            # Construir el link de invitación
            frontend_url = os.getenv('FRONTEND_URL', 'https://team-time-management.vercel.app')
            invitation_link = f"{frontend_url}/employee/register?token={invitation.token}"
            
            # Enviar email
            try:
                email_sent = InvitationService._send_invitation_email(
                    to_email=email,
                    invitation_link=invitation_link,
                    inviter_name=inviter_name,
                    custom_message=custom_message,
                    expires_hours=48
                )
                
                if not email_sent:
                    logger.warning(f"Email no pudo ser enviado a {email}, pero invitación creada")
                    
            except Exception as e:
                logger.error(f"Error enviando email de invitación: {e}")
                # No fallar si el email no se puede enviar, la invitación sigue siendo válida
            
            return {
                'success': True,
                'invitation': invitation.to_dict(),
                'message': 'Invitación enviada correctamente'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando invitación: {e}")
            return {
                'success': False,
                'error': 'Error al procesar la invitación. Intenta nuevamente.'
            }
    
    @staticmethod
    def _send_invitation_email(to_email, invitation_link, inviter_name, custom_message, expires_hours):
        """
        Envía el email de invitación
        
        Args:
            to_email: Email destino
            invitation_link: Link de invitación
            inviter_name: Nombre de quien invita
            custom_message: Mensaje personalizado
            expires_hours: Horas hasta expiración
        
        Returns:
            bool: True si se envió correctamente
        """
        subject = f"🎉 Invitación para unirte a Team Time Management"
        
        # HTML del email
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    color: #ffffff;
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .content h2 {{
                    color: #1a202c;
                    font-size: 24px;
                    margin-top: 0;
                    margin-bottom: 20px;
                }}
                .content p {{
                    color: #4a5568;
                    font-size: 16px;
                    margin-bottom: 20px;
                }}
                .custom-message {{
                    background-color: #edf2f7;
                    border-left: 4px solid #667eea;
                    padding: 15px 20px;
                    margin: 25px 0;
                    font-style: italic;
                    color: #2d3748;
                }}
                .cta-button {{
                    display: inline-block;
                    padding: 16px 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #ffffff !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                    margin: 20px 0;
                    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
                    transition: transform 0.2s;
                }}
                .cta-button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 8px rgba(102, 126, 234, 0.4);
                }}
                .info-box {{
                    background-color: #f7fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                }}
                .info-box h3 {{
                    margin-top: 0;
                    color: #2d3748;
                    font-size: 18px;
                }}
                .info-box ul {{
                    margin: 10px 0;
                    padding-left: 25px;
                    color: #4a5568;
                }}
                .info-box li {{
                    margin-bottom: 8px;
                }}
                .footer {{
                    background-color: #f7fafc;
                    padding: 30px 20px;
                    text-align: center;
                    color: #718096;
                    font-size: 14px;
                    border-top: 1px solid #e2e8f0;
                }}
                .footer a {{
                    color: #667eea;
                    text-decoration: none;
                }}
                .warning {{
                    background-color: #fef5e7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px 20px;
                    margin: 25px 0;
                    color: #92400e;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Team Time Management</h1>
                </div>
                
                <div class="content">
                    <h2>¡Bienvenido/a al equipo!</h2>
                    
                    <p>Hola,</p>
                    
                    <p><strong>{inviter_name}</strong> te ha invitado a unirte a <strong>Team Time Management</strong>, nuestra plataforma para la gestión eficiente del tiempo y recursos del equipo.</p>
                    
                    {f'<div class="custom-message"><p>{custom_message}</p></div>' if custom_message else ''}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{invitation_link}" class="cta-button">
                            ✨ Completar mi Registro
                        </a>
                    </div>
                    
                    <div class="info-box">
                        <h3>📋 Próximos pasos:</h3>
                        <ul>
                            <li>Haz clic en el botón para acceder al formulario de registro</li>
                            <li>Completa tu información personal y profesional</li>
                            <li>Tu manager revisará y aprobará tu perfil</li>
                            <li>¡Empieza a usar la plataforma!</li>
                        </ul>
                    </div>
                    
                    <div class="warning">
                        <strong>⏰ Importante:</strong> Este enlace expirará en <strong>{expires_hours} horas</strong>. Si no completas tu registro antes de esa fecha, deberás solicitar una nueva invitación.
                    </div>
                    
                    <p style="margin-top: 30px; color: #718096; font-size: 14px;">
                        Si no puedes hacer clic en el botón, copia y pega este enlace en tu navegador:<br>
                        <a href="{invitation_link}" style="color: #667eea; word-break: break-all;">{invitation_link}</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p>Este email fue enviado por Team Time Management</p>
                    <p style="margin-top: 10px;">
                        Si recibiste este email por error, puedes ignorarlo de forma segura.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Texto plano como fallback
        text_body = f"""
        ¡Bienvenido/a a Team Time Management!
        
        {inviter_name} te ha invitado a unirte a nuestra plataforma para la gestión del tiempo y recursos del equipo.
        
        {f'Mensaje personalizado: {custom_message}' if custom_message else ''}
        
        Para completar tu registro, visita el siguiente enlace:
        {invitation_link}
        
        Este enlace expirará en {expires_hours} horas.
        
        Si recibiste este email por error, puedes ignorarlo de forma segura.
        
        ---
        Team Time Management
        """
        
        return send_email(
            to_email=to_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )
    
    @staticmethod
    def verify_token(token):
        """
        Verifica un token de invitación
        
        Args:
            token: Token a verificar
        
        Returns:
            dict: Resultado de la verificación
        """
        try:
            invitation = EmployeeInvitation.query.filter_by(token=token).first()
            
            if not invitation:
                return {
                    'valid': False,
                    'error': 'Token de invitación no válido'
                }
            
            if not invitation.is_valid():
                if invitation.status == 'accepted':
                    return {
                        'valid': False,
                        'error': 'Esta invitación ya ha sido utilizada'
                    }
                elif invitation.expires_at < datetime.utcnow():
                    invitation.mark_as_expired()
                    db.session.commit()
                    return {
                        'valid': False,
                        'error': 'Esta invitación ha expirado. Solicita una nueva invitación.'
                    }
                else:
                    return {
                        'valid': False,
                        'error': 'Esta invitación no está disponible'
                    }
            
            return {
                'valid': True,
                'invitation': invitation.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return {
                'valid': False,
                'error': 'Error al verificar la invitación'
            }
    
    @staticmethod
    def mark_invitation_as_used(token):
        """
        Marca una invitación como usada
        
        Args:
            token: Token de la invitación
        
        Returns:
            bool: True si se marcó correctamente
        """
        try:
            invitation = EmployeeInvitation.query.filter_by(token=token).first()
            
            if invitation and invitation.is_valid():
                invitation.mark_as_used()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marcando invitación como usada: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_pending_invitations():
        """
        Obtiene todas las invitaciones pendientes
        
        Returns:
            list: Lista de invitaciones pendientes
        """
        try:
            invitations = EmployeeInvitation.query.filter_by(
                status='pending'
            ).order_by(EmployeeInvitation.created_at.desc()).all()
            
            return [inv.to_dict() for inv in invitations]
            
        except Exception as e:
            logger.error(f"Error obteniendo invitaciones pendientes: {e}")
            return []

