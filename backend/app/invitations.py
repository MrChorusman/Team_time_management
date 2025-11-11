"""
Invitations Blueprint

Endpoints para gestionar invitaciones de empleados
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from models.base import db
from services.invitation_service import InvitationService
import logging

logger = logging.getLogger(__name__)

invitations_bp = Blueprint('invitations', __name__)


def require_auth(f):
    """Decorator para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_admin_or_manager(f):
    """Decorator para requerir rol de admin o manager"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from models.user import User
        
        user_id = request.cookies.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        
        try:
            user = User.query.get(int(user_id))
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            # Verificar si tiene rol de admin o manager
            user_roles = [role.name for role in user.roles]
            if 'admin' not in user_roles and 'manager' not in user_roles:
                return jsonify({'error': 'No tienes permisos para esta acción'}), 403
            
            # Pasar el user_id al endpoint
            return f(user_id=int(user_id), *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            return jsonify({'error': 'Error verificando permisos'}), 500
    
    return decorated_function


@invitations_bp.route('/api/employees/invite', methods=['POST'])
@require_admin_or_manager
def invite_employee(user_id):
    """
    Envía una invitación a un nuevo empleado
    
    Body:
        - email: Email del empleado (requerido)
        - message: Mensaje personalizado (opcional)
    
    Returns:
        - 201: Invitación creada y enviada
        - 400: Email inválido o falta
        - 409: Usuario o invitación ya existe
        - 500: Error del servidor
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        email = data.get('email', '').strip().lower()
        message = data.get('message', '').strip()
        
        # Validar email
        if not email:
            return jsonify({'error': 'El email es requerido'}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        # Enviar invitación
        result = InvitationService.send_invitation(
            email=email,
            invited_by_id=user_id,
            custom_message=message if message else None
        )
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'invitation': result['invitation']
            }), 201
        else:
            # Determinar código de error apropiado
            error_msg = result.get('error', 'Error desconocido')
            if 'ya está registrado' in error_msg or 'ya existe' in error_msg:
                status_code = 409
            else:
                status_code = 400
            
            return jsonify({'error': error_msg}), status_code
    
    except Exception as e:
        logger.error(f"Error en invite_employee: {e}")
        return jsonify({'error': 'Error al procesar la invitación'}), 500


@invitations_bp.route('/api/employees/invitations', methods=['GET'])
@require_admin_or_manager
def get_invitations(user_id):
    """
    Obtiene todas las invitaciones pendientes
    
    Returns:
        - 200: Lista de invitaciones
        - 500: Error del servidor
    """
    try:
        invitations = InvitationService.get_pending_invitations()
        
        return jsonify({
            'invitations': invitations,
            'count': len(invitations)
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo invitaciones: {e}")
        return jsonify({'error': 'Error al obtener invitaciones'}), 500


@invitations_bp.route('/api/employees/invitations/verify', methods=['POST'])
def verify_invitation():
    """
    Verifica si un token de invitación es válido
    
    Body:
        - token: Token de invitación
    
    Returns:
        - 200: Token válido
        - 400: Token inválido o expirado
        - 500: Error del servidor
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'error': 'El token es requerido'}), 400
        
        result = InvitationService.verify_token(token)
        
        if result['valid']:
            return jsonify({
                'valid': True,
                'invitation': result['invitation']
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': result.get('error', 'Token inválido')
            }), 400
    
    except Exception as e:
        logger.error(f"Error verificando invitación: {e}")
        return jsonify({'error': 'Error al verificar la invitación'}), 500


@invitations_bp.route('/api/employees/invitations/<invitation_id>', methods=['DELETE'])
@require_admin_or_manager
def cancel_invitation(user_id, invitation_id):
    """
    Cancela una invitación pendiente
    
    Args:
        invitation_id: ID de la invitación
    
    Returns:
        - 200: Invitación cancelada
        - 404: Invitación no encontrada
        - 500: Error del servidor
    """
    try:
        from models.employee_invitation import EmployeeInvitation
        
        invitation = EmployeeInvitation.query.get(invitation_id)
        
        if not invitation:
            return jsonify({'error': 'Invitación no encontrada'}), 404
        
        invitation.cancel()
        db.session.commit()
        
        return jsonify({'message': 'Invitación cancelada correctamente'}), 200
    
    except Exception as e:
        logger.error(f"Error cancelando invitación: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error al cancelar la invitación'}), 500

