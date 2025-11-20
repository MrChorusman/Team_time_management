from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import logging
from flask import current_app

from models.notification import Notification, NotificationType, NotificationPriority
from models.user import User, db
from models.employee import Employee
from models.team import Team
from models.calendar_activity import CalendarActivity

logger = logging.getLogger(__name__)

class NotificationService:
    """Servicio para gestión avanzada de notificaciones"""
    
    @staticmethod
    def notify_employee_registration(employee: Employee, created_by_user: User) -> Optional[Notification]:
        """Notifica a los managers sobre nuevo registro de empleado"""
        try:
            # Encontrar el manager del equipo
            team = employee.team
            if not team or not team.manager:
                logger.warning(f"Equipo {team.name if team else 'Unknown'} no tiene manager asignado")
                return None
            
            manager_user = team.manager.user
            if not manager_user:
                logger.warning(f"Manager del equipo {team.name} no tiene usuario asociado")
                return None
            
            # Crear notificación
            notification = Notification.create_employee_registration_notification(
                manager_user, employee, created_by_user
            )
            
            db.session.commit()
            logger.info(f"Notificación de registro enviada al manager {manager_user.email}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error enviando notificación de registro: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def notify_employee_approved(employee: Employee, approved_by_user: User) -> Optional[Notification]:
        """Notifica al empleado que su cuenta ha sido aprobada y envía email"""
        try:
            employee_user = employee.user
            if not employee_user:
                logger.warning(f"Empleado {employee.full_name} no tiene usuario asociado")
                return None
            
            # Crear notificación
            notification = Notification.create_employee_approved_notification(
                employee_user, approved_by_user
            )
            
            db.session.commit()
            logger.info(f"Notificación de aprobación creada para {employee_user.email}")
            
            # Enviar email inmediatamente si está configurado
            if notification.send_email:
                try:
                    from flask import current_app
                    from .email_service import email_service
                    
                    # Asegurar que el servicio está inicializado
                    if not email_service.mail:
                        email_service.init_app(current_app)
                    
                    success = email_service.send_notification_email(notification)
                    if success:
                        notification.mark_email_sent()
                        logger.info(f"Email de aprobación enviado a {employee_user.email}")
                    else:
                        logger.warning(f"No se pudo enviar email de aprobación a {employee_user.email}")
                except Exception as email_error:
                    logger.error(f"Error enviando email de aprobación: {email_error}")
                    # No fallar si el email no se puede enviar, la notificación ya está creada
            
            return notification
            
        except Exception as e:
            logger.error(f"Error enviando notificación de aprobación: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def check_and_notify_vacation_conflicts(team_id: int, target_date: date, exclude_employee_id: int = None) -> List[Notification]:
        """Verifica y notifica conflictos de vacaciones"""
        try:
            # Obtener conflictos de vacaciones
            conflicts_count, conflicts = CalendarActivity.check_vacation_conflicts(
                team_id, target_date, exclude_employee_id
            )
            
            if conflicts_count < 2:  # No hay conflicto si hay menos de 2 personas
                return []
            
            # Obtener el equipo y su manager
            team = Team.query.get(team_id)
            if not team or not team.manager or not team.manager.user:
                logger.warning(f"Equipo {team_id} no tiene manager para notificar conflictos")
                return []
            
            # Preparar datos del conflicto
            conflicts_data = {
                'date': target_date.isoformat(),
                'team_id': team_id,
                'employees': [
                    {
                        'id': conflict.employee_id,
                        'name': conflict.employee.full_name
                    }
                    for conflict in conflicts
                ]
            }
            
            # Crear notificación
            notification = Notification.create_vacation_conflict_notification(
                team.manager.user, conflicts_data
            )
            
            db.session.commit()
            logger.info(f"Notificación de conflicto de vacaciones enviada para {target_date}")
            
            return [notification]
            
        except Exception as e:
            logger.error(f"Error verificando conflictos de vacaciones: {e}")
            db.session.rollback()
            return []
    
    @staticmethod
    def notify_calendar_changes(employee: Employee, changes_summary: str) -> Optional[Notification]:
        """Notifica al manager sobre cambios en el calendario de un empleado"""
        try:
            team = employee.team
            if not team or not team.manager or not team.manager.user:
                logger.warning(f"Empleado {employee.full_name} no tiene manager para notificar cambios")
                return None
            
            # Crear notificación
            notification = Notification.create_calendar_change_notification(
                team.manager.user, employee, changes_summary
            )
            
            db.session.commit()
            logger.info(f"Notificación de cambios de calendario enviada para {employee.full_name}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error enviando notificación de cambios: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def send_weekly_vacation_reports() -> List[Notification]:
        """Envía reportes semanales de vacaciones a todos los managers"""
        notifications = []
        
        try:
            # Obtener todos los equipos con manager
            teams = Team.query.filter(
                Team.active == True,
                Team.manager_id.isnot(None)
            ).all()
            
            # Calcular fechas (próximos 10 días)
            start_date = date.today()
            end_date = start_date + timedelta(days=10)
            
            for team in teams:
                if not team.manager or not team.manager.user:
                    continue
                
                # Obtener vacaciones próximas del equipo
                upcoming_vacations = CalendarActivity.query.join(Employee).filter(
                    Employee.team_id == team.id,
                    CalendarActivity.date >= start_date,
                    CalendarActivity.date <= end_date,
                    CalendarActivity.activity_type == 'V'
                ).order_by(CalendarActivity.date).all()
                
                # Preparar datos de vacaciones
                vacation_data = []
                for vacation in upcoming_vacations:
                    vacation_data.append({
                        'employee_name': vacation.employee.full_name,
                        'date': vacation.date.isoformat(),
                        'date_formatted': vacation.date.strftime('%d/%m/%Y')
                    })
                
                # Crear notificación
                notification = Notification.create_weekly_report_notification(
                    team.manager.user, team, vacation_data
                )
                
                notifications.append(notification)
            
            db.session.commit()
            logger.info(f"Enviados {len(notifications)} reportes semanales de vacaciones")
            
        except Exception as e:
            logger.error(f"Error enviando reportes semanales: {e}")
            db.session.rollback()
        
        return notifications
    
    @staticmethod
    def create_system_notification(user_id: int, title: str, message: str, 
                                 priority: NotificationPriority = NotificationPriority.MEDIUM,
                                 send_email: bool = False, data: Dict = None) -> Optional[Notification]:
        """Crea una notificación del sistema personalizada"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=NotificationType.SYSTEM_ALERT,
                priority=priority,
                send_email=send_email,
                data=data or {}
            )
            
            db.session.add(notification)
            db.session.commit()
            
            logger.info(f"Notificación del sistema creada para usuario {user_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creando notificación del sistema: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        """Obtiene notificaciones de un usuario"""
        query = Notification.query.filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        return query.order_by(
            Notification.priority.desc(),
            Notification.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def mark_notifications_as_read(notification_ids: List[int], user_id: int) -> int:
        """Marca notificaciones como leídas"""
        try:
            updated = Notification.query.filter(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
                Notification.read == False
            ).update({
                'read': True,
                'read_at': datetime.utcnow()
            }, synchronize_session=False)
            
            db.session.commit()
            logger.info(f"Marcadas {updated} notificaciones como leídas para usuario {user_id}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Error marcando notificaciones como leídas: {e}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def get_notification_summary(user_id: int) -> Dict:
        """Obtiene resumen de notificaciones para un usuario"""
        try:
            unread_count = Notification.query.filter(
                Notification.user_id == user_id,
                Notification.read == False
            ).count()
            
            # Contar por prioridad
            priority_counts = db.session.query(
                Notification.priority,
                db.func.count(Notification.id).label('count')
            ).filter(
                Notification.user_id == user_id,
                Notification.read == False
            ).group_by(Notification.priority).all()
            
            priority_summary = {
                'urgent': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            for priority, count in priority_counts:
                if priority:
                    priority_summary[priority.value] = count
            
            # Obtener notificaciones recientes
            recent_notifications = NotificationService.get_user_notifications(
                user_id, unread_only=True, limit=5
            )
            
            return {
                'unread_count': unread_count,
                'priority_counts': priority_summary,
                'recent_notifications': [notif.to_dict() for notif in recent_notifications],
                'has_urgent': priority_summary['urgent'] > 0,
                'has_high': priority_summary['high'] > 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de notificaciones: {e}")
            return {
                'unread_count': 0,
                'priority_counts': {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0},
                'recent_notifications': [],
                'has_urgent': False,
                'has_high': False
            }
    
    @staticmethod
    def cleanup_old_notifications(days_old: int = 30) -> int:
        """Limpia notificaciones antiguas leídas"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            deleted = Notification.query.filter(
                Notification.read == True,
                Notification.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            logger.info(f"Eliminadas {deleted} notificaciones antiguas")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error limpiando notificaciones antiguas: {e}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def get_pending_email_notifications(limit: int = 100) -> List[Notification]:
        """Obtiene notificaciones pendientes de envío por email"""
        return Notification.get_pending_emails(limit)
    
    @staticmethod
    def process_notification_queue() -> Dict:
        """Procesa la cola de notificaciones pendientes"""
        from .email_service import EmailService
        
        results = {
            'processed': 0,
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Obtener notificaciones pendientes
            pending_notifications = NotificationService.get_pending_email_notifications()
            results['processed'] = len(pending_notifications)
            
            email_service = EmailService()
            
            for notification in pending_notifications:
                try:
                    # Enviar email
                    success = email_service.send_notification_email(notification)
                    
                    if success:
                        notification.mark_email_sent()
                        results['sent'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Error enviando email para notificación {notification.id}")
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error procesando notificación {notification.id}: {e}")
                    logger.error(f"Error procesando notificación {notification.id}: {e}")
            
            logger.info(f"Procesadas {results['processed']} notificaciones: {results['sent']} enviadas, {results['failed']} fallidas")
            
        except Exception as e:
            logger.error(f"Error procesando cola de notificaciones: {e}")
            results['errors'].append(f"Error general: {e}")
        
        return results
    
    @staticmethod
    def notify_user_deleted(deleted_user_email: str, deleted_by_user: User) -> Optional[Notification]:
        """Notifica a todos los administradores sobre eliminación de usuario"""
        try:
            admins = User.query.join(User.roles).filter(
                User.active == True
            ).all()
            
            # Filtrar solo admins
            admin_users = [u for u in admins if u.is_admin()]
            
            notifications = []
            for admin in admin_users:
                notification = Notification.create_user_deleted_notification(
                    admin, deleted_user_email, deleted_by_user
                )
                notifications.append(notification)
            
            db.session.commit()
            logger.info(f"Notificaciones de eliminación de usuario enviadas a {len(notifications)} administradores")
            return notifications[0] if notifications else None
            
        except Exception as e:
            logger.error(f"Error enviando notificación de eliminación de usuario: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def notify_project_action(project, action: str, created_by_user: User, notify_users: List[User] = None) -> List[Notification]:
        """Notifica sobre acciones de proyecto (crear/actualizar/eliminar)"""
        try:
            notifications = []
            
            # Si no se especifican usuarios, notificar a todos los admins y managers
            if not notify_users:
                from models.team import Team
                users = User.query.filter(User.active == True).all()
                notify_users = [u for u in users if u.is_admin() or u.is_manager()]
            
            for user in notify_users:
                notification = Notification.create_project_notification(
                    user, project, action, created_by_user
                )
                notifications.append(notification)
            
            db.session.commit()
            logger.info(f"Notificaciones de proyecto {action} enviadas a {len(notifications)} usuarios")
            return notifications
            
        except Exception as e:
            logger.error(f"Error enviando notificaciones de proyecto: {e}")
            db.session.rollback()
            return []
    
    @staticmethod
    def notify_company_action(company, action: str, created_by_user: User) -> List[Notification]:
        """Notifica sobre acciones de empresa (crear/actualizar/eliminar)"""
        try:
            # Notificar a todos los admins
            admins = User.query.filter(User.active == True).all()
            admin_users = [u for u in admins if u.is_admin()]
            
            notifications = []
            for admin in admin_users:
                notification = Notification.create_company_notification(
                    admin, company, action, created_by_user
                )
                notifications.append(notification)
            
            db.session.commit()
            logger.info(f"Notificaciones de empresa {action} enviadas a {len(notifications)} administradores")
            return notifications
            
        except Exception as e:
            logger.error(f"Error enviando notificaciones de empresa: {e}")
            db.session.rollback()
            return []
    
    @staticmethod
    def notify_employee_action(employee: Employee, action: str, created_by_user: User) -> Optional[Notification]:
        """Notifica sobre acciones de empleado (crear/actualizar/eliminar)"""
        try:
            # Notificar al manager del equipo si existe
            team = employee.team
            if team and team.manager and team.manager.user:
                notification = Notification.create_employee_notification(
                    team.manager.user, employee, action, created_by_user
                )
                db.session.commit()
                logger.info(f"Notificación de empleado {action} enviada al manager")
                return notification
            
            # Si no hay manager, notificar a admins
            admins = User.query.filter(User.active == True).all()
            admin_users = [u for u in admins if u.is_admin()]
            
            if admin_users:
                notification = Notification.create_employee_notification(
                    admin_users[0], employee, action, created_by_user
                )
                db.session.commit()
                logger.info(f"Notificación de empleado {action} enviada a admin")
                return notification
            
            return None
            
        except Exception as e:
            logger.error(f"Error enviando notificación de empleado: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def notify_invitation_sent(invitee_email: str, created_by_user: User) -> Optional[Notification]:
        """Notifica sobre envío de invitación"""
        try:
            # Notificar al usuario que envió la invitación (si es admin)
            if created_by_user.is_admin():
                notification = Notification.create_invitation_sent_notification(
                    created_by_user, invitee_email, created_by_user
                )
                db.session.commit()
                logger.info(f"Notificación de invitación enviada registrada")
                return notification
            
            return None
            
        except Exception as e:
            logger.error(f"Error enviando notificación de invitación: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def notify_project_assignment(employee: Employee, project, created_by_user: User) -> Optional[Notification]:
        """Notifica a un empleado sobre su asignación a un proyecto"""
        try:
            if not employee.user:
                logger.warning(f"Empleado {employee.full_name} no tiene usuario asociado")
                return None
            
            notification = Notification.create_project_assignment_notification(
                employee.user, project, created_by_user
            )
            db.session.commit()
            logger.info(f"Notificación de asignación a proyecto enviada a {employee.user.email}")
            return notification
            
        except Exception as e:
            logger.error(f"Error enviando notificación de asignación a proyecto: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def notify_team_assignment(employee: Employee, team: Team, created_by_user: User) -> Optional[Notification]:
        """Notifica a un empleado sobre su asignación a un equipo"""
        try:
            if not employee.user:
                logger.warning(f"Empleado {employee.full_name} no tiene usuario asociado")
                return None
            
            notification = Notification.create_team_assignment_notification(
                employee.user, team, created_by_user
            )
            db.session.commit()
            logger.info(f"Notificación de asignación a equipo enviada a {employee.user.email}")
            return notification
            
        except Exception as e:
            logger.error(f"Error enviando notificación de asignación a equipo: {e}")
            db.session.rollback()
            return None
