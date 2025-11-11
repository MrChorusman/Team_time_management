"""
Dashboard Blueprint
Endpoint centralizado para estadísticas del dashboard según rol de usuario
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from models.base import db
from models.user import User
from models.employee import Employee
from models.team import Team
from models.notification import Notification

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """
    Obtiene estadísticas del dashboard según el rol del usuario
    
    Returns:
        - Admin: Estadísticas globales del sistema
        - Manager: Estadísticas de su equipo
        - Employee: Estadísticas personales
    """
    try:
        user = current_user
        
        # Verificar roles del usuario
        user_roles = [role.name for role in user.roles]
        is_admin = 'admin' in user_roles
        is_manager = 'manager' in user_roles
        
        # Obtener el empleado asociado al usuario
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        # ADMIN: Estadísticas globales
        if is_admin:
            return jsonify(_get_admin_stats()), 200
        
        # MANAGER: Estadísticas del equipo
        if is_manager and employee and employee.team_id:
            return jsonify(_get_manager_stats(employee.team_id)), 200
        
        # EMPLOYEE: Estadísticas personales
        if employee:
            return jsonify(_get_employee_stats(employee.id)), 200
        
        # Usuario sin empleado (probablemente admin nuevo)
        return jsonify({
            'type': 'viewer',
            'statistics': {
                'message': 'Complete su perfil de empleado para ver estadísticas'
            },
            'recent_activity': [],
            'alerts': []
        }), 200
        
    except Exception as e:
        print(f"Error obteniendo estadísticas del dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500


def _get_admin_stats():
    """Estadísticas para administradores"""
    try:
        # Total de empleados
        total_employees = Employee.query.count()
        
        # Total de equipos
        total_teams = Team.query.count()
        
        # Aprobaciones pendientes
        pending_approvals = Employee.query.filter_by(approved='pending').count()
        
        # Eficiencia global (promedio de empleados aprobados con horas registradas)
        approved_employees = Employee.query.filter_by(approved='approved').all()
        
        if approved_employees:
            # Calcular eficiencia basada en horas teóricas vs reales
            # Por ahora, si no hay datos de horas, retornar 0
            global_efficiency = 0
        else:
            global_efficiency = 0
        
        # Actividad reciente (últimas notificaciones del sistema)
        recent_notifications = Notification.query\
            .order_by(Notification.created_at.desc())\
            .limit(5)\
            .all()
        
        recent_activity = [{
            'type': notif.type,
            'message': notif.message,
            'timestamp': notif.created_at.isoformat() if notif.created_at else None
        } for notif in recent_notifications]
        
        # Rendimiento por equipos
        teams = Team.query.all()
        team_performance = []
        
        for team in teams:
            team_employees = Employee.query.filter_by(
                team_id=team.id,
                approved='approved'
            ).count()
            
            team_performance.append({
                'team_id': team.id,
                'team_name': team.name,
                'members_count': team_employees,
                'efficiency': 0  # TODO: Calcular cuando tengamos datos de horas
            })
        
        # Alertas
        alerts = []
        if pending_approvals > 0:
            alerts.append({
                'type': 'warning',
                'message': f'Hay {pending_approvals} empleado(s) pendiente(s) de aprobación',
                'action': 'review_employees'
            })
        
        if total_teams == 0:
            alerts.append({
                'type': 'info',
                'message': 'No hay equipos creados. Crea el primer equipo.',
                'action': 'create_team'
            })
        
        return {
            'type': 'admin',
            'statistics': {
                'total_employees': total_employees,
                'total_teams': total_teams,
                'pending_approvals': pending_approvals,
                'global_efficiency': global_efficiency
            },
            'recent_activity': recent_activity,
            'team_performance': team_performance,
            'alerts': alerts
        }
        
    except Exception as e:
        print(f"Error en _get_admin_stats: {e}")
        raise


def _get_manager_stats(team_id):
    """Estadísticas para managers"""
    try:
        # Miembros del equipo
        team_members = Employee.query.filter_by(
            team_id=team_id,
            approved='approved'
        ).count()
        
        # Aprobaciones pendientes en el equipo
        pending_approvals = Employee.query.filter_by(
            team_id=team_id,
            approved='pending'
        ).count()
        
        # Eficiencia del equipo
        team_efficiency = 0  # TODO: Calcular cuando tengamos datos
        
        # Proyectos (placeholder)
        projects = 0
        
        # Actividad reciente del equipo
        team_employees = Employee.query.filter_by(team_id=team_id).all()
        employee_ids = [emp.id for emp in team_employees]
        
        recent_notifications = Notification.query\
            .filter(Notification.user_id.in_([emp.user_id for emp in team_employees]))\
            .order_by(Notification.created_at.desc())\
            .limit(5)\
            .all()
        
        recent_activity = [{
            'type': notif.type,
            'message': notif.message,
            'timestamp': notif.created_at.isoformat() if notif.created_at else None
        } for notif in recent_notifications]
        
        # Alertas
        alerts = []
        if pending_approvals > 0:
            alerts.append({
                'type': 'warning',
                'message': f'Hay {pending_approvals} empleado(s) de tu equipo pendiente(s) de aprobación',
                'action': 'review_team_employees'
            })
        
        return {
            'type': 'manager',
            'statistics': {
                'team_members': team_members,
                'pending_approvals': pending_approvals,
                'team_efficiency': team_efficiency,
                'projects': projects
            },
            'team_stats': {
                'members': team_members,
                'efficiency': team_efficiency
            },
            'recent_activity': recent_activity,
            'alerts': alerts
        }
        
    except Exception as e:
        print(f"Error en _get_manager_stats: {e}")
        raise


def _get_employee_stats(employee_id):
    """Estadísticas para empleados"""
    try:
        employee = Employee.query.get(employee_id)
        
        if not employee:
            raise ValueError(f"Empleado {employee_id} no encontrado")
        
        # Horas del mes (placeholder - TODO: implementar cuando tengamos registro de horas)
        hours_this_month = 0
        
        # Eficiencia
        efficiency = 0
        
        # Días de vacaciones restantes
        vacation_days_left = employee.vacation_days or 22
        
        # Horas de libre disposición restantes
        hld_hours_left = employee.hld_hours or 40
        
        # Resumen mensual
        monthly_summary = {
            'theoretical_hours': 160,  # Aproximado
            'actual_hours': 0,
            'efficiency': 0,
            'days_worked': 0
        }
        
        # Actividad reciente
        recent_notifications = Notification.query\
            .filter_by(user_id=employee.user_id)\
            .order_by(Notification.created_at.desc())\
            .limit(5)\
            .all()
        
        recent_activity = [{
            'type': notif.type,
            'message': notif.message,
            'timestamp': notif.created_at.isoformat() if notif.created_at else None
        } for notif in recent_notifications]
        
        # Alertas
        alerts = []
        if employee.approved == 'pending':
            alerts.append({
                'type': 'info',
                'message': 'Tu perfil está pendiente de aprobación',
                'action': 'wait_approval'
            })
        elif employee.approved == 'rejected':
            alerts.append({
                'type': 'error',
                'message': 'Tu perfil fue rechazado. Contacta con tu manager.',
                'action': 'contact_manager'
            })
        
        return {
            'type': 'employee',
            'statistics': {
                'hours_this_month': hours_this_month,
                'efficiency': efficiency,
                'vacation_days_left': vacation_days_left,
                'hld_hours_left': hld_hours_left
            },
            'monthly_summary': monthly_summary,
            'recent_activity': recent_activity,
            'alerts': alerts
        }
        
    except Exception as e:
        print(f"Error en _get_employee_stats: {e}")
        raise

