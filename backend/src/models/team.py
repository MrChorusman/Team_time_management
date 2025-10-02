from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Team(db.Model):
    """Modelo para equipos de trabajo"""
    __tablename__ = 'team'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Manager del equipo (relación con Employee)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Estado del equipo
    active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    employees = db.relationship('Employee', backref='team', lazy='dynamic', 
                               foreign_keys='Employee.team_id')
    
    # Relación con el manager (evitar referencia circular)
    manager = db.relationship('Employee', foreign_keys=[manager_id], 
                             post_update=True, uselist=False)
    
    @property
    def employee_count(self):
        """Retorna el número de empleados en el equipo"""
        return self.employees.filter_by(active=True).count()
    
    @property
    def active_employees(self):
        """Retorna solo los empleados activos del equipo"""
        return self.employees.filter_by(active=True).all()
    
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
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'manager_id': self.manager_id,
            'manager_name': self.manager.full_name if self.manager else None,
            'active': self.active,
            'employee_count': self.employee_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_employees:
            data['employees'] = [emp.to_dict() for emp in self.active_employees]
        
        return data
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'<Team {self.name}>'
