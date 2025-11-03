from datetime import datetime
from enum import Enum
from .base import db

class NotificationType(Enum):
    """Tipos de notificación"""
    EMPLOYEE_REGISTRATION = 'employee_registration'
    EMPLOYEE_APPROVED = 'employee_approved'
    VACATION_CONFLICT = 'vacation_conflict'
    CALENDAR_CHANGE = 'calendar_change'
    WEEKLY_REPORT = 'weekly_report'
    SYSTEM_ALERT = 'system_alert'

class NotificationPriority(Enum):
    """Prioridades de notificación"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'

class Notification(db.Model):
    """Modelo para notificaciones del sistema"""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Destinatario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Contenido de la notificación
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Enum(NotificationType), nullable=False)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    
    # Estado de la notificación
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Datos adicionales (JSON)
    data = db.Column(db.JSON)
    
    # Configuración de envío
    send_email = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Metadatos
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Índices para optimizar consultas
    __table_args__ = (
        db.Index('idx_notification_user_read', 'user_id', 'read'),
        db.Index('idx_notification_type_created', 'notification_type', 'created_at'),
    )
    
    @classmethod
    def create_employee_registration_notification(cls, manager_user, employee, created_by_user):
        """Crea notificación para registro de nuevo empleado"""
        notification = cls(
            user_id=manager_user.id,
            title="Nueva solicitud de empleado",
            message=f"{employee.full_name} ha solicitado unirse al equipo {employee.team.name}. Revisa y aprueba su solicitud.",
            notification_type=NotificationType.EMPLOYEE_REGISTRATION,
            priority=NotificationPriority.HIGH,
            send_email=True,
            created_by=created_by_user.id,
            data={
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'team_id': employee.team_id,
                'team_name': employee.team.name,
                'action_url': f'/admin/employees/{employee.id}/approve'
            }
        )
        
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_employee_approved_notification(cls, employee_user, approved_by_user):
        """Crea notificación para empleado aprobado"""
        notification = cls(
            user_id=employee_user.id,
            title="¡Cuenta aprobada!",
            message=f"Tu solicitud ha sido aprobada. Ya puedes acceder a todas las funcionalidades de la aplicación.",
            notification_type=NotificationType.EMPLOYEE_APPROVED,
            priority=NotificationPriority.HIGH,
            send_email=True,
            created_by=approved_by_user.id,
            data={
                'approved_by': approved_by_user.full_name,
                'action_url': '/dashboard'
            }
        )
        
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_vacation_conflict_notification(cls, manager_user, conflicts_data):
        """Crea notificación para conflictos de vacaciones"""
        conflict_date = conflicts_data['date']
        employees = conflicts_data['employees']
        
        employee_names = [emp['name'] for emp in employees]
        
        notification = cls(
            user_id=manager_user.id,
            title="Conflicto de vacaciones detectado",
            message=f"Múltiples empleados han solicitado vacaciones para el {conflict_date}: {', '.join(employee_names)}",
            notification_type=NotificationType.VACATION_CONFLICT,
            priority=NotificationPriority.MEDIUM,
            send_email=True,
            data={
                'conflict_date': conflict_date,
                'employees': employees,
                'team_id': conflicts_data.get('team_id'),
                'action_url': f'/calendar?date={conflict_date}'
            }
        )
        
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_calendar_change_notification(cls, manager_user, employee, changes_summary):
        """Crea notificación para cambios en el calendario"""
        notification = cls(
            user_id=manager_user.id,
            title="Cambios en calendario de empleado",
            message=f"{employee.full_name} ha realizado cambios en su calendario. {changes_summary}",
            notification_type=NotificationType.CALENDAR_CHANGE,
            priority=NotificationPriority.LOW,
            send_email=True,
            data={
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'changes': changes_summary,
                'action_url': f'/calendar?employee={employee.id}'
            }
        )
        
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_weekly_report_notification(cls, manager_user, team, upcoming_vacations):
        """Crea notificación para reporte semanal"""
        vacation_count = len(upcoming_vacations)
        
        if vacation_count == 0:
            message = f"No hay vacaciones programadas para tu equipo {team.name} en los próximos 10 días."
        else:
            message = f"Tu equipo {team.name} tiene {vacation_count} vacaciones programadas en los próximos 10 días."
        
        notification = cls(
            user_id=manager_user.id,
            title="Reporte semanal de vacaciones",
            message=message,
            notification_type=NotificationType.WEEKLY_REPORT,
            priority=NotificationPriority.LOW,
            send_email=True,
            data={
                'team_id': team.id,
                'team_name': team.name,
                'vacation_count': vacation_count,
                'upcoming_vacations': upcoming_vacations,
                'action_url': f'/reports/team/{team.id}'
            }
        )
        
        db.session.add(notification)
        return notification
    
    @classmethod
    def get_unread_for_user(cls, user_id, limit=50):
        """Obtiene notificaciones no leídas para un usuario"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.read == False
        ).order_by(
            cls.priority.desc(),
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_recent_for_user(cls, user_id, days=7, limit=50):
        """Obtiene notificaciones recientes para un usuario"""
        from datetime import timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        return cls.query.filter(
            cls.user_id == user_id,
            cls.created_at >= since_date
        ).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def mark_as_read(cls, notification_ids, user_id):
        """Marca notificaciones como leídas"""
        cls.query.filter(
            cls.id.in_(notification_ids),
            cls.user_id == user_id
        ).update({
            'read': True,
            'read_at': datetime.utcnow()
        }, synchronize_session=False)
        
        db.session.commit()
    
    @classmethod
    def get_pending_emails(cls, limit=100):
        """Obtiene notificaciones pendientes de envío por email"""
        return cls.query.filter(
            cls.send_email == True,
            cls.email_sent == False
        ).order_by(
            cls.priority.desc(),
            cls.created_at.asc()
        ).limit(limit).all()
    
    def mark_email_sent(self):
        """Marca la notificación como enviada por email"""
        self.email_sent = True
        self.email_sent_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_read_single(self):
        """Marca esta notificación como leída"""
        self.read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    def is_expired(self):
        """Verifica si la notificación ha expirado"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_priority_color(self):
        """Obtiene el color asociado a la prioridad"""
        colors = {
            NotificationPriority.LOW: '#28a745',      # Verde
            NotificationPriority.MEDIUM: '#ffc107',   # Amarillo
            NotificationPriority.HIGH: '#fd7e14',     # Naranja
            NotificationPriority.URGENT: '#dc3545'    # Rojo
        }
        return colors.get(self.priority, '#6c757d')
    
    def get_type_icon(self):
        """Obtiene el icono asociado al tipo de notificación"""
        icons = {
            NotificationType.EMPLOYEE_REGISTRATION: 'user-plus',
            NotificationType.EMPLOYEE_APPROVED: 'check-circle',
            NotificationType.VACATION_CONFLICT: 'alert-triangle',
            NotificationType.CALENDAR_CHANGE: 'calendar',
            NotificationType.WEEKLY_REPORT: 'file-text',
            NotificationType.SYSTEM_ALERT: 'bell'
        }
        return icons.get(self.notification_type, 'bell')
    
    def to_dict(self):
        """Convierte la notificación a diccionario para JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'priority': self.priority.value if self.priority else None,
            'priority_color': self.get_priority_color(),
            'type_icon': self.get_type_icon(),
            'data': self.data,
            'read': self.read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'send_email': self.send_email,
            'email_sent': self.email_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }
    
    def __str__(self):
        return f"{self.title} - {self.user.email if self.user else 'Unknown'}"
    
    def __repr__(self):
        return f'<Notification {self.id} {self.notification_type.value if self.notification_type else "Unknown"}>'
