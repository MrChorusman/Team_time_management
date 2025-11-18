from datetime import datetime
from types import SimpleNamespace

from .base import db
from .team_membership import TeamMembership
from .project import project_team_link

class Team(db.Model):
    """Modelo para equipos de trabajo"""
    __tablename__ = 'team'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Manager del equipo (relación con Employee)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    employees = db.relationship(
        'Employee',
        backref='team',
        lazy='dynamic',
        foreign_keys='Employee.team_id'
    )
    memberships = db.relationship(
        'TeamMembership',
        back_populates='team',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    projects = db.relationship(
        'Project',
        secondary=project_team_link,
        back_populates='teams',
        lazy='selectin'
    )
    
    # Relación con el manager (evitar referencia circular)
    manager = db.relationship('Employee', foreign_keys=[manager_id], 
                             post_update=True, uselist=False)
    
    @property
    def employee_count(self):
        """Retorna el número de empleados en el equipo considerando membresías activas."""
        return len(self._active_memberships())

    def _active_memberships(self):
        def build_membership_stub(employee):
            return SimpleNamespace(
                id=None,
                employee=employee,
                employee_id=employee.id if employee else None,
                team_id=self.id,
                allocation_percent=None,
                role=None,
                is_primary=True if employee and employee.team_id == self.id else False,
                active=True
            )

        if not self.memberships or len(self.memberships) == 0:
            # Fallback temporal para compatibilidad con datos anteriores
            fallback_employees = []
            try:
                fallback_employees = self.employees.filter_by(active=True).all()
            except Exception:
                fallback_employees = self.employees.all()

            memberships = [build_membership_stub(employee) for employee in fallback_employees]
        else:
            memberships = [
                membership for membership in self.memberships
                if membership.active and membership.employee and membership.employee.active
            ]

        # Asegurar que el manager esté incluido si es miembro activo
        if self.manager and self.manager.active:
            manager_present = any(
                membership.employee_id == self.manager.id for membership in memberships
            )
            if not manager_present and self.manager.team_id == self.id:
                memberships.append(build_membership_stub(self.manager))

        return memberships
    
    @property
    def active_employees(self):
        """Retorna solo los empleados activos del equipo mediante membresías."""
        return [membership.employee for membership in self._active_memberships()]
    
    def get_team_calendar_activities(self, start_date=None, end_date=None):
        """Obtiene todas las actividades del calendario del equipo"""
        from .calendar_activity import CalendarActivity
        
        query = CalendarActivity.query.join(
            'employee'
        ).filter(
            CalendarActivity.employee_id.in_([emp.id for emp in self.active_employees])
        )
        
        if start_date:
            query = query.filter(CalendarActivity.date >= start_date)
        if end_date:
            query = query.filter(CalendarActivity.date <= end_date)
            
        return query.order_by(CalendarActivity.date).all()
    
    def get_team_hours_summary(self, year=None, month=None):
        """Calcula resumen de horas del equipo"""
        if not year:
            year = datetime.now().year
        
        summary = {
            'total_theoretical_hours': 0,
            'total_actual_hours': 0,
            'total_vacation_days': 0,
            'total_absence_days': 0,
            'total_hld_hours': 0,
            'total_guard_hours': 0,
            'employees': []
        }
        
        for employee in self.active_employees:
            emp_summary = employee.get_hours_summary(year, month)
            summary['total_theoretical_hours'] += emp_summary['theoretical_hours']
            summary['total_actual_hours'] += emp_summary['actual_hours']
            summary['total_vacation_days'] += emp_summary['vacation_days']
            summary['total_absence_days'] += emp_summary['absence_days']
            summary['total_hld_hours'] += emp_summary['hld_hours']
            summary['total_guard_hours'] += emp_summary['guard_hours']
            summary['employees'].append({
                'employee': employee.to_dict(),
                'summary': emp_summary
            })
        
        # Calcular eficiencia del equipo
        if summary['total_theoretical_hours'] > 0:
            summary['efficiency'] = (summary['total_actual_hours'] / summary['total_theoretical_hours']) * 100
        else:
            summary['efficiency'] = 0
        
        return summary
    
    def check_vacation_conflicts(self, date, exclude_employee_id=None):
        """Verifica si hay conflictos de vacaciones en una fecha"""
        from .calendar_activity import CalendarActivity
        
        query = CalendarActivity.query.join(
            'employee'
        ).filter(
            CalendarActivity.employee_id.in_([emp.id for emp in self.active_employees]),
            CalendarActivity.date == date,
            CalendarActivity.activity_type == 'V'  # Vacaciones
        )
        
        if exclude_employee_id:
            query = query.filter(CalendarActivity.employee_id != exclude_employee_id)
        
        conflicts = query.all()
        return len(conflicts), conflicts
    
    def to_dict(self, include_employees=False):
        """Convierte el equipo a diccionario para JSON"""
        try:
            data = {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'manager_id': self.manager_id,
                'manager_name': self.manager.full_name if self.manager else None,
                'manager': {
                    'id': self.manager.id,
                    'full_name': self.manager.full_name,
                    'name': self.manager.full_name
                } if self.manager else None,
                'active': True,  # Todos los equipos están activos (no hay columna active en DB)
                'employee_count': self.employee_count,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
            
            if include_employees:
                try:
                    data['employees'] = [emp.to_dict() for emp in self.active_employees]
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error serializando empleados del equipo {self.id}: {e}")
                    data['employees'] = []
            
            return data
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error serializando equipo {self.id}: {e}")
            # Devolver datos mínimos en caso de error
            return {
                'id': self.id,
                'name': self.name or 'Sin nombre',
                'description': self.description,
                'manager_id': self.manager_id,
                'manager_name': None,
                'manager': None,
                'active': True,
                'employee_count': 0,
                'created_at': None,
                'updated_at': None
            }
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'<Team {self.name}>'
