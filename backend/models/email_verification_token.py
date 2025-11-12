from datetime import datetime
from .base import db

class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_token'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con usuario
    user = db.relationship('User', backref='email_verification_tokens')
    
    def is_expired(self):
        """Verifica si el token ha expirado"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.used and not self.is_expired()
    
    def mark_as_used(self):
        """Marca el token como usado"""
        self.used = True
        self.used_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat(),
            'used': self.used,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat()
        }

