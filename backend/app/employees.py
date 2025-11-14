from flask import Blueprint, request, jsonify, current_app
from flask_security import auth_required, current_user
from datetime import datetime, timedelta
import logging
import secrets

from models.user import User, Role, db
from models.employee import Employee
from models.employee_invitation import EmployeeInvitation
from models.team import Team
from models.notification import Notification
from services.notification_service import NotificationService
from services.holiday_service import HolidayService
from services.email_service import send_invitation_email
from utils.decorators import admin_required, manager_or_admin_required

logger = logging.getLogger(__name__)

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/register', methods=['POST'])
@auth_required()
def register_employee():
    """Registra un nuevo empleado"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = [
            'full_name', 'team_id', 'hours_monday_thursday', 'hours_friday',
            'annual_vacation_days', 'annual_hld_hours', 'country'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Validar rangos numéricos
        try:
            hours_mon_thu = float(data['hours_monday_thursday'])
            hours_fri = float(data['hours_friday'])
            vacation_days = int(data['annual_vacation_days'])
            hld_hours = int(data['annual_hld_hours'])
            
            if not (0 <= hours_mon_thu <= 12):
                return jsonify({
                    'success': False,
                    'message': 'Horas Lunes-Jueves debe estar entre 0 y 12'
                }), 400
            
            if not (0 <= hours_fri <= 12):
                return jsonify({
                    'success': False,
                    'message': 'Horas Viernes debe estar entre 0 y 12'
                }), 400
            
            if not (1 <= vacation_days <= 50):
                return jsonify({
                    'success': False,
                    'message': 'Días de vacaciones debe estar entre 1 y 50'
                }), 400
            
            if not (0 <= hld_hours <= 300):
                return jsonify({
                    'success': False,
                    'message': 'Horas de libre disposición debe estar entre 0 y 300'
                }), 400
        except (ValueError, TypeError) as e:
            return jsonify({
                'success': False,
                'message': 'Valores numéricos inválidos'
            }), 400
        
        # Verificar si el usuario ya tiene un empleado registrado
        if current_user.employee:
            return jsonify({
                'success': False,
                'message': 'Ya tienes un perfil de empleado registrado'
            }), 409
        
        # Validar que el equipo existe
        team_id = data.get('team_id')
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        # Validar horario de verano si está habilitado
        has_summer = bool(data.get('has_summer_schedule', False))
        hours_summer = None
        summer_months = []
        
        if has_summer:
            # Si tiene horario de verano, validar campos relacionados
            if not data.get('hours_summer'):
                return jsonify({
                    'success': False,
                    'message': 'Horas de verano requeridas cuando tiene horario de verano'
                }), 400
            
            hours_summer = float(data['hours_summer'])
            if not (0 <= hours_summer <= 12):
                return jsonify({
                    'success': False,
                    'message': 'Horas de verano debe estar entre 0 y 12'
                }), 400
            
            summer_months = data.get('summer_months', [])
            if not summer_months or len(summer_months) == 0:
                return jsonify({
                    'success': False,
                    'message': 'Debe seleccionar al menos un mes de verano'
                }), 400
            
            # Validar que los meses sean válidos (1-12)
            if not all(isinstance(m, int) and 1 <= m <= 12 for m in summer_months):
                return jsonify({
                    'success': False,
                    'message': 'Meses de verano inválidos'
                }), 400
        
        # Crear empleado
        employee = Employee(
            user_id=current_user.id,
            full_name=data['full_name'].strip(),
            team_id=team_id,
            hours_monday_thursday=hours_mon_thu,
            hours_friday=hours_fri,
            hours_summer=hours_summer,
            has_summer_schedule=has_summer,
            annual_vacation_days=vacation_days,
            annual_hld_hours=hld_hours,
            country=data['country'].strip(),
            region=data.get('region', '').strip() if data.get('region') else None,
            city=data.get('city', '').strip() if data.get('city') else None,
            active=True,
            approved=False  # Requiere aprobación del manager
        )
        
        # Configurar meses de verano si aplica
        if has_summer and summer_months:
            employee.summer_months_list = summer_months
        
        db.session.add(employee)
        
        # ⚠️ NO confirmar email automáticamente - el usuario debe verificar su email primero
        # El email debe estar verificado antes de completar el registro de empleado
        
        db.session.commit()
        
        # Cargar festivos automáticamente para la ubicación del empleado
        holiday_service = HolidayService()
        holidays_loaded, errors = holiday_service.load_holidays_for_employee_location(employee)
        
        if holidays_loaded > 0:
            logger.info(f"Cargados {holidays_loaded} festivos para {employee.country}")
        
        # Notificar al manager del equipo
        NotificationService.notify_employee_registration(employee, current_user)
        
        # Crear notificación para administradores sobre nuevo empleado registrado
        from models.notification import NotificationType, NotificationPriority
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_users = User.query.join(User.roles).filter(Role.id == admin_role.id).all()
            for admin_user in admin_users:
                notification = Notification(
                    user_id=admin_user.id,
                    title="Nuevo empleado registrado",
                    message=f"{employee.full_name} se ha registrado en el equipo {team.name}. Estado: {'Aprobado' if employee.approved else 'Pendiente de aprobación'}",
                    notification_type=NotificationType.EMPLOYEE_REGISTRATION,
                    priority=NotificationPriority.HIGH if not employee.approved else NotificationPriority.MEDIUM,
                    send_email=False,
                    created_by=current_user.id,
                    data={
                        'employee_id': employee.id,
                        'employee_name': employee.full_name,
                        'team_id': team.id,
                        'team_name': team.name,
                        'approved': employee.approved,
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                db.session.add(notification)
            
            # Si hay aprobaciones pendientes, crear notificación de alta prioridad
            pending_count = Employee.query.filter(
                Employee.active == True,
                Employee.approved == False
            ).count()
            
            if pending_count > 0:
                for admin_user in admin_users:
                    # Crear notificación de aprobación pendiente
                    approval_notification = Notification(
                        user_id=admin_user.id,
                        title="Aprobación pendiente",
                        message=f"Tienes {pending_count} empleado(s) pendiente(s) de aprobación",
                        notification_type=NotificationType.SYSTEM_ALERT,
                        priority=NotificationPriority.HIGH,
                        send_email=False,
                        created_by=current_user.id,
                        data={
                            'pending_count': pending_count,
                            'action_url': '/employees?status=pending'
                        }
                    )
                    db.session.add(approval_notification)
            
            db.session.commit()
        
        logger.info(f"Empleado registrado: {employee.full_name} en equipo {team.name}")
        
        return jsonify({
            'success': True,
            'message': 'Empleado registrado exitosamente. Esperando aprobación del manager.',
            'employee': employee.to_dict(),
            'holidays_loaded': holidays_loaded,
            'holiday_errors': errors[:3] if errors else []  # Solo mostrar primeros 3 errores
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registrando empleado: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@employees_bp.route('/me', methods=['GET'])
@auth_required()
def get_my_employee_profile():
    """Obtiene el perfil del empleado actual"""
    try:
        if not current_user.employee:
            return jsonify({
                'success': False,
                'message': 'No tienes un perfil de empleado registrado'
            }), 404
        
        employee_data = current_user.employee.to_dict(include_summary=True)
        
        return jsonify({
            'success': True,
            'employee': employee_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil de empleado: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo perfil'
        }), 500

@employees_bp.route('/me', methods=['PUT'])
@auth_required()
def update_my_employee_profile():
    """Actualiza el perfil del empleado actual"""
    try:
        if not current_user.employee:
            return jsonify({
                'success': False,
                'message': 'No tienes un perfil de empleado registrado'
            }), 404
        
        data = request.get_json()
        employee = current_user.employee
        
        # Campos actualizables por el empleado
        updatable_fields = [
            'hours_monday_thursday', 'hours_friday', 'hours_summer',
            'has_summer_schedule', 'summer_months', 'country', 'region', 'city'
        ]
        
        changes_made = []
        
        for field in updatable_fields:
            if field in data:
                old_value = getattr(employee, field)
                
                if field == 'summer_months':
                    employee.summer_months_list = data[field]
                    new_value = employee.summer_months_list
                else:
                    setattr(employee, field, data[field])
                    new_value = data[field]
                
                if old_value != new_value:
                    changes_made.append(f"{field}: {old_value} → {new_value}")
        
        if changes_made:
            employee.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Notificar cambios al manager
            changes_summary = f"Actualizó su perfil: {', '.join(changes_made)}"
            NotificationService.notify_calendar_changes(employee, changes_summary)
            
            logger.info(f"Empleado {employee.full_name} actualizó su perfil")
        
        return jsonify({
            'success': True,
            'message': 'Perfil actualizado exitosamente',
            'employee': employee.to_dict(),
            'changes_made': len(changes_made)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando perfil: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando perfil'
        }), 500

@employees_bp.route('/', methods=['GET'])
@auth_required()
def list_employees():
    """Lista empleados (con filtros según permisos)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        team_id = request.args.get('team_id', type=int)
        # Por defecto, los admins ven todos los empleados (aprobados y pendientes)
        # Otros roles solo ven aprobados por defecto
        default_approved_only = 'false' if current_user.is_admin() else 'true'
        approved_only = request.args.get('approved_only', default_approved_only).lower() == 'true'
        
        # Construir query base
        query = Employee.query.filter(Employee.active == True)
        
        # Filtros según permisos del usuario
        if current_user.is_admin():
            # Admin puede ver todos
            pass
        elif current_user.is_manager():
            # Manager solo puede ver empleados de sus equipos
            managed_teams = current_user.get_managed_teams()
            team_ids = [team.id for team in managed_teams]
            query = query.filter(Employee.team_id.in_(team_ids))
        elif current_user.is_employee():
            # Employee solo puede ver empleados de su equipo
            if current_user.employee and current_user.employee.team_id:
                query = query.filter(Employee.team_id == current_user.employee.team_id)
            else:
                query = query.filter(Employee.id == -1)  # No mostrar nada
        else:
            # Viewer no puede ver empleados
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        # Aplicar filtros adicionales
        if team_id:
            query = query.filter(Employee.team_id == team_id)
        
        if approved_only:
            query = query.filter(Employee.approved == True)
        
        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        employees_data = []
        for employee in pagination.items:
            emp_data = employee.to_dict()
            # Añadir información del equipo
            if employee.team:
                emp_data['team_name'] = employee.team.name
            # Añadir roles del usuario asociado
            if employee.user:
                emp_data['user_roles'] = [role.name for role in employee.user.roles]
                emp_data['user_id'] = employee.user_id
            employees_data.append(emp_data)
        
        return jsonify({
            'success': True,
            'employees': employees_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error listando empleados: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo empleados'
        }), 500

@employees_bp.route('/<int:employee_id>', methods=['GET'])
@auth_required()
def get_employee(employee_id):
    """Obtiene un empleado específico"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        # Verificar permisos
        if not current_user.is_admin() and not current_user.can_manage_employee(employee):
            if current_user.employee and current_user.employee.id != employee_id:
                # Solo puede ver empleados de su equipo
                if not current_user.employee.team_id or current_user.employee.team_id != employee.team_id:
                    return jsonify({
                        'success': False,
                        'message': 'Acceso denegado'
                    }), 403
        
        employee_data = employee.to_dict(include_summary=True)
        
        # Añadir email del usuario asociado
        if employee.user:
            employee_data['email'] = employee.user.email
        
        # Mapear hours_summary a monthly_stats y annual_stats para compatibilidad con frontend
        from datetime import datetime
        now = datetime.utcnow()
        current_year = now.year
        current_month = now.month
        
        # Calcular estadísticas mensuales para el mes actual
        monthly_summary = employee.get_hours_summary(current_year, current_month)
        employee_data['monthly_stats'] = {
            'theoretical_hours': monthly_summary.get('theoretical_hours', 0),
            'actual_hours': monthly_summary.get('actual_hours', 0),
            'efficiency': monthly_summary.get('efficiency', 0)
        }
        
        # Calcular estadísticas anuales
        annual_summary = employee.get_hours_summary(current_year)
        remaining_benefits = employee.get_remaining_benefits(current_year)
        
        employee_data['annual_stats'] = {
            'total_actual_hours': annual_summary.get('actual_hours', 0),
            'total_efficiency': annual_summary.get('efficiency', 0),
            'remaining_vacation_days': remaining_benefits.get('remaining_vacation_days', 0),
            'remaining_hld_hours': remaining_benefits.get('remaining_hld_hours', 0)
        }
        
        return jsonify({
            'success': True,
            'employee': employee_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo empleado {employee_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo empleado'
        }), 500

@employees_bp.route('/<int:employee_id>/approve', methods=['POST'])
@auth_required()
@manager_or_admin_required()
def approve_employee(employee_id):
    """Aprueba un empleado (solo managers y admins)"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        # Verificar permisos
        if not current_user.is_admin() and not current_user.can_manage_employee(employee):
            return jsonify({
                'success': False,
                'message': 'No tienes permisos para aprobar este empleado'
            }), 403
        
        if employee.approved:
            return jsonify({
                'success': False,
                'message': 'El empleado ya está aprobado'
            }), 409
        
        # Aprobar empleado
        employee.approved = True
        employee.approved_at = datetime.utcnow()
        
        # Cambiar rol del usuario a employee
        employee_role = Role.query.filter_by(name='employee').first()
        viewer_role = Role.query.filter_by(name='viewer').first()
        
        if employee_role and employee.user:
            # Remover rol viewer y añadir employee
            if viewer_role in employee.user.roles:
                employee.user.roles.remove(viewer_role)
            if employee_role not in employee.user.roles:
                employee.user.roles.append(employee_role)
        
        db.session.commit()
        
        # Notificar al empleado
        NotificationService.notify_employee_approved(employee, current_user)
        
        logger.info(f"Empleado {employee.full_name} aprobado por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Empleado aprobado exitosamente',
            'employee': employee.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error aprobando empleado {employee_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error aprobando empleado'
        }), 500

@employees_bp.route('/<int:employee_id>/deactivate', methods=['POST'])
@auth_required()
@admin_required()
def deactivate_employee(employee_id):
    """Desactiva un empleado (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden desactivar empleados'
            }), 403
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        employee.active = False
        employee.updated_at = datetime.utcnow()
        
        # También desactivar el usuario asociado
        if employee.user:
            employee.user.active = False
        
        db.session.commit()
        
        logger.info(f"Empleado {employee.full_name} desactivado por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Empleado desactivado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error desactivando empleado {employee_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error desactivando empleado'
        }), 500

@employees_bp.route('/<int:employee_id>/hourly-rate', methods=['PUT'])
@auth_required()
@admin_required()
def update_employee_hourly_rate(employee_id):
    """Actualiza la tarifa por hora de un empleado (solo admins)"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        data = request.get_json()
        hourly_rate = data.get('hourly_rate')
        
        # Validar que hourly_rate sea un número positivo o null
        if hourly_rate is not None:
            try:
                hourly_rate = float(hourly_rate)
                if hourly_rate < 0:
                    return jsonify({
                        'success': False,
                        'message': 'La tarifa debe ser un número positivo'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'La tarifa debe ser un número válido'
                }), 400
        
        employee.hourly_rate = hourly_rate
        employee.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'employee': employee.to_dict(),
            'message': 'Tarifa actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando tarifa del empleado {employee_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando tarifa'
        }), 500

@employees_bp.route('/<int:employee_id>/change-team', methods=['PUT'])
@auth_required()
@admin_required()
def change_employee_team(employee_id):
    """Cambia el equipo de un empleado (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden cambiar el equipo de un empleado'
            }), 403
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        data = request.get_json()
        
        if not data or 'team_id' not in data:
            return jsonify({
                'success': False,
                'message': 'ID del equipo es requerido'
            }), 400
        
        team_id = data['team_id']
        team = Team.query.get(team_id)
        
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        old_team_id = employee.team_id
        employee.team_id = team_id
        employee.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Empleado {employee.full_name} movido del equipo {old_team_id} al equipo {team_id} por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': f'Empleado movido al equipo {team.name} exitosamente',
            'employee': employee.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cambiando equipo del empleado {employee_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error cambiando equipo del empleado'
        }), 500

@employees_bp.route('/pending-approval', methods=['GET'])
@auth_required()
@manager_or_admin_required()
def get_pending_approvals():
    """Obtiene empleados pendientes de aprobación (solo managers y admins)"""
    try:
        # Solo managers y admins pueden ver pendientes
        if not (current_user.is_admin() or current_user.is_manager()):
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        query = Employee.query.filter(
            Employee.active == True,
            Employee.approved == False
        )
        
        # Si es manager, solo ver pendientes de sus equipos
        if current_user.is_manager() and not current_user.is_admin():
            managed_teams = current_user.get_managed_teams()
            team_ids = [team.id for team in managed_teams]
            query = query.filter(Employee.team_id.in_(team_ids))
        
        pending_employees = query.order_by(Employee.created_at.desc()).all()
        
        employees_data = []
        for employee in pending_employees:
            emp_data = employee.to_dict()
            if employee.team:
                emp_data['team_name'] = employee.team.name
            employees_data.append(emp_data)
        
        return jsonify({
            'success': True,
            'pending_employees': employees_data,
            'count': len(employees_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo empleados pendientes: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo empleados pendientes'
        }), 500


# ============================================================
# INVITACIONES DE EMPLEADOS
# ============================================================

@employees_bp.route('/invite', methods=['POST'])
@auth_required()
@manager_or_admin_required()
def invite_employee():
    """
    Invitar a un empleado por email
    Genera un token único y envía email de invitación
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email es requerido'}), 400
        
        email = data['email'].lower().strip()
        
        # Validar formato de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Email inválido'}), 400
        
        # Verificar si el email ya existe como usuario
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Este email ya tiene una cuenta en el sistema'}), 409
        
        # Verificar si ya existe una invitación activa (no usada y no expirada)
        existing_invitation = EmployeeInvitation.query.filter_by(
            email=email,
            used=False
        ).filter(
            EmployeeInvitation.expires_at > datetime.utcnow()
        ).first()
        
        if existing_invitation:
            # Reenviar la invitación existente
            token = existing_invitation.token
            expires_at = existing_invitation.expires_at
        else:
            # Generar token único y seguro
            token = secrets.token_urlsafe(32)
            
            # La invitación expira en 7 días
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            # Crear nueva invitación
            invitation = EmployeeInvitation(
                email=email,
                token=token,
                invited_by=current_user.id,
                expires_at=expires_at
            )
            
            db.session.add(invitation)
            db.session.commit()
        
        # Enviar email de invitación
        frontend_url = request.headers.get('Origin', 'https://team-time-management.vercel.app')
        invitation_link = f"{frontend_url}/register?token={token}"
        
        logger.info(f"📧 Intentando enviar invitación a {email}")
        logger.info(f"📧 Link: {invitation_link}")
        logger.info(f"📧 Invitado por: {current_user.email}")
        
        try:
            email_sent = send_invitation_email(
                to_email=email,
                invitation_link=invitation_link,
                inviter_name=current_user.first_name or current_user.email,
                expires_days=7
            )
            
            if email_sent:
                logger.info(f"✅ Invitación enviada exitosamente a {email}")
                
                # Crear notificación para administradores sobre la invitación enviada
                from models.notification import NotificationType, NotificationPriority
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    admin_users = User.query.join(User.roles).filter(Role.id == admin_role.id).all()
                    for admin_user in admin_users:
                        notification = Notification(
                            user_id=admin_user.id,
                            title="Invitación enviada",
                            message=f"Se ha enviado una invitación a {email} para unirse al sistema.",
                            notification_type=NotificationType.SYSTEM_ALERT,
                            priority=NotificationPriority.LOW,
                            send_email=False,
                            created_by=current_user.id,
                            data={
                                'invitation_email': email,
                                'invited_by': current_user.email,
                                'expires_at': expires_at.isoformat()
                            }
                        )
                        db.session.add(notification)
                    
                    db.session.commit()
            else:
                logger.warning(f"⚠️ send_invitation_email devolvió False para {email}")
            
            return jsonify({
                'message': 'Invitación enviada exitosamente' if email_sent else 'Invitación creada pero el email falló',
                'email': email,
                'expires_at': expires_at.isoformat(),
                'invitation_link': invitation_link if request.headers.get('X-Debug') == 'true' else None,
                'email_sent': email_sent
            }), 201
            
        except Exception as email_error:
            logger.error(f"❌ Excepción enviando email de invitación: {email_error}")
            logger.exception(email_error)  # Log completo del stack trace
            # No fallar si el email no se envía, pero informar
            return jsonify({
                'message': 'Invitación creada pero hubo un error enviando el email',
                'email': email,
                'expires_at': expires_at.isoformat(),
                'invitation_link': invitation_link,
                'email_error': str(email_error)
            }), 201
    
    except Exception as e:
        logger.error(f"Error creando invitación: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500


@employees_bp.route('/invite/<token>', methods=['GET'])
def validate_invitation(token):
    """
    Validar un token de invitación
    No requiere autenticación (es para usuarios nuevos)
    """
    try:
        invitation = EmployeeInvitation.query.filter_by(token=token).first()
        
        if not invitation:
            return jsonify({'error': 'Invitación no encontrada'}), 404
        
        if invitation.used:
            return jsonify({'error': 'Esta invitación ya ha sido utilizada'}), 410
        
        if datetime.utcnow() > invitation.expires_at:
            return jsonify({'error': 'Esta invitación ha expirado'}), 410
        
        return jsonify({
            'valid': True,
            'email': invitation.email,
            'expires_at': invitation.expires_at.isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error validando invitación: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@employees_bp.route('/invite/<token>/use', methods=['POST'])
def mark_invitation_used(token):
    """
    Marcar una invitación como usada
    Llamado después de que el usuario complete su registro
    """
    try:
        invitation = EmployeeInvitation.query.filter_by(token=token).first()
        
        if not invitation:
            return jsonify({'error': 'Invitación no encontrada'}), 404
        
        if invitation.used:
            return jsonify({'error': 'Esta invitación ya ha sido utilizada'}), 410
        
        invitation.used = True
        invitation.used_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Invitación marcada como usada'}), 200
    
    except Exception as e:
        logger.error(f"Error marcando invitación como usada: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500
