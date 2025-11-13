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
                    from .email_service import EmailService
                    email_service = EmailService()
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
