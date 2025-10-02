from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from datetime import datetime, date
import logging

from models.holiday import Holiday
from models.employee import Employee
from models.user import db
from services.holiday_service import HolidayService

logger = logging.getLogger(__name__)

holidays_bp = Blueprint('holidays', __name__)

@holidays_bp.route('/', methods=['GET'])
@auth_required()
def list_holidays():
    """Lista festivos con filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        country = request.args.get('country')
        region = request.args.get('region')
        year = request.args.get('year', type=int)
        
        # Construir query
        query = Holiday.query.filter(Holiday.active == True)
        
        # Filtros
        if country:
            query = query.filter(Holiday.country == country)
        
        if region:
            query = query.filter(Holiday.region == region)
        
        if year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            query = query.filter(Holiday.date >= start_date, Holiday.date <= end_date)
        
        # Ordenar por fecha
        query = query.order_by(Holiday.date.desc())
        
        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        holidays_data = [holiday.to_dict() for holiday in pagination.items]
        
        return jsonify({
            'success': True,
            'holidays': holidays_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'country': country,
                'region': region,
                'year': year
            }
        })
        
    except Exception as e:
        logger.error(f"Error listando festivos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo festivos'
        }), 500

@holidays_bp.route('/my-holidays', methods=['GET'])
@auth_required()
def get_my_holidays():
    """Obtiene festivos aplicables para el empleado actual"""
    try:
        if not current_user.employee:
            return jsonify({
                'success': False,
                'message': 'No tienes un perfil de empleado registrado'
            }), 404
        
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Obtener festivos para la ubicación del empleado
        holiday_service = HolidayService()
        holidays = holiday_service.get_holidays_for_employee(current_user.employee, year)
        
        holidays_data = [holiday.to_dict() for holiday in holidays]
        
        # Agrupar por tipo jerárquico
        grouped_holidays = {
            'national': [],
            'regional': [],
            'local': []
        }
        
        for holiday_data in holidays_data:
            level = holiday_data['hierarchy_level']
            grouped_holidays[level].append(holiday_data)
        
        return jsonify({
            'success': True,
            'holidays': holidays_data,
            'grouped_holidays': grouped_holidays,
            'employee_location': {
                'country': current_user.employee.country,
                'region': current_user.employee.region,
                'city': current_user.employee.city
            },
            'year': year,
            'total_count': len(holidays_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo festivos del empleado: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo tus festivos'
        }), 500

@holidays_bp.route('/countries', methods=['GET'])
@auth_required()
def get_countries():
    """Obtiene lista de países con festivos"""
    try:
        # Obtener países con festivos cargados
        countries_with_holidays = Holiday.get_countries_with_holidays()
        
        # Obtener países soportados por la API
        holiday_service = HolidayService()
        supported_countries = holiday_service.SUPPORTED_COUNTRIES
        
        countries_data = []
        for country_tuple in countries_with_holidays:
            country_name = country_tuple[0]
            
            # Contar festivos
            holiday_count = Holiday.query.filter(
                Holiday.country == country_name,
                Holiday.active == True
            ).count()
            
            countries_data.append({
                'name': country_name,
                'holiday_count': holiday_count,
                'supported': country_name in supported_countries.values()
            })
        
        # Añadir países soportados sin festivos
        loaded_countries = [c['name'] for c in countries_data]
        for code, name in supported_countries.items():
            if name not in loaded_countries:
                countries_data.append({
                    'name': name,
                    'code': code,
                    'holiday_count': 0,
                    'supported': True,
                    'can_load': True
                })
        
        return jsonify({
            'success': True,
            'countries': sorted(countries_data, key=lambda x: x['name']),
            'total_supported': len(supported_countries),
            'total_with_holidays': len(countries_with_holidays)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo países: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo países'
        }), 500

@holidays_bp.route('/regions/<country>', methods=['GET'])
@auth_required()
def get_regions(country):
    """Obtiene regiones para un país específico"""
    try:
        regions = Holiday.get_regions_for_country(country)
        
        regions_data = []
        for region_tuple in regions:
            region_name = region_tuple[0]
            
            # Contar festivos regionales
            holiday_count = Holiday.query.filter(
                Holiday.country == country,
                Holiday.region == region_name,
                Holiday.active == True
            ).count()
            
            regions_data.append({
                'name': region_name,
                'holiday_count': holiday_count
            })
        
        return jsonify({
            'success': True,
            'country': country,
            'regions': sorted(regions_data, key=lambda x: x['name']),
            'total_regions': len(regions_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo regiones para {country}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo regiones'
        }), 500

@holidays_bp.route('/load', methods=['POST'])
@auth_required()
def load_holidays():
    """Carga festivos para un país específico (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden cargar festivos'
            }), 403
        
        data = request.get_json()
        
        if not data or not data.get('country_code'):
            return jsonify({
                'success': False,
                'message': 'Código de país es requerido'
            }), 400
        
        country_code = data['country_code']
        year = data.get('year', datetime.now().year)
        
        # Cargar festivos
        holiday_service = HolidayService()
        created_count, errors = holiday_service.load_holidays_for_country(country_code, year)
        
        return jsonify({
            'success': True,
            'message': f'Cargados {created_count} festivos para {country_code} ({year})',
            'holidays_loaded': created_count,
            'year': year,
            'country_code': country_code,
            'errors': errors[:5] if errors else []  # Solo mostrar primeros 5 errores
        })
        
    except Exception as e:
        logger.error(f"Error cargando festivos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error cargando festivos'
        }), 500

@holidays_bp.route('/auto-load', methods=['POST'])
@auth_required()
def auto_load_holidays():
    """Carga automáticamente festivos para países sin festivos (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden cargar festivos automáticamente'
            }), 403
        
        holiday_service = HolidayService()
        results = holiday_service.auto_load_missing_holidays()
        
        return jsonify({
            'success': True,
            'message': f'Proceso completado. {results["total_holidays_loaded"]} festivos cargados.',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error en carga automática de festivos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error en carga automática'
        }), 500

@holidays_bp.route('/summary', methods=['GET'])
@auth_required()
def get_holidays_summary():
    """Obtiene resumen estadístico de festivos"""
    try:
        holiday_service = HolidayService()
        summary = holiday_service.get_holidays_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de festivos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo resumen'
        }), 500

@holidays_bp.route('/refresh/<int:year>', methods=['POST'])
@auth_required()
def refresh_holidays_for_year(year):
    """Actualiza festivos para un año específico (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden actualizar festivos'
            }), 403
        
        if year < 2020 or year > 2030:
            return jsonify({
                'success': False,
                'message': 'Año debe estar entre 2020 y 2030'
            }), 400
        
        holiday_service = HolidayService()
        results = holiday_service.refresh_holidays_for_year(year)
        
        return jsonify({
            'success': True,
            'message': f'Festivos actualizados para {year}',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error actualizando festivos para {year}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando festivos'
        }), 500

@holidays_bp.route('/<int:holiday_id>', methods=['GET'])
@auth_required()
def get_holiday(holiday_id):
    """Obtiene un festivo específico"""
    try:
        holiday = Holiday.query.get(holiday_id)
        if not holiday:
            return jsonify({
                'success': False,
                'message': 'Festivo no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'holiday': holiday.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo festivo {holiday_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo festivo'
        }), 500

@holidays_bp.route('/<int:holiday_id>/toggle', methods=['POST'])
@auth_required()
def toggle_holiday(holiday_id):
    """Activa/desactiva un festivo (solo admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden modificar festivos'
            }), 403
        
        holiday = Holiday.query.get(holiday_id)
        if not holiday:
            return jsonify({
                'success': False,
                'message': 'Festivo no encontrado'
            }), 404
        
        holiday.active = not holiday.active
        holiday.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        status = 'activado' if holiday.active else 'desactivado'
        logger.info(f"Festivo {holiday.name} {status} por {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': f'Festivo {status} exitosamente',
            'holiday': holiday.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error modificando festivo {holiday_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error modificando festivo'
        }), 500

@holidays_bp.route('/check-date', methods=['POST'])
@auth_required()
def check_holiday_date():
    """Verifica si una fecha es festivo para un empleado"""
    try:
        data = request.get_json()
        
        if not data or not data.get('date'):
            return jsonify({
                'success': False,
                'message': 'Fecha es requerida'
            }), 400
        
        check_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        employee_id = data.get('employee_id')
        
        # Si no se especifica empleado, usar el actual
        if employee_id:
            if not current_user.is_admin() and not current_user.can_manage_employee(Employee.query.get(employee_id)):
                employee = current_user.employee
            else:
                employee = Employee.query.get(employee_id)
        else:
            employee = current_user.employee
        
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        # Verificar si es festivo
        holidays = Holiday.get_holidays_for_date(
            check_date, employee.country, employee.region, employee.city
        )
        
        is_holiday = len(holidays) > 0
        
        return jsonify({
            'success': True,
            'date': check_date.isoformat(),
            'is_holiday': is_holiday,
            'holidays': [holiday.to_dict() for holiday in holidays],
            'employee_location': {
                'country': employee.country,
                'region': employee.region,
                'city': employee.city
            }
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
        }), 400
    except Exception as e:
        logger.error(f"Error verificando fecha festiva: {e}")
        return jsonify({
            'success': False,
            'message': 'Error verificando fecha'
        }), 500
