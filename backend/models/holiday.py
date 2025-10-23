from datetime import datetime, date
from .base import db

class Holiday(db.Model):
    """Modelo para festivos globales"""
    __tablename__ = 'holiday'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Información del festivo
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Ubicación geográfica (jerarquía global)
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=True)  # Estado/Provincia/Comunidad
    city = db.Column(db.String(100), nullable=True)
    
    # Tipo de festivo
    holiday_type = db.Column(db.String(50), default='national')  # national, regional, local
    
    # Información adicional
    description = db.Column(db.Text)
    is_fixed = db.Column(db.Boolean, default=True)  # Si es fecha fija cada año
    
    # Metadatos de la fuente
    source = db.Column(db.String(100))  # API source (nager.date, etc.)
    source_id = db.Column(db.String(100))  # ID en la fuente externa
    
    # Estado
    active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices para optimizar consultas
    __table_args__ = (
        db.Index('idx_holiday_date_country', 'date', 'country'),
        db.Index('idx_holiday_country_region', 'country', 'region'),
        db.Index('idx_holiday_location', 'country', 'region', 'city'),
    )
    
    @classmethod
    def get_holidays_for_location(cls, country, region=None, city=None, year=None):
        """Obtiene todos los festivos para una ubicación específica"""
        query = cls.query.filter(
            cls.country == country,
            cls.active == True
        )
        
        # Filtrar por año si se especifica
        if year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            query = query.filter(cls.date >= start_date, cls.date <= end_date)
        
        # Incluir festivos nacionales, regionales y locales
        location_filter = db.or_(
            cls.region.is_(None),  # Festivos nacionales
            cls.region == region if region else False,  # Festivos regionales
            db.and_(cls.region == region, cls.city == city) if city else False  # Festivos locales
        )
        
        query = query.filter(location_filter)
        
        return query.order_by(cls.date).all()
    
    @classmethod
    def get_holidays_for_date(cls, target_date, country, region=None, city=None):
        """Verifica si una fecha específica es festivo en una ubicación"""
        return cls.query.filter(
            cls.date == target_date,
            cls.country == country,
            cls.active == True,
            db.or_(
                cls.region.is_(None),  # Festivos nacionales
                cls.region == region if region else False,  # Festivos regionales
                db.and_(cls.region == region, cls.city == city) if city else False  # Festivos locales
            )
        ).all()
    
    @classmethod
    def get_countries_with_holidays(cls):
        """Obtiene lista de países con festivos cargados"""
        return db.session.query(cls.country).distinct().order_by(cls.country).all()
    
    @classmethod
    def get_regions_for_country(cls, country):
        """Obtiene lista de regiones para un país"""
        return db.session.query(cls.region).filter(
            cls.country == country,
            cls.region.isnot(None)
        ).distinct().order_by(cls.region).all()
    
    @classmethod
    def get_cities_for_region(cls, country, region):
        """Obtiene lista de ciudades para una región"""
        return db.session.query(cls.city).filter(
            cls.country == country,
            cls.region == region,
            cls.city.isnot(None)
        ).distinct().order_by(cls.city).all()
    
    @classmethod
    def bulk_create_holidays(cls, holidays_data):
        """Crea múltiples festivos de forma eficiente"""
        holidays_to_create = []
        
        for holiday_data in holidays_data:
            # Verificar si ya existe
            existing = cls.query.filter(
                cls.date == holiday_data['date'],
                cls.country == holiday_data['country'],
                cls.region == holiday_data.get('region'),
                cls.city == holiday_data.get('city'),
                cls.name == holiday_data['name']
            ).first()
            
            if not existing:
                holiday = cls(**holiday_data)
                holidays_to_create.append(holiday)
        
        if holidays_to_create:
            db.session.bulk_save_objects(holidays_to_create)
            db.session.commit()
        
        return len(holidays_to_create)
    
    def get_hierarchy_level(self):
        """Determina el nivel jerárquico del festivo"""
        if self.city:
            return 'local'
        elif self.region:
            return 'regional'
        else:
            return 'national'
    
    def get_location_string(self):
        """Retorna una cadena descriptiva de la ubicación"""
        parts = [self.country]
        if self.region:
            parts.append(self.region)
        if self.city:
            parts.append(self.city)
        return ' > '.join(parts)
    
    def is_applicable_for_employee(self, employee):
        """Verifica si este festivo aplica para un empleado específico"""
        if self.country != employee.country:
            return False
        
        # Festivo nacional - aplica para todos
        if not self.region:
            return True
        
        # Festivo regional - debe coincidir la región
        if self.region == employee.region:
            # Si no hay ciudad específica, aplica para toda la región
            if not self.city:
                return True
            # Si hay ciudad específica, debe coincidir
            return self.city == employee.city
        
        return False
    
    def to_dict(self):
        """Convierte el festivo a diccionario para JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'holiday_type': self.holiday_type,
            'hierarchy_level': self.get_hierarchy_level(),
            'location_string': self.get_location_string(),
            'description': self.description,
            'is_fixed': self.is_fixed,
            'source': self.source,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __str__(self):
        return f"{self.name} ({self.date}) - {self.get_location_string()}"
    
    def __repr__(self):
        return f'<Holiday {self.name} {self.date} {self.country}>'
