from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from datetime import datetime
import logging

from models.employee import Employee
from models.team import Team
from models.company import Company
from services.forecast_calculator import ForecastCalculator
from utils.decorators import admin_required, manager_or_admin_required

logger = logging.getLogger(__name__)

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/', methods=['GET'])
@auth_required()
def get_forecast():
    """
    Obtiene el forecast según los filtros proporcionados.
    
    Query params:
    - employee_id: ID del empleado (opcional)
    - team_id: ID del equipo (opcional)
    - company_id: ID de la empresa (requerido)
    - year: Año (opcional, por defecto año actual)
    - month: Mes (opcional, por defecto mes actual)
    - view: Tipo de vista ('employee', 'team', 'global') (opcional, por defecto 'employee')
    """
    try:
        # Obtener parámetros
        employee_id = request.args.get('employee_id', type=int)
        team_id = request.args.get('team_id', type=int)
        company_id = request.args.get('company_id', type=int)
        year = request.args.get('year', type=int) or datetime.now().year
        month = request.args.get('month', type=int) or datetime.now().month
        view = request.args.get('view', 'employee')  # 'employee', 'team', 'global'
        
        # Validar que se proporcione company_id
        if not company_id:
            return jsonify({
                'success': False,
                'message': 'company_id es requerido'
            }), 400
        
        # Obtener empresa
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'message': 'Empresa no encontrada'
            }), 404
        
        if not company.active:
            return jsonify({
                'success': False,
                'message': 'Empresa inactiva'
            }), 400
        
        # Verificar permisos según el tipo de vista
        if view == 'employee':
            if not employee_id:
                return jsonify({
                    'success': False,
                    'message': 'employee_id es requerido para vista de empleado'
                }), 400
            
            employee = Employee.query.get(employee_id)
            if not employee:
                return jsonify({
                    'success': False,
                    'message': 'Empleado no encontrado'
                }), 404
            
            # Verificar permisos: admin, manager del equipo, o el propio empleado
            if not current_user.is_admin():
                if current_user.is_manager():
                    # Manager solo puede ver empleados de sus equipos
                    managed_teams = current_user.get_managed_teams()
                    if employee.team_id not in [team.id for team in managed_teams]:
                        return jsonify({
                            'success': False,
                            'message': 'Acceso denegado'
                        }), 403
                elif current_user.is_employee():
                    # Empleado solo puede ver su propio forecast
                    if current_user.employee.id != employee_id:
                        return jsonify({
                            'success': False,
                            'message': 'Acceso denegado'
                        }), 403
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Acceso denegado'
                    }), 403
            
            forecast_data = ForecastCalculator.calculate_forecast_for_employee(
                employee, company, year, month
            )
            
        elif view == 'team':
            if not team_id:
                return jsonify({
                    'success': False,
                    'message': 'team_id es requerido para vista de equipo'
                }), 400
            
            team = Team.query.get(team_id)
            if not team:
                return jsonify({
                    'success': False,
                    'message': 'Equipo no encontrado'
                }), 404
            
            # Verificar permisos: admin o manager del equipo
            if not current_user.is_admin():
                if current_user.is_manager():
                    managed_teams = current_user.get_managed_teams()
                    if team_id not in [team.id for team in managed_teams]:
                        return jsonify({
                            'success': False,
                            'message': 'Acceso denegado'
                        }), 403
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Acceso denegado'
                    }), 403
            
            forecast_data = ForecastCalculator.calculate_forecast_for_team(
                team, company, year, month
            )
            
        elif view == 'global':
            # Solo admin puede ver vista global
            if not current_user.is_admin():
                return jsonify({
                    'success': False,
                    'message': 'Acceso denegado. Solo administradores pueden ver vista global'
                }), 403
            
            forecast_data = ForecastCalculator.calculate_forecast_global(
                company, year, month
            )
        else:
            return jsonify({
                'success': False,
                'message': f'Vista no válida: {view}. Valores permitidos: employee, team, global'
            }), 400
        
        return jsonify({
            'success': True,
            'forecast': forecast_data,
            'period': {
                'year': year,
                'month': month,
                'company_id': company_id,
                'company_name': company.name
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo forecast: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Error obteniendo forecast'
        }), 500

