from datetime import datetime
from enum import Enum
from .base import db

class NotificationType(Enum):
    """Tipos de notificación"""
    EMPLOYEE_REGISTRATION = 'employee_registration'
    EMPLOYEE_APPROVED = 'employee_approved'
    EMPLOYEE_CREATED = 'employee_created'
    EMPLOYEE_UPDATED = 'employee_updated'
    EMPLOYEE_DELETED = 'employee_deleted'
    USER_DELETED = 'user_deleted'
    PROJECT_CREATED = 'project_created'
    PROJECT_UPDATED = 'project_updated'
    PROJECT_DELETED = 'project_deleted'
    COMPANY_CREATED = 'company_created'
    COMPANY_UPDATED = 'company_updated'
    COMPANY_DELETED = 'company_deleted'
    INVITATION_SENT = 'invitation_sent'
    PROJECT_ASSIGNMENT = 'project_assignment'
    TEAM_ASSIGNMENT = 'team_assignment'
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
    # Usar VARCHAR en lugar de Enum para evitar problemas con tipos ENUM en PostgreSQL
    _notification_type = db.Column('notification_type', db.String(50), nullable=False)
    _priority = db.Column('priority', db.String(20), default='medium')
    
    @property
    def notification_type(self):
        """Convierte el string almacenado a Enum para uso en código"""
        if self._notification_type:
            try:
                return NotificationType(self._notification_type)
            except ValueError:
                return None
        return None
    
    @notification_type.setter
    def notification_type(self, value):
        """Convierte Enum a string para almacenamiento"""
        if isinstance(value, NotificationType):
            self._notification_type = value.value
        elif isinstance(value, str):
            self._notification_type = value
        else:
            self._notification_type = None
    
    @property
    def priority(self):
        """Convierte el string almacenado a Enum para uso en código"""
        if self._priority:
            try:
                return NotificationPriority(self._priority)
            except ValueError:
                return NotificationPriority.MEDIUM
        return NotificationPriority.MEDIUM
    
    @priority.setter
    def priority(self, value):
        """Convierte Enum a string para almacenamiento"""
        if isinstance(value, NotificationPriority):
            self._priority = value.value
        elif isinstance(value, str):
            self._priority = value
        else:
            self._priority = NotificationPriority.MEDIUM.value
    
    
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
    def create_user_deleted_notification(cls, admin_user, deleted_user_email, deleted_by_user):
        """Crea notificación para eliminación de usuario"""
        notification = cls(
            user_id=admin_user.id,
            title="Usuario eliminado",
            message=f"El usuario {deleted_user_email} ha sido eliminado del sistema por {deleted_by_user.email}.",
            notification_type=NotificationType.USER_DELETED,
            priority=NotificationPriority.MEDIUM,
            send_email=False,
            created_by=deleted_by_user.id,
            data={
                'deleted_user_email': deleted_user_email,
                'deleted_by': deleted_by_user.email,
                'action_url': '/admin/users'
            }
        )
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_project_notification(cls, user, project, action, created_by_user):
        """Crea notificación para creación/actualización/eliminación de proyecto"""
        action_messages = {
            'created': f"Se ha creado el proyecto {project.name} ({project.code}).",
            'updated': f"Se ha actualizado el proyecto {project.name} ({project.code}).",
            'deleted': f"Se ha eliminado el proyecto {project.name} ({project.code})."
        }
        action_types = {
            'created': NotificationType.PROJECT_CREATED,
            'updated': NotificationType.PROJECT_UPDATED,
            'deleted': NotificationType.PROJECT_DELETED
        }
        priorities = {
            'created': NotificationPriority.MEDIUM,
            'updated': NotificationPriority.LOW,
            'deleted': NotificationPriority.HIGH
        }
        
        notification = cls(
            user_id=user.id,
            title=f"Proyecto {action}",
            message=action_messages.get(action, f"Proyecto {project.name} {action}."),
            notification_type=action_types.get(action, NotificationType.PROJECT_CREATED),
            priority=priorities.get(action, NotificationPriority.MEDIUM),
            send_email=action == 'deleted',
            created_by=created_by_user.id if created_by_user else None,
            data={
                'project_id': project.id,
                'project_code': project.code,
                'project_name': project.name,
                'action': action,
                'action_url': f'/projects/{project.id}' if action != 'deleted' else '/projects'
            }
        )
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_company_notification(cls, user, company, action, created_by_user):
        """Crea notificación para creación/actualización/eliminación de empresa"""
        action_messages = {
            'created': f"Se ha creado la empresa {company.name}.",
            'updated': f"Se ha actualizado la empresa {company.name}.",
            'deleted': f"Se ha eliminado la empresa {company.name}."
        }
        action_types = {
            'created': NotificationType.COMPANY_CREATED,
            'updated': NotificationType.COMPANY_UPDATED,
            'deleted': NotificationType.COMPANY_DELETED
        }
        priorities = {
            'created': NotificationPriority.MEDIUM,
            'updated': NotificationPriority.LOW,
            'deleted': NotificationPriority.HIGH
        }
        
        notification = cls(
            user_id=user.id,
            title=f"Empresa {action}",
            message=action_messages.get(action, f"Empresa {company.name} {action}."),
            notification_type=action_types.get(action, NotificationType.COMPANY_CREATED),
            priority=priorities.get(action, NotificationPriority.MEDIUM),
            send_email=action == 'deleted',
            created_by=created_by_user.id if created_by_user else None,
            data={
                'company_id': company.id,
                'company_name': company.name,
                'action': action,
                'action_url': '/admin/companies'
            }
        )
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_employee_notification(cls, user, employee, action, created_by_user):
        """Crea notificación para creación/actualización/eliminación de empleado"""
        action_messages = {
            'created': f"Se ha creado el empleado {employee.full_name}.",
            'updated': f"Se ha actualizado el empleado {employee.full_name}.",
            'deleted': f"Se ha eliminado el empleado {employee.full_name}."
        }
        action_types = {
            'created': NotificationType.EMPLOYEE_CREATED,
            'updated': NotificationType.EMPLOYEE_UPDATED,
            'deleted': NotificationType.EMPLOYEE_DELETED
        }
        priorities = {
            'created': NotificationPriority.MEDIUM,
            'updated': NotificationPriority.LOW,
            'deleted': NotificationPriority.HIGH
        }
        
        notification = cls(
            user_id=user.id,
            title=f"Empleado {action}",
            message=action_messages.get(action, f"Empleado {employee.full_name} {action}."),
            notification_type=action_types.get(action, NotificationType.EMPLOYEE_CREATED),
            priority=priorities.get(action, NotificationPriority.MEDIUM),
            send_email=action == 'deleted',
            created_by=created_by_user.id if created_by_user else None,
            data={
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'action': action,
                'action_url': f'/employees/{employee.id}' if action != 'deleted' else '/employees'
            }
        )
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_invitation_sent_notification(cls, admin_user, invitee_email, created_by_user):
        """Crea notificación para envío de invitación"""
        notification = cls(
            user_id=admin_user.id,
            title="Invitación enviada",
            message=f"Se ha enviado una invitación a {invitee_email} para unirse al sistema.",
            notification_type=NotificationType.INVITATION_SENT,
            priority=NotificationPriority.LOW,
            send_email=False,
            created_by=created_by_user.id if created_by_user else None,
            data={
                'invitee_email': invitee_email,
                'action_url': '/admin/users'
            }
        )
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_project_assignment_notification(cls, employee_user, project, created_by_user):
        """Crea notificación para asignación de empleado a proyecto"""
        notification = cls(
            user_id=employee_user.id,
            title="Asignado a proyecto",
            message=f"Has sido asignado al proyecto {project.name} ({project.code}).",
            notification_type=NotificationType.PROJECT_ASSIGNMENT,
            priority=NotificationPriority.MEDIUM,
            send_email=True,
            created_by=created_by_user.id if created_by_user else None,
            data={
                'project_id': project.id,
                'project_code': project.code,
                'project_name': project.name,
                'action_url': f'/projects/{project.id}'
            }
        )
        db.session.add(notification)
        return notification
    
    @classmethod
    def create_team_assignment_notification(cls, employee_user, team, created_by_user):
        """Crea notificación para asignación de empleado a equipo"""
        notification = cls(
            user_id=employee_user.id,
            title="Asignado a equipo",
            message=f"Has sido asignado al equipo {team.name}.",
            notification_type=NotificationType.TEAM_ASSIGNMENT,
            priority=NotificationPriority.MEDIUM,
            send_email=True,
            created_by=created_by_user.id if created_by_user else None,
            data={
                'team_id': team.id,
                'team_name': team.name,
                'action_url': f'/teams/{team.id}'
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
            cls._priority.desc(),
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
        # Manejar tanto Enum como string para compatibilidad
        priority_value = self.priority.value if isinstance(self.priority, NotificationPriority) else self._priority
        colors = {
            'low': '#28a745',      # Verde
            'medium': '#ffc107',   # Amarillo
            'high': '#fd7e14',     # Naranja
            'urgent': '#dc3545'    # Rojo
        }
        return colors.get(priority_value, '#6c757d')
    
    def get_type_icon(self):
        """Obtiene el icono asociado al tipo de notificación"""
        # Manejar tanto Enum como string para compatibilidad
        type_value = self.notification_type.value if isinstance(self.notification_type, NotificationType) else self._notification_type
        icons = {
            'employee_registration': 'user-plus',
            'employee_approved': 'check-circle',
            'employee_created': 'user-plus',
            'employee_updated': 'user-edit',
            'employee_deleted': 'user-minus',
            'user_deleted': 'user-x',
            'project_created': 'folder-plus',
            'project_updated': 'folder-edit',
            'project_deleted': 'folder-minus',
            'company_created': 'building-plus',
            'company_updated': 'building-edit',
            'company_deleted': 'building-minus',
            'invitation_sent': 'mail',
            'project_assignment': 'briefcase',
            'team_assignment': 'users',
            'vacation_conflict': 'alert-triangle',
            'calendar_change': 'calendar',
            'weekly_report': 'file-text',
            'system_alert': 'bell'
        }
        return icons.get(type_value, 'bell')
    
    def to_dict(self):
        """Convierte la notificación a diccionario para JSON"""
        # Obtener valores como strings para JSON
        type_value = self.notification_type.value if isinstance(self.notification_type, NotificationType) else self._notification_type
        priority_value = self.priority.value if isinstance(self.priority, NotificationPriority) else self._priority
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': type_value,
            'priority': priority_value,
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
        type_value = self.notification_type.value if isinstance(self.notification_type, NotificationType) else self._notification_type
        return f'<Notification {self.id} {type_value or "Unknown"}>'
