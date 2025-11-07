from datetime import datetime, date
from .base import db

class CalendarActivity(db.Model):
    """Modelo para actividades del calendario de empleados"""
    __tablename__ = 'calendar_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con empleado
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    # Información de la actividad
    date = db.Column(db.Date, nullable=False)
    activity_type = db.Column(db.String(10), nullable=False)  # V, A, HLD, G, F, C
    hours = db.Column(db.Float, nullable=True)  # Para HLD, G, F (actividades con horas específicas)
    
    # Horarios para guardias (solo para activity_type = 'G')
    start_time = db.Column(db.Time, nullable=True)  # Horario de inicio (ej: 18:00)
    end_time = db.Column(db.Time, nullable=True)    # Horario de fin (ej: 22:00)
    
    # Información adicional
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Metadatos
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices para optimizar consultas
    __table_args__ = (
        db.Index('idx_calendar_employee_date', 'employee_id', 'date'),
        db.Index('idx_calendar_date_type', 'date', 'activity_type'),
        db.UniqueConstraint('employee_id', 'date', name='uq_employee_date'),
    )
    
    # Definición de tipos de actividad
    ACTIVITY_TYPES = {
        'V': {
            'name': 'Vacaciones',
            'description': 'Días completos de vacaciones',
            'color': '#90EE90',  # Verde claro
            'affects_hours': 'full_day',  # Resta día completo
            'requires_hours': False
        },
        'A': {
            'name': 'Ausencias',
            'description': 'Faltas por enfermedad o motivos personales',
            'color': '#FFFF99',  # Amarillo claro
            'affects_hours': 'full_day',  # Resta día completo
            'requires_hours': False
        },
        'HLD': {
            'name': 'Horas Libre Disposición',
            'description': 'Horas libres (salir antes, llegar tarde)',
            'color': '#006400',  # Verde oscuro
            'affects_hours': 'partial',  # Resta horas específicas
            'requires_hours': True
        },
        'G': {
            'name': 'Guardia',
            'description': 'Horas extra o guardias',
            'color': '#87CEEB',  # Azul claro
            'affects_hours': 'add',  # Suma horas específicas
            'requires_hours': True
        },
        'F': {
            'name': 'Formación/Evento',
            'description': 'Formación, eventos de empresa',
            'color': '#9370DB',  # Morado
            'affects_hours': 'partial',  # Resta horas específicas
            'requires_hours': True
        },
        'C': {
            'name': 'Permiso/Otro',
            'description': 'Otros permisos, citas personales',
            'color': '#ADD8E6',  # Azul claro
            'affects_hours': 'full_day',  # Resta día completo
            'requires_hours': False
        }
    }
    
    @classmethod
    def get_activity_types(cls):
        """Retorna los tipos de actividad disponibles"""
        return cls.ACTIVITY_TYPES
    
    @classmethod
    def get_activity_info(cls, activity_type):
        """Obtiene información de un tipo de actividad específico"""
        return cls.ACTIVITY_TYPES.get(activity_type, {})
    
    def validate_activity(self):
        """Valida la actividad según su tipo"""
        activity_info = self.get_activity_info(self.activity_type)
        
        if not activity_info:
            return False, f"Tipo de actividad '{self.activity_type}' no válido"
        
        # Verificar si requiere horas
        if activity_info['requires_hours'] and (self.hours is None or self.hours <= 0):
            return False, f"El tipo '{activity_info['name']}' requiere especificar horas"
        
        # Verificar si NO debe tener horas
        if not activity_info['requires_hours'] and self.hours is not None:
            return False, f"El tipo '{activity_info['name']}' no debe especificar horas"
        
        # Verificar límites de horas
        if self.hours is not None:
            if self.hours < 0:
                return False, "Las horas no pueden ser negativas"
            if self.hours > 24:
                return False, "Las horas no pueden ser más de 24"
        
        return True, "Actividad válida"
    
    def can_be_created_on_date(self):
        """Verifica si la actividad puede ser creada en la fecha especificada"""
        # No se pueden crear actividades en fechas pasadas (excepto admin)
        if self.date < date.today():
            return False, "No se pueden crear actividades en fechas pasadas"
        
        # Verificar si es fin de semana
        if self.date.weekday() >= 5:  # Sábado=5, Domingo=6
            return False, "No se pueden crear actividades en fines de semana"
        
        # Verificar si es festivo
        if self.employee and self.employee.is_holiday(self.date):
            return False, "No se pueden crear actividades en días festivos"
        
        return True, "Fecha válida"
    
    def calculate_hours_impact(self):
        """Calcula el impacto en horas de esta actividad"""
        if not self.employee:
            return 0
        
        daily_theoretical = self.employee.get_daily_hours(self.date)
        activity_info = self.get_activity_info(self.activity_type)
        
        if activity_info['affects_hours'] == 'full_day':
            # Actividades que afectan el día completo (V, A, C)
            return -daily_theoretical
        elif activity_info['affects_hours'] == 'partial':
            # Actividades que restan horas específicas (HLD, F)
            return -(self.hours or 0)
        elif activity_info['affects_hours'] == 'add':
            # Actividades que suman horas (G)
            return self.hours or 0
        
        return 0
    
    def get_display_text(self):
        """Obtiene el texto a mostrar en el calendario"""
        activity_info = self.get_activity_info(self.activity_type)
        
        if activity_info['requires_hours'] and self.hours:
            if activity_info['affects_hours'] == 'add':
                return f"{self.activity_type} +{self.hours}h"
            else:
                return f"{self.activity_type} -{self.hours}h"
        else:
            return self.activity_type
    
    def get_color(self):
        """Obtiene el color para mostrar en el calendario"""
        activity_info = self.get_activity_info(self.activity_type)
        return activity_info.get('color', '#CCCCCC')
    
    @classmethod
    def get_team_activities_for_date(cls, team_id, target_date):
        """Obtiene todas las actividades de un equipo para una fecha específica"""
        from .employee import Employee
        
        return cls.query.join(Employee).filter(
            Employee.team_id == team_id,
            cls.date == target_date
        ).all()
    
    @classmethod
    def check_vacation_conflicts(cls, team_id, target_date, exclude_employee_id=None):
        """Verifica conflictos de vacaciones en un equipo para una fecha"""
        from .employee import Employee
        
        query = cls.query.join(Employee).filter(
            Employee.team_id == team_id,
            cls.date == target_date,
            cls.activity_type == 'V'
        )
        
        if exclude_employee_id:
            query = query.filter(cls.employee_id != exclude_employee_id)
        
        conflicts = query.all()
        return len(conflicts), conflicts
    
    def to_dict(self):
        """Convierte la actividad a diccionario para JSON"""
        activity_info = self.get_activity_info(self.activity_type)
        
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'date': self.date.isoformat() if self.date else None,
            'activity_type': self.activity_type,
            'activity_name': activity_info.get('name', ''),
            'hours': self.hours,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'description': self.description,
            'notes': self.notes,
            'display_text': self.get_display_text(),
            'color': self.get_color(),
            'hours_impact': self.calculate_hours_impact(),
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"{self.employee.full_name if self.employee else 'Unknown'} - {self.activity_type} ({self.date})"
    
    def __repr__(self):
        return f'<CalendarActivity {self.activity_type} {self.date} Employee:{self.employee_id}>'
