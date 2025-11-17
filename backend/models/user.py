from flask_security import UserMixin, RoleMixin
from datetime import datetime
import uuid
from sqlalchemy import Boolean, DateTime, Column, Integer, String, Text, ForeignKey
from .base import db

# Tabla de asociación para roles de usuario (many-to-many)
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    """Modelo para roles de usuario"""
    __tablename__ = 'role'
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model, UserMixin):
    """Modelo para usuarios del sistema"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Campos requeridos por Flask-Security
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    
    # Información adicional del usuario
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Campos de seguimiento
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.fs_uniquifier:
            self.fs_uniquifier = uuid.uuid4().hex
    
    # Relaciones
    roles = db.relationship('Role', secondary=roles_users,
                           backref=db.backref('users', lazy='dynamic'))
    
    # Relación con empleado (one-to-one) - referencia tardía
    employee = db.relationship('Employee', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Relación con notificaciones (especificar foreign_keys para evitar ambigüedad)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', 
                                   cascade='all, delete-orphan',
                                   foreign_keys='Notification.user_id')
    
    @property
    def full_name(self):
        """Retorna el nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def has_role(self, role_name):
        """Verifica si el usuario tiene un rol específico"""
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.has_role('admin')
    
    def is_manager(self):
        """Verifica si el usuario es manager"""
        return self.has_role('manager')
    
    def is_employee(self):
        """Verifica si el usuario es empleado"""
        return self.has_role('employee')
    
    def is_viewer(self):
        """Verifica si el usuario es solo viewer"""
        return self.has_role('viewer')
    
    def get_primary_role(self):
        """Retorna el rol primario del usuario (el más importante según jerarquía)"""
        if not self.roles:
            return None
        
        # Jerarquía de roles: admin > manager > employee > viewer
        role_hierarchy = ['admin', 'manager', 'employee', 'viewer']
        role_names = [role.name for role in self.roles]
        
        # Retornar el rol más importante que tenga el usuario
        for role_name in role_hierarchy:
            if role_name in role_names:
                return role_name
        
        # Si no coincide con ninguno, retornar el primero
        return role_names[0] if role_names else None
    
    def get_managed_teams(self):
        """Retorna los equipos que gestiona este usuario (si es manager)"""
        if not self.is_manager() or not self.employee:
            return []
        
        from .team import Team
        return Team.query.filter_by(manager_id=self.employee.id).all()
    
    def can_manage_employee(self, employee):
        """Verifica si puede gestionar a un empleado específico"""
        if self.is_admin():
            return True
        
        if self.is_manager() and self.employee:
            managed_teams = self.get_managed_teams()
            return any(team.id == employee.team_id for team in managed_teams)
        
        return False
    
    def to_dict(self):
        """Convierte el usuario a diccionario para JSON"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'active': self.active,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'roles': [role.name for role in self.roles],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'login_count': self.login_count or 0
        }
    
    def __str__(self):
        return self.email
    
    def __repr__(self):
        return f'<User {self.email}>'
