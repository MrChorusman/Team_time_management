from flask import Blueprint, request, jsonify, current_app
from flask_security import auth_required, current_user
from datetime import datetime
import logging

from models.user import User, Role, db
from models.employee import Employee
from models.team import Team
from services.notification_service import NotificationService
from services.holiday_service import HolidayService

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
            'full_name', 'hours_monday_thursday', 'hours_friday',
            'annual_vacation_days', 'annual_hld_hours', 'country'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar si el usuario ya tiene un empleado registrado
        if current_user.employee:
            return jsonify({
                'success': False,
                'message': 'Ya tienes un perfil de empleado registrado'
            }), 409
        
        # Validar equipo si se proporciona
        team_id = data.get('team_id')
        if team_id:
            team = Team.query.get(team_id)
            if not team:
                return jsonify({
                    'success': False,
                    'message': 'Equipo no encontrado'
                }), 404
        
        # Crear empleado
        employee = Employee(
            user_id=current_user.id,
            full_name=data['full_name'].strip(),
            team_id=team_id,  # Puede ser None si no se asigna equipo todavía
            hours_monday_thursday=float(data['hours_monday_thursday']),
            hours_friday=float(data['hours_friday']),
            hours_summer=float(data.get('hours_summer', 0)) if data.get('hours_summer') else None,
            has_summer_schedule=bool(data.get('has_summer_schedule', False)),
            annual_vacation_days=int(data['annual_vacation_days']),
            annual_hld_hours=int(data['annual_hld_hours']),
            country=data['country'].strip(),
            region=data.get('region', '').strip() if data.get('region') else None,
            city=data.get('city', '').strip() if data.get('city') else None,
            active=True,
            approved=False  # Requiere aprobación del manager
        )
        
        # Configurar meses de verano si aplica
        if employee.has_summer_schedule and data.get('summer_months'):
            employee.summer_months_list = data['summer_months']
        
        db.session.add(employee)
        db.session.commit()
        
        # Cargar festivos automáticamente para la ubicación del empleado
        holiday_service = HolidayService()
        holidays_loaded, errors = holiday_service.load_holidays_for_employee_location(employee)
        
        if holidays_loaded > 0:
            logger.info(f"Cargados {holidays_loaded} festivos para {employee.country}")
        
        # Notificar al manager del equipo si hay equipo asignado
        if team_id and team:
            NotificationService.notify_employee_registration(employee, current_user)
            logger.info(f"Empleado registrado: {employee.full_name} en equipo {team.name}")
        else:
            logger.info(f"Empleado registrado: {employee.full_name} sin equipo asignado")
        
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
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        
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

@employees_bp.route('/pending-approval', methods=['GET'])
@auth_required()
def get_pending_approvals():
    """Obtiene empleados pendientes de aprobación"""
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
