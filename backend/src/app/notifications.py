from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from datetime import datetime
import logging

from models.notification import Notification
from models.user import db
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@auth_required()
def list_notifications():
    """Lista notificaciones del usuario actual"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Construir query
        query = Notification.query.filter(Notification.user_id == current_user.id)
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        # Ordenar por prioridad y fecha
        query = query.order_by(
            Notification.priority.desc(),
            Notification.created_at.desc()
        )
        
        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        notifications_data = [notif.to_dict() for notif in pagination.items]
        
        return jsonify({
            'success': True,
            'notifications': notifications_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'unread_only': unread_only
        })
        
    except Exception as e:
        logger.error(f"Error listando notificaciones: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo notificaciones'
        }), 500

@notifications_bp.route('/summary', methods=['GET'])
@auth_required()
def get_notifications_summary():
    """Obtiene resumen de notificaciones del usuario actual"""
    try:
        summary = NotificationService.get_notification_summary(current_user.id)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de notificaciones: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo resumen'
        }), 500

@notifications_bp.route('/mark-read', methods=['POST'])
@auth_required()
def mark_notifications_read():
    """Marca notificaciones como leídas"""
    try:
        data = request.get_json()
        
        if not data or 'notification_ids' not in data:
            return jsonify({
                'success': False,
                'message': 'IDs de notificaciones son requeridos'
            }), 400
        
        notification_ids = data['notification_ids']
        
        if not isinstance(notification_ids, list):
            return jsonify({
                'success': False,
                'message': 'notification_ids debe ser una lista'
            }), 400
        
        # Marcar como leídas
        updated_count = NotificationService.mark_notifications_as_read(
            notification_ids, current_user.id
        )
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} notificaciones marcadas como leídas',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error marcando notificaciones como leídas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error marcando notificaciones'
        }), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@auth_required()
def mark_all_notifications_read():
    """Marca todas las notificaciones no leídas como leídas"""
    try:
        # Obtener todas las notificaciones no leídas del usuario
        unread_notifications = Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.read == False
        ).all()
        
        notification_ids = [notif.id for notif in unread_notifications]
        
        if not notification_ids:
            return jsonify({
                'success': True,
                'message': 'No hay notificaciones sin leer',
                'updated_count': 0
            })
        
        # Marcar como leídas
        updated_count = NotificationService.mark_notifications_as_read(
            notification_ids, current_user.id
        )
        
        return jsonify({
            'success': True,
            'message': f'Todas las notificaciones marcadas como leídas ({updated_count})',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error marcando todas las notificaciones: {e}")
        return jsonify({
            'success': False,
            'message': 'Error marcando notificaciones'
        }), 500

@notifications_bp.route('/<int:notification_id>', methods=['GET'])
@auth_required()
def get_notification(notification_id):
    """Obtiene una notificación específica"""
    try:
        notification = Notification.query.filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'message': 'Notificación no encontrada'
            }), 404
        
        # Marcar como leída automáticamente al verla
        if not notification.read:
            notification.read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'notification': notification.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo notificación {notification_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo notificación'
        }), 500

@notifications_bp.route('/<int:notification_id>/mark-read', methods=['POST'])
@auth_required()
def mark_single_notification_read(notification_id):
    """Marca una notificación específica como leída"""
    try:
        notification = Notification.query.filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'message': 'Notificación no encontrada'
            }), 404
        
        if notification.read:
            return jsonify({
                'success': True,
                'message': 'La notificación ya estaba marcada como leída'
            })
        
        notification.read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notificación marcada como leída',
            'notification': notification.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marcando notificación {notification_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error marcando notificación'
        }), 500

@notifications_bp.route('/create', methods=['POST'])
@auth_required()
def create_notification():
    """Crea una notificación personalizada (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden crear notificaciones'
            }), 403
        
        data = request.get_json()
        
        required_fields = ['user_id', 'title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar que el usuario existe
        from models.user import User
        target_user = User.query.get(data['user_id'])
        if not target_user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Crear notificación
        notification = NotificationService.create_system_notification(
            user_id=data['user_id'],
            title=data['title'],
            message=data['message'],
            priority=data.get('priority', 'medium'),
            send_email=data.get('send_email', False),
            data=data.get('data', {})
        )
        
        if notification:
            return jsonify({
                'success': True,
                'message': 'Notificación creada exitosamente',
                'notification': notification.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Error creando notificación'
            }), 500
        
    except Exception as e:
        logger.error(f"Error creando notificación: {e}")
        return jsonify({
            'success': False,
            'message': 'Error creando notificación'
        }), 500

@notifications_bp.route('/broadcast', methods=['POST'])
@auth_required()
def broadcast_notification():
    """Envía una notificación a múltiples usuarios (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden enviar notificaciones masivas'
            }), 403
        
        data = request.get_json()
        
        required_fields = ['title', 'message', 'target_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        target_type = data['target_type']  # 'all', 'employees', 'managers', 'team'
        
        # Determinar usuarios objetivo
        from models.user import User
        target_users = []
        
        if target_type == 'all':
            target_users = User.query.filter(User.active == True).all()
        elif target_type == 'employees':
            employee_role = Role.query.filter_by(name='employee').first()
            if employee_role:
                target_users = [user for user in User.query.filter(User.active == True).all() 
                              if employee_role in user.roles]
        elif target_type == 'managers':
            manager_role = Role.query.filter_by(name='manager').first()
            if manager_role:
                target_users = [user for user in User.query.filter(User.active == True).all() 
                              if manager_role in user.roles]
        elif target_type == 'team':
            team_id = data.get('team_id')
            if not team_id:
                return jsonify({
                    'success': False,
                    'message': 'team_id es requerido para target_type=team'
                }), 400
            
            from models.employee import Employee
            employees = Employee.query.filter(
                Employee.team_id == team_id,
                Employee.active == True
            ).all()
            target_users = [emp.user for emp in employees if emp.user and emp.user.active]
        
        if not target_users:
            return jsonify({
                'success': False,
                'message': 'No se encontraron usuarios objetivo'
            }), 400
        
        # Crear notificaciones
        created_notifications = []
        for user in target_users:
            notification = NotificationService.create_system_notification(
                user_id=user.id,
                title=data['title'],
                message=data['message'],
                priority=data.get('priority', 'medium'),
                send_email=data.get('send_email', False),
                data=data.get('data', {})
            )
            if notification:
                created_notifications.append(notification)
        
        return jsonify({
            'success': True,
            'message': f'Notificación enviada a {len(created_notifications)} usuarios',
            'notifications_sent': len(created_notifications),
            'target_type': target_type
        })
        
    except Exception as e:
        logger.error(f"Error enviando notificación masiva: {e}")
        return jsonify({
            'success': False,
            'message': 'Error enviando notificación masiva'
        }), 500

@notifications_bp.route('/types', methods=['GET'])
@auth_required()
def get_notification_types():
    """Obtiene los tipos de notificación disponibles"""
    try:
        notification_types = Notification.get_notification_types()
        
        return jsonify({
            'success': True,
            'notification_types': notification_types
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo tipos de notificación: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo tipos'
        }), 500

@notifications_bp.route('/cleanup', methods=['POST'])
@auth_required()
def cleanup_old_notifications():
    """Limpia notificaciones antiguas (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden limpiar notificaciones'
            }), 403
        
        days_old = request.json.get('days_old', 30) if request.json else 30
        
        if days_old < 7:
            return jsonify({
                'success': False,
                'message': 'No se pueden eliminar notificaciones de menos de 7 días'
            }), 400
        
        deleted_count = NotificationService.cleanup_old_notifications(days_old)
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} notificaciones antiguas eliminadas',
            'deleted_count': deleted_count,
            'days_old': days_old
        })
        
    except Exception as e:
        logger.error(f"Error limpiando notificaciones: {e}")
        return jsonify({
            'success': False,
            'message': 'Error limpiando notificaciones'
        }), 500

@notifications_bp.route('/process-queue', methods=['POST'])
@auth_required()
def process_notification_queue():
    """Procesa la cola de notificaciones pendientes (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden procesar la cola'
            }), 403
        
        results = NotificationService.process_notification_queue()
        
        return jsonify({
            'success': True,
            'message': f'Cola procesada: {results["sent"]}/{results["processed"]} enviados',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error procesando cola de notificaciones: {e}")
        return jsonify({
            'success': False,
            'message': 'Error procesando cola'
        }), 500
