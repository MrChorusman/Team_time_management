from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from datetime import datetime, timedelta
import logging

from models.user import User, Role, db
from models.employee import Employee
from models.team import Team
from models.holiday import Holiday
from models.calendar_activity import CalendarActivity
from models.notification import Notification
from models.company import Company
from models.email_verification_token import EmailVerificationToken
from services.notification_service import NotificationService
from services.holiday_service import HolidayService
from services.email_service import EmailService
from services.google_oauth_service import GoogleOAuthService
from utils.decorators import admin_required

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@auth_required()
@admin_required()
def get_admin_dashboard():
    """Obtiene el dashboard de administración"""
    try:
        # Estadísticas generales
        stats = {
            'users': {
                'total': User.query.count(),
                'active': User.query.filter(User.active == True).count(),
                'inactive': User.query.filter(User.active == False).count()
            },
            'employees': {
                'total': Employee.query.count(),
                'active': Employee.query.filter(Employee.active == True).count(),
                'approved': Employee.query.filter(Employee.approved == True).count(),
                'pending_approval': Employee.query.filter(
                    Employee.active == True,
                    Employee.approved == False
                ).count()
            },
            'teams': {
                'total': Team.query.count(),
                'active': Team.query.count(),  # Todos los equipos están activos (no hay columna active)
                'with_manager': Team.query.filter(Team.manager_id.isnot(None)).count()
            },
            'holidays': {
                'total': Holiday.query.count(),
                'active': Holiday.query.filter(Holiday.active == True).count(),
                'countries': Holiday.query.with_entities(Holiday.country).distinct().count()
            },
            'notifications': {
                'total': Notification.query.count(),
                'unread': Notification.query.filter(Notification.read == False).count(),
                'pending_email': Notification.query.filter(
                    Notification.send_email == True,
                    Notification.email_sent == False
                ).count()
            }
        }
        
        # Actividad reciente
        recent_activity = []
        
        # Usuarios registrados recientemente
        recent_users = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(User.created_at.desc()).limit(5).all()
        
        for user in recent_users:
            recent_activity.append({
                'type': 'user_registration',
                'description': f'Nuevo usuario registrado: {user.email}',
                'timestamp': user.created_at.isoformat(),
                'user_id': user.id
            })
        
        # Empleados registrados recientemente
        recent_employees = Employee.query.filter(
            Employee.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(Employee.created_at.desc()).limit(5).all()
        
        for employee in recent_employees:
            recent_activity.append({
                'type': 'employee_registration',
                'description': f'Nuevo empleado: {employee.full_name}',
                'timestamp': employee.created_at.isoformat(),
                'employee_id': employee.id,
                'approved': employee.approved
            })
        
        # Invitaciones enviadas recientemente
        from models.employee_invitation import EmployeeInvitation
        recent_invitations = EmployeeInvitation.query.filter(
            EmployeeInvitation.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(EmployeeInvitation.created_at.desc()).limit(5).all()
        
        for invitation in recent_invitations:
            inviter = User.query.get(invitation.invited_by)
            inviter_name = inviter.email if inviter else 'Sistema'
            recent_activity.append({
                'type': 'invitation_sent',
                'description': f'Invitación enviada a {invitation.email}',
                'timestamp': invitation.created_at.isoformat(),
                'invitation_email': invitation.email,
                'invited_by': inviter_name
            })
        
        # Ordenar actividad por fecha
        recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Distribución por roles
        role_distribution = []
        roles = Role.query.all()
        
        for role in roles:
            user_count = User.query.filter(
                User.roles.contains(role),
                User.active == True
            ).count()
            role_distribution.append({
                'role': role.name,
                'description': role.description,
                'user_count': user_count
            })
        
        # Equipos más activos (por número de actividades recientes)
        team_activity = db.session.query(
            Team.id,
            Team.name,
            db.func.count(CalendarActivity.id).label('activity_count')
        ).join(
            Employee, Team.id == Employee.team_id
        ).join(
            CalendarActivity, Employee.id == CalendarActivity.employee_id
        ).filter(
            CalendarActivity.created_at >= datetime.utcnow() - timedelta(days=30)
        ).group_by(Team.id, Team.name).order_by(
            db.func.count(CalendarActivity.id).desc()
        ).limit(10).all()
        
        most_active_teams = [
            {
                'team_id': team.id,
                'team_name': team.name,
                'activity_count': team.activity_count
            }
            for team in team_activity
        ]
        
        return jsonify({
            'success': True,
            'dashboard': {
                'statistics': stats,
                'recent_activity': recent_activity[:10],
                'role_distribution': role_distribution,
                'most_active_teams': most_active_teams,
                'generated_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo dashboard de admin: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo dashboard'
        }), 500

@admin_bp.route('/users', methods=['GET'])
@auth_required()
@admin_required()
def list_all_users():
    """Lista todos los usuarios del sistema"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role_filter = request.args.get('role')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # Construir query
        query = User.query
        
        if active_only:
            query = query.filter(User.active == True)
        
        if role_filter:
            role = Role.query.filter_by(name=role_filter).first()
            if role:
                query = query.filter(User.roles.contains(role))
        
        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in pagination.items:
            user_data = user.to_dict()
            # Añadir información del empleado si existe
            if user.employee:
                user_data['employee'] = user.employee.to_dict()
            users_data.append(user_data)
        
        return jsonify({
            'success': True,
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'role': role_filter,
                'active_only': active_only
            }
        })
        
    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo usuarios'
        }), 500

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@auth_required()
@admin_required()
def toggle_user_active(user_id):
    """Activa/desactiva un usuario"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # No permitir desactivar al propio usuario admin
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'No puedes desactivar tu propia cuenta'
            }), 400
        
        user.active = not user.active
        
        # Si se desactiva el usuario, también desactivar su empleado
        if not user.active and user.employee:
            user.employee.active = False
        
        db.session.commit()
        
        status = 'activado' if user.active else 'desactivado'
        logger.info(f"Usuario {user.email} {status} por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': f'Usuario {status} exitosamente',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error modificando usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error modificando usuario'
        }), 500

@admin_bp.route('/users/<int:user_id>/roles', methods=['PUT'])
@auth_required()
@admin_required()
def update_user_roles(user_id):
    """Actualiza los roles de un usuario"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        data = request.get_json()
        
        if not data or 'role_names' not in data:
            return jsonify({
                'success': False,
                'message': 'Lista de roles es requerida'
            }), 400
        
        role_names = data['role_names']
        
        if not isinstance(role_names, list):
            return jsonify({
                'success': False,
                'message': 'role_names debe ser una lista'
            }), 400
        
        # Obtener roles válidos
        new_roles = []
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                new_roles.append(role)
            else:
                return jsonify({
                    'success': False,
                    'message': f'Rol no válido: {role_name}'
                }), 400
        
        # Actualizar roles
        user.roles.clear()
        for role in new_roles:
            user.roles.append(role)
        
        db.session.commit()
        
        logger.info(f"Roles actualizados para usuario {user.email}: {role_names}")
        
        return jsonify({
            'success': True,
            'message': 'Roles actualizados exitosamente',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando roles del usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando roles'
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@auth_required()
@admin_required()
def delete_user(user_id):
    """Elimina un usuario del sistema"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # No permitir eliminar al propio usuario admin
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'No puedes eliminar tu propia cuenta'
            }), 400
        
        email = user.email
        
        # Eliminar explícitamente los tokens de verificación de email asociados
        # Esto evita problemas con la restricción NOT NULL en user_id
        email_tokens = EmailVerificationToken.query.filter_by(user_id=user_id).all()
        for token in email_tokens:
            db.session.delete(token)
        
        # Eliminar usuario (las relaciones CASCADE eliminarán empleado, notificaciones, etc.)
        db.session.delete(user)
        db.session.commit()
        
        # Notificar a todos los administradores sobre la eliminación
        try:
            NotificationService.notify_user_deleted(email, current_user)
        except Exception as notif_error:
            logger.error(f"Error enviando notificación de eliminación de usuario: {notif_error}")
            # No fallar si la notificación no se puede enviar
        
        logger.info(f"Usuario {email} eliminado por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': f'Usuario {email} eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando usuario {user_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error eliminando usuario: {str(e)}'
        }), 500

@admin_bp.route('/system/maintenance', methods=['POST'])
@auth_required()
@admin_required()
def run_system_maintenance():
    """Ejecuta tareas de mantenimiento del sistema"""
    try:
        data = request.get_json() or {}
        tasks = data.get('tasks', ['cleanup_notifications', 'process_notification_queue'])
        
        results = {
            'executed_tasks': [],
            'errors': []
        }
        
        # Limpiar notificaciones antiguas
        if 'cleanup_notifications' in tasks:
            try:
                days_old = data.get('cleanup_days', 30)
                deleted_count = NotificationService.cleanup_old_notifications(days_old)
                results['executed_tasks'].append({
                    'task': 'cleanup_notifications',
                    'result': f'{deleted_count} notificaciones eliminadas',
                    'success': True
                })
            except Exception as e:
                results['errors'].append(f'Error limpiando notificaciones: {e}')
        
        # Procesar cola de notificaciones
        if 'process_notification_queue' in tasks:
            try:
                queue_results = NotificationService.process_notification_queue()
                results['executed_tasks'].append({
                    'task': 'process_notification_queue',
                    'result': f'{queue_results["sent"]}/{queue_results["processed"]} emails enviados',
                    'success': True,
                    'details': queue_results
                })
            except Exception as e:
                results['errors'].append(f'Error procesando cola: {e}')
        
        # Cargar festivos faltantes
        if 'load_missing_holidays' in tasks:
            try:
                holiday_service = HolidayService()
                holiday_results = holiday_service.auto_load_missing_holidays()
                results['executed_tasks'].append({
                    'task': 'load_missing_holidays',
                    'result': f'{holiday_results["total_holidays_loaded"]} festivos cargados',
                    'success': True,
                    'details': holiday_results
                })
            except Exception as e:
                results['errors'].append(f'Error cargando festivos: {e}')
        
        # Limpiar sesiones expiradas
        if 'cleanup_sessions' in tasks:
            try:
                # Esta tarea dependería de la configuración de sesiones de Flask
                results['executed_tasks'].append({
                    'task': 'cleanup_sessions',
                    'result': 'Sesiones limpiadas (simulado)',
                    'success': True
                })
            except Exception as e:
                results['errors'].append(f'Error limpiando sesiones: {e}')
        
        return jsonify({
            'success': True,
            'message': f'Mantenimiento completado. {len(results["executed_tasks"])} tareas ejecutadas.',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error en mantenimiento del sistema: {e}")
        return jsonify({
            'success': False,
            'message': 'Error ejecutando mantenimiento'
        }), 500

@admin_bp.route('/system/stats', methods=['GET'])
@auth_required()
@admin_required()
def get_system_stats():
    """Obtiene estadísticas detalladas del sistema"""
    try:
        # Estadísticas de base de datos
        db_stats = {
            'users': User.query.count(),
            'employees': Employee.query.count(),
            'teams': Team.query.count(),
            'holidays': Holiday.query.count(),
            'calendar_activities': CalendarActivity.query.count(),
            'notifications': Notification.query.count()
        }
        
        # Estadísticas de actividad (últimos 30 días)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        activity_stats = {
            'new_users': User.query.filter(User.created_at >= thirty_days_ago).count(),
            'new_employees': Employee.query.filter(Employee.created_at >= thirty_days_ago).count(),
            'new_activities': CalendarActivity.query.filter(CalendarActivity.created_at >= thirty_days_ago).count(),
            'notifications_sent': Notification.query.filter(
                Notification.created_at >= thirty_days_ago,
                Notification.email_sent == True
            ).count()
        }
        
        # Distribución por países
        country_distribution = db.session.query(
            Employee.country,
            db.func.count(Employee.id).label('employee_count')
        ).filter(
            Employee.active == True
        ).group_by(Employee.country).order_by(
            db.func.count(Employee.id).desc()
        ).all()
        
        countries = [
            {
                'country': country.country,
                'employee_count': country.employee_count
            }
            for country in country_distribution
        ]
        
        # Eficiencia promedio por equipo
        team_efficiency = []
        teams = Team.query.all()  # Todos los equipos (no hay columna active)
        
        for team in teams:
            if team.active_employees:
                total_efficiency = sum(
                    emp.get_hours_summary(datetime.now().year, datetime.now().month)['efficiency']
                    for emp in team.active_employees
                )
                avg_efficiency = total_efficiency / len(team.active_employees)
                
                team_efficiency.append({
                    'team_name': team.name,
                    'employee_count': len(team.active_employees),
                    'average_efficiency': round(avg_efficiency, 2)
                })
        
        # Tipos de actividad más comunes
        activity_types = db.session.query(
            CalendarActivity.activity_type,
            db.func.count(CalendarActivity.id).label('count')
        ).filter(
            CalendarActivity.created_at >= thirty_days_ago
        ).group_by(CalendarActivity.activity_type).order_by(
            db.func.count(CalendarActivity.id).desc()
        ).all()
        
        activity_type_stats = [
            {
                'type': activity.activity_type,
                'count': activity.count,
                'display_name': CalendarActivity.get_activity_display_name(activity.activity_type)
            }
            for activity in activity_types
        ]
        
        return jsonify({
            'success': True,
            'stats': {
                'database': db_stats,
                'activity_last_30_days': activity_stats,
                'country_distribution': countries,
                'team_efficiency': sorted(team_efficiency, key=lambda x: x['average_efficiency'], reverse=True),
                'activity_types': activity_type_stats,
                'generated_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del sistema: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo estadísticas'
        }), 500

@admin_bp.route('/system/backup-info', methods=['GET'])
@auth_required()
@admin_required()
def get_backup_info():
    """Obtiene información sobre respaldos del sistema"""
    try:
        # Esta sería una implementación básica
        # En un entorno real, se conectaría con el sistema de respaldos
        
        backup_info = {
            'last_backup': None,  # Se obtendría de la configuración real
            'backup_frequency': 'daily',
            'backup_retention': '30 days',
            'backup_size': 'N/A',
            'backup_status': 'configured',
            'next_backup': None,
            'backup_location': 'cloud_storage',
            'tables_included': [
                'users', 'employees', 'teams', 'holidays', 
                'calendar_activities', 'notifications'
            ]
        }
        
        return jsonify({
            'success': True,
            'backup_info': backup_info,
            'note': 'Esta es información simulada. Implementar según el sistema de respaldos real.'
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo información de respaldos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo información de respaldos'
        }), 500

@admin_bp.route('/logs', methods=['GET'])
@auth_required()
@admin_required()
def get_system_logs():
    """Obtiene logs del sistema"""
    try:
        from logging_config import get_logger
        import os
        
        # Parámetros de consulta
        level = request.args.get('level', 'INFO')
        limit = min(request.args.get('limit', 50, type=int), 200)
        category = request.args.get('category')
        
        # En un entorno real, esto leería los archivos de log estructurados
        # Por ahora, devolvemos logs simulados basados en la actividad reciente
        
        logs = []
        
        # Logs de usuarios recientes
        recent_users = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(User.created_at.desc()).limit(10).all()
        
        for user in recent_users:
            logs.append({
                'timestamp': user.created_at.isoformat(),
                'level': 'INFO',
                'message': f'Nuevo usuario registrado: {user.email}',
                'category': 'user_management',
                'logger': 'team_time.user_actions',
                'module': 'admin',
                'function': 'get_system_logs'
            })
        
        # Logs de empleados recientes
        recent_employees = Employee.query.filter(
            Employee.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(Employee.created_at.desc()).limit(10).all()
        
        for employee in recent_employees:
            logs.append({
                'timestamp': employee.created_at.isoformat(),
                'level': 'INFO',
                'message': f'Nuevo empleado registrado: {employee.full_name}',
                'category': 'employee_management',
                'logger': 'team_time.user_actions',
                'module': 'admin',
                'function': 'get_system_logs'
            })
        
        # Logs de autenticación reciente
        auth_logs = [
            {
                'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'level': 'INFO',
                'message': 'Login exitoso',
                'category': 'authentication',
                'logger': 'team_time.auth',
                'module': 'auth',
                'function': 'login'
            },
            {
                'timestamp': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                'level': 'WARNING',
                'message': 'Intento de login fallido',
                'category': 'security',
                'logger': 'team_time.security',
                'module': 'auth',
                'function': 'login'
            }
        ]
        logs.extend(auth_logs)
        
        # Filtrar por nivel si se especifica
        if level != 'ALL':
            logs = [log for log in logs if log['level'] == level]
        
        # Filtrar por categoría si se especifica
        if category:
            logs = [log for log in logs if log['category'] == category]
        
        # Ordenar logs por timestamp
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limitar resultados
        logs = logs[:limit]
        
        return jsonify({
            'success': True,
            'logs': logs,
            'filters': {
                'level': level,
                'category': category,
                'limit': limit
            },
            'total_found': len(logs),
            'note': 'Estos son logs simulados. En producción, se leerían archivos de log reales.'
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo logs del sistema: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo logs'
        }), 500

@admin_bp.route('/logs/email', methods=['GET'])
@auth_required()
@admin_required()
def get_email_logs():
    """Obtiene logs específicos de email"""
    try:
        from services.email_service import EmailService
        from flask import current_app
        
        email_service = EmailService()
        email_service.init_app(current_app)
        
        # Si está en modo mock, obtener estadísticas del mock
        if email_service.use_mock_mode:
            stats = email_service.get_mock_email_stats()
            sent_emails = email_service.get_mock_sent_emails(limit=50)
            
            return jsonify({
                'success': True,
                'mode': 'mock',
                'stats': stats,
                'recent_emails': sent_emails,
                'note': 'Modo mock activo - emails simulados'
            })
        else:
            # En modo real, devolver información de configuración
            return jsonify({
                'success': True,
                'mode': 'real',
                'message': 'Emails enviados por SMTP real',
                'note': 'Los logs de email reales se almacenan en el sistema de logging'
            })
        
    except Exception as e:
        logger.error(f"Error obteniendo logs de email: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo logs de email'
        }), 500

@admin_bp.route('/metrics', methods=['GET'])
@auth_required()
@admin_required()
def get_system_metrics():
    """Obtiene métricas del sistema"""
    try:
        import psutil
        from flask import current_app
        
        # Métricas de sistema
        system_metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent_used': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free,
                'percent_used': psutil.disk_usage('/').percent
            }
        }
        
        # Métricas de aplicación
        app_metrics = {
            'active_users': User.query.filter(User.active == True).count(),
            'total_employees': Employee.query.count(),
            'active_teams': Team.query.count(),  # Todos los equipos (no hay columna active)
            'pending_notifications': Notification.query.filter(
                Notification.read == False
            ).count(),
            'unread_notifications': Notification.query.filter(
                Notification.read == False
            ).count()
        }
        
        # Métricas de actividad (últimas 24 horas)
        last_24h = datetime.utcnow() - timedelta(hours=24)
        activity_metrics = {
            'new_users_24h': User.query.filter(User.created_at >= last_24h).count(),
            'new_employees_24h': Employee.query.filter(Employee.created_at >= last_24h).count(),
            'calendar_activities_24h': CalendarActivity.query.filter(
                CalendarActivity.created_at >= last_24h
            ).count(),
            'notifications_sent_24h': Notification.query.filter(
                Notification.created_at >= last_24h,
                Notification.email_sent == True
            ).count()
        }
        
        # Métricas de configuración
        config_metrics = {
            'google_oauth_configured': current_app.config.get('google_oauth_configured', False),
            'email_configured': current_app.config.get('email_configured', False),
            'mock_email_mode': current_app.config.get('should_use_mock_email', False),
            'log_level': current_app.config.get('LOG_LEVEL', 'INFO'),
            'environment': current_app.config.get('FLASK_ENV', 'unknown')
        }
        
        return jsonify({
            'success': True,
            'metrics': {
                'system': system_metrics,
                'application': app_metrics,
                'activity_24h': activity_metrics,
                'configuration': config_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas del sistema: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo métricas'
        }), 500

@admin_bp.route('/test-smtp', methods=['POST'])
@auth_required()
@admin_required()
def test_smtp_configuration():
    """Prueba la configuración SMTP"""
    try:
        from flask import current_app
        
        # Inicializar servicio de email
        email_service = EmailService()
        email_service.init_app(current_app)
        
        # Probar configuración
        result = email_service.test_email_configuration()
        
        if result['success']:
            logger.info(f"Prueba SMTP exitosa: {result['message']}")
            return jsonify({
                'success': True,
                'message': result['message'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"Prueba SMTP fallida: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error'],
                'timestamp': datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error probando configuración SMTP: {e}")
        return jsonify({
            'success': False,
            'error': f'Error probando configuración SMTP: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

@admin_bp.route('/email-config', methods=['GET'])
@auth_required()
@admin_required()
def get_email_configuration():
    """Obtiene la configuración actual de email (sin mostrar credenciales)"""
    try:
        from flask import current_app
        
        config = {
            'mail_server': current_app.config.get('MAIL_SERVER'),
            'mail_port': current_app.config.get('MAIL_PORT'),
            'mail_use_tls': current_app.config.get('MAIL_USE_TLS'),
            'mail_username': current_app.config.get('MAIL_USERNAME'),
            'mail_default_sender': current_app.config.get('MAIL_DEFAULT_SENDER'),
            'configured': bool(current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_PASSWORD'))
        }
        
        return jsonify({
            'success': True,
            'config': config,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración de email: {e}")
        return jsonify({
            'success': False,
            'error': f'Error obteniendo configuración: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

@admin_bp.route('/google-oauth-config', methods=['GET'])
@auth_required()
@admin_required()
def get_google_oauth_configuration():
    """Obtiene la configuración actual de Google OAuth (sin mostrar credenciales)"""
    try:
        from flask import current_app
        
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        config = {
            'configured': google_oauth.is_configured(),
            'client_id': current_app.config.get('GOOGLE_CLIENT_ID', '').split('.')[0] + '...' if current_app.config.get('GOOGLE_CLIENT_ID') else None,
            'redirect_uri': current_app.config.get('GOOGLE_REDIRECT_URI'),
            'has_client_secret': bool(current_app.config.get('GOOGLE_CLIENT_SECRET'))
        }
        
        return jsonify({
            'success': True,
            'config': config,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración de Google OAuth: {e}")
        return jsonify({
            'success': False,
            'error': f'Error obteniendo configuración: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

@admin_bp.route('/test-google-oauth', methods=['POST'])
@auth_required()
@admin_required()
def test_google_oauth_configuration():
    """Prueba la configuración de Google OAuth"""
    try:
        from flask import current_app
        
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        if not google_oauth.is_configured():
            return jsonify({
                'success': False,
                'error': 'Google OAuth no está configurado completamente',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Intentar generar URL de autorización (prueba básica)
        try:
            auth_url = google_oauth.get_auth_url()
            logger.info("Google OAuth configurado correctamente - URL generada")
            
            return jsonify({
                'success': True,
                'message': 'Google OAuth configurado correctamente',
                'auth_url_preview': auth_url[:50] + '...',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error generando URL de autorización: {e}',
                'timestamp': datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error probando configuración Google OAuth: {e}")
        return jsonify({
            'success': False,
            'error': f'Error probando configuración Google OAuth: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== ENDPOINTS DE GESTIÓN DE EMPRESAS ====================

@admin_bp.route('/companies', methods=['GET'])
@auth_required()
def list_companies():
    """Lista todas las empresas (admins y managers pueden acceder)"""
    try:
        # Permitir acceso a admins y managers
        if not (current_user.is_admin() or current_user.is_manager()):
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        query = Company.query
        if active_only:
            query = query.filter(Company.active == True)
        
        companies = query.order_by(Company.name).all()
        
        return jsonify({
            'success': True,
            'companies': [company.to_dict() for company in companies]
        })
    except Exception as e:
        logger.error(f"Error listando empresas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo empresas'
        }), 500

@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@auth_required()
@admin_required()
def get_company(company_id):
    """Obtiene una empresa específica"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'message': 'Empresa no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'company': company.to_dict()
        })
    except Exception as e:
        logger.error(f"Error obteniendo empresa {company_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo empresa'
        }), 500

@admin_bp.route('/companies', methods=['POST'])
@auth_required()
@admin_required()
def create_company():
    """Crea una nueva empresa"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'El nombre de la empresa es requerido'
            }), 400
        
        billing_start = data.get('billing_period_start_day')
        billing_end = data.get('billing_period_end_day')
        
        if billing_start is None or billing_end is None:
            return jsonify({
                'success': False,
                'message': 'Los días de período de facturación son requeridos'
            }), 400
        
        if not (1 <= billing_start <= 31) or not (1 <= billing_end <= 31):
            return jsonify({
                'success': False,
                'message': 'Los días de período deben estar entre 1 y 31'
            }), 400
        
        # Verificar si ya existe una empresa con ese nombre
        existing = Company.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Ya existe una empresa con ese nombre'
            }), 409
        
        # Crear empresa
        company = Company(
            name=data['name'],
            billing_period_start_day=billing_start,
            billing_period_end_day=billing_end,
            active=data.get('active', True)
        )
        
        db.session.add(company)
        db.session.commit()
        
        # Notificar a todos los administradores sobre la creación
        try:
            NotificationService.notify_company_action(company, 'created', current_user)
        except Exception as notif_error:
            logger.error(f"Error enviando notificación de creación de empresa: {notif_error}")
            # No fallar si la notificación no se puede enviar
        
        return jsonify({
            'success': True,
            'company': company.to_dict(),
            'message': 'Empresa creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando empresa: {e}")
        return jsonify({
            'success': False,
            'message': 'Error creando empresa'
        }), 500

@admin_bp.route('/companies/<int:company_id>', methods=['PUT'])
@auth_required()
@admin_required()
def update_company(company_id):
    """Actualiza una empresa"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'message': 'Empresa no encontrada'
            }), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'name' in data:
            # Verificar que no haya otra empresa con ese nombre
            existing = Company.query.filter(
                Company.name == data['name'],
                Company.id != company_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': 'Ya existe otra empresa con ese nombre'
                }), 409
            company.name = data['name']
        
        if 'billing_period_start_day' in data:
            billing_start = data['billing_period_start_day']
            if not (1 <= billing_start <= 31):
                return jsonify({
                    'success': False,
                    'message': 'El día de inicio debe estar entre 1 y 31'
                }), 400
            company.billing_period_start_day = billing_start
        
        if 'billing_period_end_day' in data:
            billing_end = data['billing_period_end_day']
            if not (1 <= billing_end <= 31):
                return jsonify({
                    'success': False,
                    'message': 'El día de fin debe estar entre 1 y 31'
                }), 400
            company.billing_period_end_day = billing_end
        
        if 'active' in data:
            company.active = data['active']
        
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notificar a todos los administradores sobre la actualización
        try:
            NotificationService.notify_company_action(company, 'updated', current_user)
        except Exception as notif_error:
            logger.error(f"Error enviando notificación de actualización de empresa: {notif_error}")
            # No fallar si la notificación no se puede enviar
        
        return jsonify({
            'success': True,
            'company': company.to_dict(),
            'message': 'Empresa actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando empresa {company_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando empresa'
        }), 500

@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@auth_required()
@admin_required()
def delete_company(company_id):
    """Elimina una empresa (marca como inactiva)"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'message': 'Empresa no encontrada'
            }), 404
        
        # En lugar de eliminar físicamente, marcamos como inactiva
        # Esto preserva los datos históricos de forecast
        company.active = False
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notificar a todos los administradores sobre la eliminación
        try:
            NotificationService.notify_company_action(company, 'deleted', current_user)
        except Exception as notif_error:
            logger.error(f"Error enviando notificación de eliminación de empresa: {notif_error}")
            # No fallar si la notificación no se puede enviar
        
        return jsonify({
            'success': True,
            'message': 'Empresa desactivada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando empresa {company_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error eliminando empresa'
        }), 500
