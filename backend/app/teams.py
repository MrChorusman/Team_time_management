from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from datetime import datetime
import logging

from models.team import Team
from sqlalchemy.orm import load_only
from models.employee import Employee
from models.user import db
from services.hours_calculator import HoursCalculator

logger = logging.getLogger(__name__)

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/', methods=['GET'])
@auth_required()
def list_teams():
    """Lista todos los equipos"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        include_employees = request.args.get('include_employees', 'false').lower() == 'true'
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Construir query
        query = Team.query
        
        if active_only:
            query = query.filter(Team.active == True)
        
        # Filtros según permisos
        if current_user.is_manager() and not current_user.is_admin():
            # Manager solo puede ver sus equipos
            managed_teams = current_user.get_managed_teams()
            team_ids = [team.id for team in managed_teams]
            if current_user.employee and current_user.employee.team_id:
                team_ids.append(current_user.employee.team_id)
            query = query.filter(Team.id.in_(team_ids))
        elif current_user.is_employee() and not current_user.is_manager():
            # Employee solo puede ver su equipo
            if current_user.employee and current_user.employee.team_id:
                query = query.filter(Team.id == current_user.employee.team_id)
            else:
                query = query.filter(Team.id == -1)  # No mostrar nada
        
        # Reducir columnas para evitar tocar campos no existentes en despliegues desincronizados
        query = query.options(load_only(Team.id, Team.name, Team.active))

        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        teams_data = []
        for team in pagination.items:
            try:
                if include_employees:
                    team_data = team.to_dict(include_employees=True)
                else:
                    # Respuesta mínima y segura para combos
                    team_data = {
                        'id': team.id,
                        'name': team.name,
                        'active': team.active
                    }
                teams_data.append(team_data)
            except Exception as e:
                logger.exception(f"Error serializando equipo id={getattr(team, 'id', None)}: {e}")
                # Continuar con el resto de equipos sin romper la respuesta
                continue
        
        return jsonify({
            'success': True,
            'teams': teams_data,
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
        logger.error(f"Error listando equipos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo equipos'
        }), 500

@teams_bp.route('/', methods=['POST'])
@auth_required()
def create_team():
    """Crea un nuevo equipo (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden crear equipos'
            }), 403
        
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'El nombre del equipo es requerido'
            }), 400
        
        # Verificar que no exista un equipo con el mismo nombre
        existing_team = Team.query.filter_by(name=data['name'].strip()).first()
        if existing_team:
            return jsonify({
                'success': False,
                'message': 'Ya existe un equipo con ese nombre'
            }), 409
        
        # Crear equipo
        team = Team(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            manager_id=data.get('manager_id'),
            active=True
        )
        
        # Validar manager si se especifica
        if team.manager_id:
            manager_employee = Employee.query.get(team.manager_id)
            if not manager_employee:
                return jsonify({
                    'success': False,
                    'message': 'Manager especificado no encontrado'
                }), 404
        
        db.session.add(team)
        db.session.commit()
        
        logger.info(f"Equipo creado: {team.name} por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Equipo creado exitosamente',
            'team': team.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando equipo: {e}")
        return jsonify({
            'success': False,
            'message': 'Error creando equipo'
        }), 500

@teams_bp.route('/<int:team_id>', methods=['GET'])
@auth_required()
def get_team(team_id):
    """Obtiene un equipo específico"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        # Verificar permisos
        can_access = False
        if current_user.is_admin():
            can_access = True
        elif current_user.is_manager():
            managed_teams = current_user.get_managed_teams()
            can_access = team in managed_teams or (current_user.employee and current_user.employee.team_id == team_id)
        elif current_user.is_employee():
            can_access = current_user.employee and current_user.employee.team_id == team_id
        
        if not can_access:
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        include_employees = request.args.get('include_employees', 'true').lower() == 'true'
        team_data = team.to_dict(include_employees=include_employees)
        
        return jsonify({
            'success': True,
            'team': team_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo equipo {team_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo equipo'
        }), 500

@teams_bp.route('/<int:team_id>', methods=['PUT'])
@auth_required()
def update_team(team_id):
    """Actualiza un equipo (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden actualizar equipos'
            }), 403
        
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'name' in data:
            # Verificar que no exista otro equipo con el mismo nombre
            existing_team = Team.query.filter(
                Team.name == data['name'].strip(),
                Team.id != team_id
            ).first()
            if existing_team:
                return jsonify({
                    'success': False,
                    'message': 'Ya existe otro equipo con ese nombre'
                }), 409
            team.name = data['name'].strip()
        
        if 'description' in data:
            team.description = data['description'].strip()
        
        if 'manager_id' in data:
            if data['manager_id']:
                manager_employee = Employee.query.get(data['manager_id'])
                if not manager_employee:
                    return jsonify({
                        'success': False,
                        'message': 'Manager especificado no encontrado'
                    }), 404
            team.manager_id = data['manager_id']
        
        if 'active' in data:
            team.active = bool(data['active'])
        
        team.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Equipo {team.name} actualizado por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Equipo actualizado exitosamente',
            'team': team.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando equipo {team_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando equipo'
        }), 500

@teams_bp.route('/<int:team_id>/summary', methods=['GET'])
@auth_required()
def get_team_summary(team_id):
    """Obtiene resumen de horas y eficiencia del equipo"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        # Verificar permisos
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
        
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', type=int)
        
        # Calcular resumen del equipo
        team_summary = HoursCalculator.calculate_team_efficiency(team, year, month)
        
        return jsonify({
            'success': True,
            'team_summary': team_summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen del equipo {team_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo resumen del equipo'
        }), 500

@teams_bp.route('/<int:team_id>/employees', methods=['GET'])
@auth_required()
def get_team_employees(team_id):
    """Obtiene empleados de un equipo específico"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        # Verificar permisos
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
        
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        include_summary = request.args.get('include_summary', 'false').lower() == 'true'
        
        # Obtener empleados
        query = Employee.query.filter(
            Employee.team_id == team_id,
            Employee.active == True
        )
        
        if approved_only:
            query = query.filter(Employee.approved == True)
        
        employees = query.order_by(Employee.full_name).all()
        
        employees_data = []
        for employee in employees:
            emp_data = employee.to_dict(include_summary=include_summary)
            employees_data.append(emp_data)
        
        return jsonify({
            'success': True,
            'team': team.to_dict(),
            'employees': employees_data,
            'count': len(employees_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo empleados del equipo {team_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo empleados del equipo'
        }), 500

@teams_bp.route('/<int:team_id>/assign-manager', methods=['POST'])
@auth_required()
def assign_manager(team_id):
    """Asigna un manager a un equipo (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden asignar managers'
            }), 403
        
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        data = request.get_json()
        
        if not data or 'employee_id' not in data:
            return jsonify({
                'success': False,
                'message': 'ID del empleado es requerido'
            }), 400
        
        employee_id = data['employee_id']
        
        # Verificar que el empleado existe y está aprobado
        employee = Employee.query.get(employee_id)
        if not employee or not employee.approved or not employee.active:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado o no está aprobado'
            }), 404
        
        # Asignar manager
        old_manager_id = team.manager_id
        team.manager_id = employee_id
        team.updated_at = datetime.utcnow()
        
        # Asignar rol de manager al usuario del empleado
        manager_role = Role.query.filter_by(name='manager').first()
        if manager_role and employee.user and manager_role not in employee.user.roles:
            employee.user.roles.append(manager_role)
        
        db.session.commit()
        
        logger.info(f"Manager asignado al equipo {team.name}: {employee.full_name}")
        
        return jsonify({
            'success': True,
            'message': 'Manager asignado exitosamente',
            'team': team.to_dict(),
            'old_manager_id': old_manager_id,
            'new_manager_id': employee_id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error asignando manager al equipo {team_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error asignando manager'
        }), 500

@teams_bp.route('/available-managers', methods=['GET'])
@auth_required()
def get_available_managers():
    """Obtiene empleados que pueden ser managers (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        # Obtener empleados aprobados y activos
        employees = Employee.query.filter(
            Employee.approved == True,
            Employee.active == True
        ).order_by(Employee.full_name).all()
        
        available_managers = []
        for employee in employees:
            emp_data = {
                'id': employee.id,
                'full_name': employee.full_name,
                'team_id': employee.team_id,
                'team_name': employee.team.name if employee.team else None,
                'is_current_manager': bool(employee.team and employee.team.manager_id == employee.id),
                'manages_teams': [team.name for team in Team.query.filter_by(manager_id=employee.id).all()]
            }
            available_managers.append(emp_data)
        
        return jsonify({
            'success': True,
            'available_managers': available_managers
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo managers disponibles: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo managers disponibles'
        }), 500

@teams_bp.route('/my-teams', methods=['GET'])
@auth_required()
def get_my_teams():
    """Obtiene los equipos que gestiona el usuario actual"""
    try:
        if not current_user.is_manager():
            return jsonify({
                'success': False,
                'message': 'Solo los managers pueden acceder a esta información'
            }), 403
        
        managed_teams = current_user.get_managed_teams()
        
        teams_data = []
        for team in managed_teams:
            team_data = team.to_dict(include_employees=True)
            # Añadir resumen del equipo
            team_summary = HoursCalculator.calculate_team_efficiency(team)
            team_data['summary'] = team_summary
            teams_data.append(team_data)
        
        return jsonify({
            'success': True,
            'managed_teams': teams_data,
            'count': len(teams_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo equipos gestionados: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo equipos gestionados'
        }), 500
