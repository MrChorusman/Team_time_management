from datetime import datetime, date
from calendar import monthrange
import json
from .base import db

class Employee(db.Model):
    """Modelo para empleados"""
    __tablename__ = 'employee'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con usuario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Información básica
    full_name = db.Column(db.String(200), nullable=False)
    
    # Relación con equipo
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    
    # Configuración horaria
    hours_monday_thursday = db.Column(db.Float, nullable=False, default=8.0)
    hours_friday = db.Column(db.Float, nullable=False, default=7.0)
    hours_summer = db.Column(db.Float, nullable=True)
    has_summer_schedule = db.Column(db.Boolean, default=False)
    summer_months = db.Column(db.Text)  # JSON array de meses
    
    # Beneficios laborales
    annual_vacation_days = db.Column(db.Integer, nullable=False, default=22)
    annual_hld_hours = db.Column(db.Integer, nullable=False, default=40)
    
    # Tarifa por hora (solo visible para admin)
    hourly_rate = db.Column(db.Float, nullable=True)  # Tarifa en euros/hora
    
    # Ubicación geográfica (estructura jerárquica global)
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=True)  # Estado/Provincia/Comunidad
    city = db.Column(db.String(100), nullable=True)
    
    # Estado del empleado
    active = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)  # Aprobado por manager
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    calendar_activities = db.relationship(
        'CalendarActivity',
        backref='employee',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    memberships = db.relationship(
        'TeamMembership',
        back_populates='employee',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    project_assignments = db.relationship(
        'ProjectAssignment',
        back_populates='employee',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    
    @property
    def summer_months_list(self):
        """Retorna la lista de meses de verano"""
        if self.summer_months:
            try:
                return json.loads(self.summer_months)
            except:
                return []
        return []
    
    @summer_months_list.setter
    def summer_months_list(self, months):
        """Establece la lista de meses de verano"""
        if months:
            self.summer_months = json.dumps(months)
        else:
            self.summer_months = None
    
    def get_daily_hours(self, target_date):
        """Calcula las horas teóricas para una fecha específica"""
        if not isinstance(target_date, date):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # Verificar si es fin de semana
        if target_date.weekday() >= 5:  # Sábado=5, Domingo=6
            return 0
        
        # Verificar si es festivo
        if self.is_holiday(target_date):
            return 0
        
        # Verificar si es horario de verano
        if self.has_summer_schedule and self.is_summer_month(target_date.month):
            return self.hours_summer or 7.0
        
        # Horario normal
        if target_date.weekday() == 4:  # Viernes
            return self.hours_friday
        else:  # Lunes a Jueves
            return self.hours_monday_thursday
    
    def is_summer_month(self, month):
        """Verifica si un mes es de horario de verano"""
        if not self.has_summer_schedule:
            return False
        
        summer_months = self.summer_months_list
        return month in summer_months
    
    def is_holiday(self, target_date):
        """Verifica si una fecha es festivo para este empleado"""
        from .holiday import Holiday
        from utils.country_mapper import get_country_variants
        
        # Obtener variantes del país del empleado
        variants = get_country_variants(self.country)
        countries_to_search = []
        
        if variants:
            countries_to_search = [variants['en'], variants['es']]
        else:
            countries_to_search = [self.country]
        
        holidays = Holiday.query.filter(
            Holiday.date == target_date,
            Holiday.country.in_(countries_to_search)
        ).filter(
            (Holiday.region.is_(None)) |  # Festivos nacionales
            (Holiday.region == self.region) |  # Festivos regionales
            (Holiday.city == self.city)  # Festivos locales
        ).first()
        
        return holidays is not None
    
    def get_calendar_activities(self, year=None, month=None):
        """Obtiene las actividades del calendario del empleado"""
        query = self.calendar_activities
        
        if year:
            if month:
                # Mes específico
                start_date = date(year, month, 1)
                _, last_day = monthrange(year, month)
                end_date = date(year, month, last_day)
            else:
                # Año completo
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
            
            query = query.filter(
                self.calendar_activities.c.date >= start_date,
                self.calendar_activities.c.date <= end_date
            )
        
        return query.order_by('date').all()
    
    def get_hours_summary(self, year=None, month=None):
        """Calcula el resumen de horas del empleado"""
        if not year:
            year = datetime.now().year
        
        # Determinar rango de fechas
        if month:
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)
        else:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
        
        # Obtener actividades del período usando la relación directamente
        from models.calendar_activity import CalendarActivity
        activities = CalendarActivity.query.filter(
            CalendarActivity.employee_id == self.id,
            CalendarActivity.date >= start_date,
            CalendarActivity.date <= end_date
        ).all()
        
        # Crear diccionario de actividades por fecha
        activities_dict = {activity.date: activity for activity in activities}
        
        # Calcular totales
        theoretical_hours = 0
        actual_hours = 0
        vacation_days = 0
        absence_days = 0
        hld_hours = 0
        guard_hours = 0
        training_hours = 0
        other_days = 0
        
        # Iterar por cada día del período
        current_date = start_date
        while current_date <= end_date:
            daily_theoretical = self.get_daily_hours(current_date)
            theoretical_hours += daily_theoretical
            
            if current_date in activities_dict:
                activity = activities_dict[current_date]
                
                if activity.activity_type == 'V':  # Vacaciones
                    vacation_days += 1
                    # No suma horas reales
                elif activity.activity_type == 'A':  # Ausencias
                    absence_days += 1
                    # No suma horas reales
                elif activity.activity_type == 'HLD':  # Horas Libre Disposición
                    hld_hours += activity.hours or 0
                    actual_hours += daily_theoretical - (activity.hours or 0)
                elif activity.activity_type == 'G':  # Guardia
                    guard_hours += activity.hours or 0
                    actual_hours += daily_theoretical + (activity.hours or 0)
                elif activity.activity_type == 'F':  # Formación
                    training_hours += activity.hours or 0
                    actual_hours += daily_theoretical - (activity.hours or 0)
                elif activity.activity_type == 'C':  # Otros
                    other_days += 1
                    # No suma horas reales
                else:
                    # Día normal
                    actual_hours += daily_theoretical
            else:
                # Día normal sin actividades
                if daily_theoretical > 0:  # Solo días laborables
                    actual_hours += daily_theoretical
            
            current_date = date(current_date.year, current_date.month, current_date.day + 1) \
                          if current_date.day < monthrange(current_date.year, current_date.month)[1] \
                          else date(current_date.year + (1 if current_date.month == 12 else 0), 
                                   (current_date.month % 12) + 1, 1)
        
        # Calcular eficiencia
        efficiency = (actual_hours / theoretical_hours * 100) if theoretical_hours > 0 else 0
        
        return {
            'theoretical_hours': theoretical_hours,
            'actual_hours': actual_hours,
            'vacation_days': vacation_days,
            'absence_days': absence_days,
            'hld_hours': hld_hours,
            'guard_hours': guard_hours,
            'training_hours': training_hours,
            'other_days': other_days,
            'efficiency': round(efficiency, 2),
            'period': f"{year}-{month:02d}" if month else str(year)
        }
    
    def get_remaining_benefits(self, year=None):
        """Calcula los beneficios restantes del empleado"""
        if not year:
            year = datetime.now().year
        
        summary = self.get_hours_summary(year)
        
        return {
            'remaining_vacation_days': max(0, self.annual_vacation_days - summary['vacation_days']),
            'remaining_hld_hours': max(0, self.annual_hld_hours - summary['hld_hours']),
            'used_vacation_days': summary['vacation_days'],
            'used_hld_hours': summary['hld_hours']
        }
    
    def get_active_memberships(self):
        """Retorna solo las membresías activas."""
        if not self.memberships:
            return []
        return [membership for membership in self.memberships if membership.active]

    def get_primary_membership(self):
        """Obtiene la membresía primaria (o None)."""
        active_memberships = self.get_active_memberships()
        if not active_memberships:
            return None
        for membership in active_memberships:
            if membership.is_primary:
                return membership
        return active_memberships[0]

    def to_dict(self, include_summary=False, year=None):
        """Convierte el empleado a diccionario para JSON"""
        # Obtener team_name de forma segura sin lazy loading
        team_name = None
        try:
            # Solo acceder a team si ya está cargado en la sesión
            from sqlalchemy import inspect
            if inspect(self).attrs.team.loaded_value is not None:
                team_name = self.team.name
        except:
            # Si falla, obtener directamente desde la BD
            from .team import Team
            team = Team.query.filter_by(id=self.team_id).first()
            team_name = team.name if team else None
        
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'team_id': self.team_id,
            'team_name': team_name,
            'hours_monday_thursday': self.hours_monday_thursday,
            'hours_friday': self.hours_friday,
            'hours_summer': self.hours_summer,
            'has_summer_schedule': self.has_summer_schedule,
            'summer_months': self.summer_months_list,
            'annual_vacation_days': self.annual_vacation_days,
            'annual_hld_hours': self.annual_hld_hours,
            'hourly_rate': self.hourly_rate,  # Tarifa por hora (solo visible para admin)
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'active': self.active,
            'approved': self.approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }

        # Equipos (membresías)
        active_memberships = self.get_active_memberships()
        if active_memberships:
            data['teams'] = [
                {
                    'membership_id': membership.id,
                    'team_id': membership.team_id,
                    'team_name': membership.team.name if membership.team else None,
                    'role': membership.role,
                    'allocation_percent': membership.allocation_percent,
                    'is_primary': membership.is_primary,
                    'active': membership.active,
                    'notes': membership.notes
                } for membership in active_memberships
            ]
        else:
            data['teams'] = []

        # Proyectos asignados
        if self.project_assignments:
            data['projects'] = [
                assignment.to_dict(include_employee=False)
                for assignment in self.project_assignments
                if assignment.active
            ]
        else:
            data['projects'] = []
        
        if include_summary:
            data['hours_summary'] = self.get_hours_summary(year)
            data['remaining_benefits'] = self.get_remaining_benefits(year)
        
        return data
    
    def __str__(self):
        return self.full_name
    
    def __repr__(self):
        return f'<Employee {self.full_name}>'
