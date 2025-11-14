from datetime import datetime
from .base import db

class Company(db.Model):
    """Modelo para empresas/clientes con períodos de facturación personalizados"""
    __tablename__ = 'company'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    
    # Período de facturación (días del mes)
    # Ejemplo: billing_period_start_day=26, billing_period_end_day=25 significa del 26 al 25 del mes siguiente
    billing_period_start_day = db.Column(db.Integer, nullable=False)  # 1-31
    billing_period_end_day = db.Column(db.Integer, nullable=False)   # 1-31
    
    # Estado
    active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_billing_period_dates(self, year: int, month: int):
        """
        Calcula las fechas de inicio y fin del período de facturación para un mes/año dado.
        
        Ejemplo:
        - billing_period_start_day=26, billing_period_end_day=25, month=1, year=2025
        - Retorna: (2024-12-26, 2025-01-25)
        
        Ejemplo 2:
        - billing_period_start_day=1, billing_period_end_day=31, month=1, year=2025
        - Retorna: (2025-01-01, 2025-01-31)
        """
        from datetime import date
        from calendar import monthrange
        
        # Si el día de inicio es mayor que el día de fin, significa que cruza meses
        # Ejemplo: start_day=26, end_day=25 significa del 26 del mes anterior al 25 del mes actual
        if self.billing_period_start_day > self.billing_period_end_day:
            # La fecha de inicio es del mes anterior
            if month == 1:
                start_month = 12
                start_year = year - 1
            else:
                start_month = month - 1
                start_year = year
            
            # Calcular fecha de inicio (del mes anterior)
            _, last_day_start = monthrange(start_year, start_month)
            start_day = min(self.billing_period_start_day, last_day_start)
            start_date = date(start_year, start_month, start_day)
            
            # La fecha de fin es del mes actual
            _, last_day_end = monthrange(year, month)
            end_day = min(self.billing_period_end_day, last_day_end)
            end_date = date(year, month, end_day)
        else:
            # Período normal dentro del mismo mes
            _, last_day = monthrange(year, month)
            
            # Calcular fecha de inicio
            start_day = min(self.billing_period_start_day, last_day)
            start_date = date(year, month, start_day)
            
            # Calcular fecha de fin
            end_day = min(self.billing_period_end_day, last_day)
            end_date = date(year, month, end_day)
        
        return start_date, end_date
    
    def to_dict(self):
        """Convierte la empresa a diccionario para JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'billing_period_start_day': self.billing_period_start_day,
            'billing_period_end_day': self.billing_period_end_day,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'<Company {self.name}>'

