from datetime import datetime, date

from .base import db


project_team_link = db.Table(
    'project_team_link',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)


class Project(db.Model):
    """Proyecto o iniciativa facturable."""

    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_name = db.Column(db.String(200))
    status = db.Column(db.String(50), default='planned')  # planned, in_progress, paused, closed
    service_line = db.Column(db.String(100))
    billing_model = db.Column(db.String(50))  # t&m, fixed_price, retainer, etc
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget_hours = db.Column(db.Float)
    budget_amount = db.Column(db.Float)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manager = db.relationship('Employee', foreign_keys=[manager_id], backref='managed_projects', lazy='joined')
    teams = db.relationship('Team', secondary=project_team_link, back_populates='projects')
    assignments = db.relationship('ProjectAssignment', back_populates='project', cascade='all, delete-orphan')

    def to_dict(self, include_assignments=False):
        data = {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'client_name': self.client_name,
            'status': self.status,
            'service_line': self.service_line,
            'billing_model': self.billing_model,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date,
            'budget_hours': self.budget_hours,
            'budget_amount': self.budget_amount,
            'manager_id': self.manager_id,
            'manager_name': self.manager.full_name if self.manager else None,
            'active': self.active,
            'teams': [
                {
                    'id': team.id,
                    'name': team.name
                } for team in self.teams
            ],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_assignments:
            data['assignments'] = [assignment.to_dict(include_employee=True) for assignment in self.assignments if assignment.active]

        return data


class ProjectAssignment(db.Model):
    """Asignación de un empleado a un proyecto con porcentaje."""

    __tablename__ = 'project_assignment'
    __table_args__ = (
        db.UniqueConstraint('project_id', 'employee_id', name='uq_project_assignment_employee'),
    )

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))  # Opcional: equipo desde el cual se factura
    role = db.Column(db.String(120))
    allocation_percent = db.Column(db.Float)  # Porcentaje de dedicación
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', back_populates='assignments')
    employee = db.relationship('Employee', back_populates='project_assignments')
    team = db.relationship('Team', lazy='joined')

    def to_dict(self, include_employee=False):
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'employee_id': self.employee_id,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'role': self.role,
            'allocation_percent': self.allocation_percent,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date,
            'active': self.active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if self.project:
            data['project_name'] = self.project.name
            data['project_code'] = self.project.code

        if include_employee and self.employee:
            data['employee'] = {
                'id': self.employee.id,
                'full_name': self.employee.full_name,
                'team_id': self.employee.team_id,
                'team_name': self.employee.team.name if self.employee.team else None
            }

        return data

