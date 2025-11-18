from datetime import datetime

from .base import db


class TeamMembership(db.Model):
    """Relación entre empleados y equipos con soporte para múltiples pertenencias."""

    __tablename__ = 'team_membership'
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'team_id', name='uq_team_membership_employee_team'),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    role = db.Column(db.String(120))
    allocation_percent = db.Column(db.Float)  # Porcentaje opcional (0-100)
    is_primary = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='memberships')
    team = db.relationship('Team', back_populates='memberships')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'role': self.role,
            'allocation_percent': self.allocation_percent,
            'is_primary': self.is_primary,
            'active': self.active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

