from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from datetime import datetime, date
import logging

from models.calendar_activity import CalendarActivity
from models.employee import Employee
from models.team import Team
from models.user import db
from services.calendar_service import CalendarService

logger = logging.getLogger(__name__)

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/', methods=['GET'])
@auth_required()
def get_calendar():
    """Obtiene datos del calendario"""
    try:
        # Parámetros de consulta
        employee_id = request.args.get('employee_id', type=int)
        team_id = request.args.get('team_id', type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        view = request.args.get('view', 'monthly')  # monthly, annual
        
        # Verificar permisos
        if employee_id:
            employee = Employee.query.get(employee_id)
            if not employee:
                return jsonify({
                    'success': False,
                    'message': 'Empleado no encontrado'
                }), 404
            
            # Verificar si puede ver este empleado
            if not current_user.is_admin() and not current_user.can_manage_employee(employee):
                if not (current_user.employee and 
                       (current_user.employee.id == employee_id or 
                        current_user.employee.team_id == employee.team_id)):
                    return jsonify({
                        'success': False,
                        'message': 'Acceso denegado'
                    }), 403
        
        elif team_id:
            team = Team.query.get(team_id)
            if not team:
                return jsonify({
                    'success': False,
                    'message': 'Equipo no encontrado'
                }), 404
            
            # Verificar permisos para el equipo
            can_access = False
            if current_user.is_admin():
                can_access = True
            elif current_user.is_manager():
                managed_teams = current_user.get_managed_teams()
                can_access = team in managed_teams
            elif current_user.is_employee():
                can_access = current_user.employee and current_user.employee.team_id == team_id
            
            if not can_access:
                return jsonify({
                    'success': False,
                    'message': 'Acceso denegado'
                }), 403
        
        else:
            # Sin filtros específicos - usar empleado actual o su equipo
            if current_user.employee:
                if current_user.is_manager():
                    # Manager ve su equipo por defecto
                    team_id = current_user.employee.team_id
                else:
                    # Employee ve solo su calendario
                    employee_id = current_user.employee.id
            else:
                return jsonify({
                    'success': False,
                    'message': 'Debes especificar un empleado o equipo'
                }), 400
        
        # Obtener datos del calendario
        if view == 'annual':
            # Vista anual - obtener todos los meses
            calendar_data = {
                'view': 'annual',
                'year': year,
                'months': []
            }
            
            for month_num in range(1, 13):
                month_data = CalendarService.get_calendar_data(
                    employee_id=employee_id,
                    team_id=team_id,
                    year=year,
                    month=month_num
                )
                calendar_data['months'].append(month_data)
        
        else:
            # Vista mensual
            calendar_data = CalendarService.get_calendar_data(
                employee_id=employee_id,
                team_id=team_id,
                year=year,
                month=month
            )
            calendar_data['view'] = 'monthly'
        
        return jsonify({
            'success': True,
            'calendar': calendar_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo calendario: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo datos del calendario'
        }), 500

@calendar_bp.route('/activities', methods=['POST'])
@auth_required()
def create_activity():
    """Crea una nueva actividad en el calendario"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['employee_id', 'date', 'activity_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        employee_id = data['employee_id']
        activity_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        activity_type = data['activity_type']
        hours = data.get('hours')
        description = data.get('description', '')
        
        # Verificar que el empleado existe
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        # Verificar permisos
        can_create = False
        if current_user.is_admin():
            can_create = True
        elif current_user.can_manage_employee(employee):
            can_create = True
        elif current_user.employee and current_user.employee.id == employee_id:
            can_create = True
        
        if not can_create:
            return jsonify({
                'success': False,
                'message': 'No tienes permisos para crear actividades para este empleado'
            }), 403
        
        # Crear actividad
        success, message, activity = CalendarService.create_calendar_activity(
            employee_id=employee_id,
            activity_date=activity_date,
            activity_type=activity_type,
            hours=hours,
            description=description,
            created_by_user_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'activity': activity.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
        }), 400
    except Exception as e:
        logger.error(f"Error creando actividad: {e}")
        return jsonify({
            'success': False,
            'message': 'Error creando actividad'
        }), 500

@calendar_bp.route('/activities/<int:activity_id>', methods=['PUT'])
@auth_required()
def update_activity(activity_id):
    """Actualiza una actividad existente"""
    try:
        activity = CalendarActivity.query.get(activity_id)
        if not activity:
            return jsonify({
                'success': False,
                'message': 'Actividad no encontrada'
            }), 404
        
        # Verificar permisos
        can_update = False
        if current_user.is_admin():
            can_update = True
        elif current_user.can_manage_employee(activity.employee):
            can_update = True
        elif current_user.employee and current_user.employee.id == activity.employee_id:
            can_update = True
        
        if not can_update:
            return jsonify({
                'success': False,
                'message': 'No tienes permisos para actualizar esta actividad'
            }), 403
        
        data = request.get_json()
        
        # Actualizar actividad
        success, message, updated_activity = CalendarService.update_calendar_activity(
            activity_id=activity_id,
            activity_type=data.get('activity_type'),
            hours=data.get('hours'),
            description=data.get('description'),
            updated_by_user_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'activity': updated_activity.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
    except Exception as e:
        logger.error(f"Error actualizando actividad {activity_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando actividad'
        }), 500

@calendar_bp.route('/activities/<int:activity_id>', methods=['DELETE'])
@auth_required()
def delete_activity(activity_id):
    """Elimina una actividad"""
    try:
        activity = CalendarActivity.query.get(activity_id)
        if not activity:
            return jsonify({
                'success': False,
                'message': 'Actividad no encontrada'
            }), 404
        
        # Verificar permisos
        can_delete = False
        if current_user.is_admin():
            can_delete = True
        elif current_user.can_manage_employee(activity.employee):
            can_delete = True
        elif current_user.employee and current_user.employee.id == activity.employee_id:
            can_delete = True
        
        if not can_delete:
            return jsonify({
                'success': False,
                'message': 'No tienes permisos para eliminar esta actividad'
            }), 403
        
        # Eliminar actividad
        success, message = CalendarService.delete_calendar_activity(
            activity_id=activity_id,
            deleted_by_user_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
    except Exception as e:
        logger.error(f"Error eliminando actividad {activity_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error eliminando actividad'
        }), 500

@calendar_bp.route('/activity-types', methods=['GET'])
@auth_required()
def get_activity_types():
    """Obtiene los tipos de actividad disponibles"""
    try:
        activity_types = CalendarActivity.get_activity_types()
        
        return jsonify({
            'success': True,
            'activity_types': activity_types
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo tipos de actividad: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo tipos de actividad'
        }), 500

@calendar_bp.route('/conflicts', methods=['GET'])
@auth_required()
def get_calendar_conflicts():
    """Obtiene conflictos de calendario para un equipo"""
    try:
        team_id = request.args.get('team_id', type=int)
        days_ahead = request.args.get('days_ahead', 30, type=int)
        
        if not team_id:
            return jsonify({
                'success': False,
                'message': 'ID del equipo es requerido'
            }), 400
        
        # Verificar permisos para el equipo
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        can_access = False
        if current_user.is_admin():
            can_access = True
        elif current_user.is_manager():
            managed_teams = current_user.get_managed_teams()
            can_access = team in managed_teams
        
        if not can_access:
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        # Obtener conflictos
        conflicts = CalendarService.get_team_calendar_conflicts(
            team_id=team_id,
            end_date=date.today() + datetime.timedelta(days=days_ahead)
        )
        
        return jsonify({
            'success': True,
            'conflicts': conflicts,
            'team_id': team_id,
            'days_ahead': days_ahead
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo conflictos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo conflictos'
        }), 500

@calendar_bp.route('/upcoming', methods=['GET'])
@auth_required()
def get_upcoming_activities():
    """Obtiene actividades próximas"""
    try:
        employee_id = request.args.get('employee_id', type=int)
        team_id = request.args.get('team_id', type=int)
        days_ahead = request.args.get('days_ahead', 10, type=int)
        
        # Verificar permisos
        if employee_id:
            employee = Employee.query.get(employee_id)
            if not employee:
                return jsonify({
                    'success': False,
                    'message': 'Empleado no encontrado'
                }), 404
            
            if not current_user.is_admin() and not current_user.can_manage_employee(employee):
                if not (current_user.employee and current_user.employee.id == employee_id):
                    return jsonify({
                        'success': False,
                        'message': 'Acceso denegado'
                    }), 403
        
        elif team_id:
            team = Team.query.get(team_id)
            if not team:
                return jsonify({
                    'success': False,
                    'message': 'Equipo no encontrado'
                }), 404
            
            can_access = False
            if current_user.is_admin():
                can_access = True
            elif current_user.is_manager():
                managed_teams = current_user.get_managed_teams()
                can_access = team in managed_teams
            elif current_user.is_employee():
                can_access = current_user.employee and current_user.employee.team_id == team_id
            
            if not can_access:
                return jsonify({
                    'success': False,
                    'message': 'Acceso denegado'
                }), 403
        
        else:
            # Sin filtros - usar empleado actual
            if current_user.employee:
                employee_id = current_user.employee.id
            else:
                return jsonify({
                    'success': False,
                    'message': 'Debes especificar un empleado o equipo'
                }), 400
        
        # Obtener actividades próximas
        upcoming_activities = CalendarService.get_upcoming_activities(
            employee_id=employee_id,
            team_id=team_id,
            days_ahead=days_ahead
        )
        
        return jsonify({
            'success': True,
            'upcoming_activities': upcoming_activities,
            'days_ahead': days_ahead
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo actividades próximas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo actividades próximas'
        }), 500

@calendar_bp.route('/my-calendar', methods=['GET'])
@auth_required()
def get_my_calendar():
    """Obtiene el calendario del usuario actual"""
    try:
        if not current_user.employee:
            return jsonify({
                'success': False,
                'message': 'No tienes un perfil de empleado registrado'
            }), 404
        
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        view = request.args.get('view', 'monthly')
        
        # Obtener datos del calendario personal
        if view == 'annual':
            calendar_data = {
                'view': 'annual',
                'year': year,
                'months': []
            }
            
            for month_num in range(1, 13):
                month_data = CalendarService.get_calendar_data(
                    employee_id=current_user.employee.id,
                    year=year,
                    month=month_num
                )
                calendar_data['months'].append(month_data)
        else:
            calendar_data = CalendarService.get_calendar_data(
                employee_id=current_user.employee.id,
                year=year,
                month=month
            )
            calendar_data['view'] = 'monthly'
        
        return jsonify({
            'success': True,
            'calendar': calendar_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo calendario personal: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo calendario personal'
        }), 500

@calendar_bp.route('/team-calendar', methods=['GET'])
@auth_required()
def get_team_calendar():
    """Obtiene el calendario del equipo del usuario actual"""
    try:
        if not current_user.employee or not current_user.employee.team_id:
            return jsonify({
                'success': False,
                'message': 'No perteneces a ningún equipo'
            }), 404
        
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        view = request.args.get('view', 'monthly')
        
        # Obtener datos del calendario del equipo
        if view == 'annual':
            calendar_data = {
                'view': 'annual',
                'year': year,
                'months': []
            }
            
            for month_num in range(1, 13):
                month_data = CalendarService.get_calendar_data(
                    team_id=current_user.employee.team_id,
                    year=year,
                    month=month_num
                )
                calendar_data['months'].append(month_data)
        else:
            calendar_data = CalendarService.get_calendar_data(
                team_id=current_user.employee.team_id,
                year=year,
                month=month
            )
            calendar_data['view'] = 'monthly'
        
        return jsonify({
            'success': True,
            'calendar': calendar_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo calendario del equipo: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo calendario del equipo'
        }), 500
