from datetime import datetime
from .base import db

class EmployeeInvitation(db.Model):
    __tablename__ = 'employee_invitation'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    inviter = db.relationship('User', foreign_keys=[invited_by], backref='sent_invitations')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'token': self.token,
            'invited_by': self.invited_by,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_expired': datetime.utcnow() > self.expires_at if self.expires_at else True
        }

    def is_valid(self):
        """Check if invitation is still valid (not used and not expired)"""
        return not self.used and datetime.utcnow() <= self.expires_at

    def __repr__(self):
        return f'<EmployeeInvitation {self.email}>'
