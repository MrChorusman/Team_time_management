"""
Employee Invitation Model

Maneja las invitaciones enviadas a nuevos empleados
"""

from datetime import datetime, timedelta
from models.base import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
import secrets


class EmployeeInvitation(db.Model):
    """Modelo para invitaciones de empleados"""
    
    __tablename__ = 'employee_invitations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), nullable=False, unique=True)
    token = db.Column(db.String(255), nullable=False, unique=True)
    invited_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, expired, cancelled
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el usuario que invitó
    invited_by = db.relationship('User', backref='sent_invitations')
    
    @staticmethod
    def generate_token():
        """Genera un token seguro para la invitación"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_invitation(email, invited_by_id, expiry_hours=48):
        """
        Crea una nueva invitación
        
        Args:
            email: Email del empleado a invitar
            invited_by_id: ID del usuario que envía la invitación
            expiry_hours: Horas hasta que expire (default: 48h)
        
        Returns:
            EmployeeInvitation: La invitación creada
        """
        token = EmployeeInvitation.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        invitation = EmployeeInvitation(
            email=email,
            token=token,
            invited_by_id=invited_by_id,
            expires_at=expires_at
        )
        
        return invitation
    
    def is_valid(self):
        """Verifica si la invitación es válida"""
        return (
            self.status == 'pending' and
            self.expires_at > datetime.utcnow() and
            self.used_at is None
        )
    
    def mark_as_used(self):
        """Marca la invitación como usada"""
        self.status = 'accepted'
        self.used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_expired(self):
        """Marca la invitación como expirada"""
        self.status = 'expired'
        self.updated_at = datetime.utcnow()
    
    def cancel(self):
        """Cancela la invitación"""
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convierte la invitación a diccionario"""
        return {
            'id': str(self.id),
            'email': self.email,
            'status': self.status,
            'invited_by': {
                'id': self.invited_by.id,
                'email': self.invited_by.email,
                'first_name': self.invited_by.first_name,
                'last_name': self.invited_by.last_name
            } if self.invited_by else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_valid': self.is_valid()
        }

