from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.base import db
from models.employee_invitation import EmployeeInvitation
from models.user import User
from services.auth_service import token_required, admin_or_manager_required
from services.email_service import send_invitation_email
import secrets
import logging

logger = logging.getLogger(__name__)

employee_invitations_bp = Blueprint('employee_invitations', __name__)

@employee_invitations_bp.route('/api/employees/invite', methods=['POST'])
@token_required
@admin_or_manager_required
def invite_employee(current_user):
    """
    Invitar a un empleado por email
    Genera un token único y envía email de invitación
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email es requerido'}), 400
        
        email = data['email'].lower().strip()
        
        # Validar formato de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Email inválido'}), 400
        
        # Verificar si el email ya existe como usuario
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Este email ya tiene una cuenta en el sistema'}), 409
        
        # Verificar si ya existe una invitación activa (no usada y no expirada)
        existing_invitation = EmployeeInvitation.query.filter_by(
            email=email,
            used=False
        ).filter(
            EmployeeInvitation.expires_at > datetime.utcnow()
        ).first()
        
        if existing_invitation:
            # Reenviar la invitación existente
            token = existing_invitation.token
            expires_at = existing_invitation.expires_at
        else:
            # Generar token único y seguro
            token = secrets.token_urlsafe(32)
            
            # La invitación expira en 7 días
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            # Crear nueva invitación
            invitation = EmployeeInvitation(
                email=email,
                token=token,
                invited_by=current_user.id,
                expires_at=expires_at
            )
            
            db.session.add(invitation)
            db.session.commit()
        
        # Enviar email de invitación
        frontend_url = request.headers.get('Origin', 'https://team-time-management.vercel.app')
        invitation_link = f"{frontend_url}/employee/register?token={token}"
        
        try:
            send_invitation_email(
                to_email=email,
                invitation_link=invitation_link,
                inviter_name=current_user.first_name or current_user.email,
                expires_days=7
            )
            
            logger.info(f"Invitación enviada a {email} por {current_user.email}")
            
            return jsonify({
                'message': 'Invitación enviada exitosamente',
                'email': email,
                'expires_at': expires_at.isoformat(),
                'invitation_link': invitation_link if request.headers.get('X-Debug') == 'true' else None
            }), 201
            
        except Exception as email_error:
            logger.error(f"Error enviando email de invitación: {email_error}")
            # No fallar si el email no se envía, pero informar
            return jsonify({
                'message': 'Invitación creada pero hubo un error enviando el email',
                'email': email,
                'expires_at': expires_at.isoformat(),
                'invitation_link': invitation_link,
                'email_error': str(email_error)
            }), 201
    
    except Exception as e:
        logger.error(f"Error creando invitación: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500


@employee_invitations_bp.route('/api/employees/invite/<token>', methods=['GET'])
def validate_invitation(token):
    """
    Validar un token de invitación
    No requiere autenticación (es para usuarios nuevos)
    """
    try:
        invitation = EmployeeInvitation.query.filter_by(token=token).first()
        
        if not invitation:
            return jsonify({'error': 'Invitación no encontrada'}), 404
        
        if invitation.used:
            return jsonify({'error': 'Esta invitación ya ha sido utilizada'}), 410
        
        if datetime.utcnow() > invitation.expires_at:
            return jsonify({'error': 'Esta invitación ha expirado'}), 410
        
        return jsonify({
            'valid': True,
            'email': invitation.email,
            'expires_at': invitation.expires_at.isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error validando invitación: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@employee_invitations_bp.route('/api/employees/invite/<token>/use', methods=['POST'])
def mark_invitation_used(token):
    """
    Marcar una invitación como usada
    Llamado después de que el usuario complete su registro
    """
    try:
        invitation = EmployeeInvitation.query.filter_by(token=token).first()
        
        if not invitation:
            return jsonify({'error': 'Invitación no encontrada'}), 404
        
        if invitation.used:
            return jsonify({'error': 'Esta invitación ya ha sido utilizada'}), 410
        
        invitation.used = True
        invitation.used_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Invitación marcada como usada'}), 200
    
    except Exception as e:
        logger.error(f"Error marcando invitación como usada: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

