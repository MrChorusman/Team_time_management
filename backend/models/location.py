from datetime import datetime
from .base import db

class Country(db.Model):
    """Modelo para países"""
    __tablename__ = 'countries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), nullable=False, unique=True)  # ISO 3166-1
    is_active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    autonomous_communities = db.relationship('AutonomousCommunity', backref='country', lazy='dynamic')
    
    def to_dict(self):
        """Convierte el país a diccionario para JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Country {self.name} ({self.code})>'


class AutonomousCommunity(db.Model):
    """Modelo para comunidades autónomas / estados / regiones"""
    __tablename__ = 'autonomous_communities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    
    # Relaciones
    provinces = db.relationship('Province', backref='autonomous_community', lazy='dynamic')
    cities = db.relationship('City', backref='autonomous_community', lazy='dynamic')
    
    def to_dict(self):
        """Convierte la comunidad autónoma a diccionario para JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'country_id': self.country_id,
            'country_name': self.country.name if self.country else None,
            'country_code': self.country.code if self.country else None
        }
    
    def __repr__(self):
        return f'<AutonomousCommunity {self.name}>'


class Province(db.Model):
    """Modelo para provincias"""
    __tablename__ = 'provinces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    autonomous_community_id = db.Column(db.Integer, db.ForeignKey('autonomous_communities.id'))
    
    def to_dict(self):
        """Convierte la provincia a diccionario para JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'autonomous_community_id': self.autonomous_community_id,
            'autonomous_community_name': self.autonomous_community.name if self.autonomous_community else None
        }
    
    def __repr__(self):
        return f'<Province {self.name}>'


class City(db.Model):
    """Modelo para ciudades"""
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    autonomous_community_id = db.Column(db.Integer, db.ForeignKey('autonomous_communities.id'))
    postal_code = db.Column(db.String(10))
    
    def to_dict(self):
        """Convierte la ciudad a diccionario para JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'autonomous_community_id': self.autonomous_community_id,
            'autonomous_community_name': self.autonomous_community.name if self.autonomous_community else None,
            'postal_code': self.postal_code
        }
    
    def __repr__(self):
        return f'<City {self.name}>'

