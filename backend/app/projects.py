from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging

from models import db
from models.project import Project, ProjectAssignment
from models.team import Team
from models.employee import Employee
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

projects_bp = Blueprint('projects', __name__)


def _can_manage_projects(user):
    return user.is_admin() or user.is_manager()


@projects_bp.route('/', methods=['GET'])
@auth_required()
def list_projects():
    """Lista proyectos con filtros básicos."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    status = request.args.get('status')
    client = request.args.get('client')
    search = request.args.get('search')
    include_assignments = request.args.get('include_assignments', 'false').lower() == 'true'

    query = Project.query.filter(Project.active == True)

    if status:
        query = query.filter(Project.status == status)
    if client:
        query = query.filter(Project.client_name.ilike(f'%{client}%'))
    if search:
        query = query.filter(
            (Project.name.ilike(f'%{search}%')) |
            (Project.code.ilike(f'%{search}%')) |
            (Project.client_name.ilike(f'%{search}%'))
        )

    projects = query.order_by(Project.created_at.desc()).all()

    return jsonify({
        'success': True,
        'projects': [project.to_dict(include_assignments=include_assignments) for project in projects]
    })


@projects_bp.route('/', methods=['POST'])
@auth_required()
def create_project():
    """Crea un nuevo proyecto."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    data = request.get_json() or {}
    required_fields = ['code', 'name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    project = Project(
        code=data['code'].strip(),
        name=data['name'].strip(),
        description=data.get('description'),
        client_name=data.get('client_name'),
        status=data.get('status', 'planned'),
        service_line=data.get('service_line'),
        billing_model=data.get('billing_model'),
        start_date=_parse_date(data.get('start_date')),
        end_date=_parse_date(data.get('end_date')),
        budget_hours=data.get('budget_hours'),
        budget_amount=data.get('budget_amount'),
        manager_id=data.get('manager_id'),
        active=True
    )

    team_ids = data.get('team_ids', [])
    if team_ids:
        teams = Team.query.filter(Team.id.in_(team_ids)).all()
        project.teams = teams

    db.session.add(project)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'El código del proyecto ya existe'}), 409

    # Notificar sobre la creación del proyecto
    try:
        NotificationService.notify_project_action(project, 'created', current_user)
    except Exception as notif_error:
        logger.error(f"Error enviando notificación de creación de proyecto: {notif_error}")

    return jsonify({'success': True, 'project': project.to_dict(include_assignments=True)}), 201


@projects_bp.route('/<int:project_id>', methods=['GET'])
@auth_required()
def get_project(project_id):
    """Obtiene el detalle de un proyecto."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    include_assignments = request.args.get('include_assignments', 'true').lower() == 'true'
    project = Project.query.get(project_id)
    if not project or not project.active:
        return jsonify({'success': False, 'message': 'Proyecto no encontrado'}), 404

    return jsonify({'success': True, 'project': project.to_dict(include_assignments=include_assignments)})


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@auth_required()
def update_project(project_id):
    """Actualiza un proyecto."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    project = Project.query.get(project_id)
    if not project or not project.active:
        return jsonify({'success': False, 'message': 'Proyecto no encontrado'}), 404

    data = request.get_json() or {}
    for field in ['name', 'description', 'client_name', 'status', 'service_line', 'billing_model']:
        if field in data:
            setattr(project, field, data[field])

    if 'start_date' in data:
        project.start_date = _parse_date(data['start_date'])
    if 'end_date' in data:
        project.end_date = _parse_date(data['end_date'])
    if 'budget_hours' in data:
        project.budget_hours = data['budget_hours']
    if 'budget_amount' in data:
        project.budget_amount = data['budget_amount']
    if 'manager_id' in data:
        project.manager_id = data['manager_id']
    if 'team_ids' in data:
        teams = Team.query.filter(Team.id.in_(data['team_ids'] or [])).all()
        project.teams = teams

    db.session.commit()
    
    # Notificar sobre la actualización del proyecto
    try:
        NotificationService.notify_project_action(project, 'updated', current_user)
    except Exception as notif_error:
        logger.error(f"Error enviando notificación de actualización de proyecto: {notif_error}")
    
    return jsonify({'success': True, 'project': project.to_dict(include_assignments=True)})


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@auth_required()
def delete_project(project_id):
    """Desactiva un proyecto."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    project = Project.query.get(project_id)
    if not project or not project.active:
        return jsonify({'success': False, 'message': 'Proyecto no encontrado'}), 404

    project.active = False
    db.session.commit()
    
    # Notificar sobre la eliminación del proyecto
    try:
        NotificationService.notify_project_action(project, 'deleted', current_user)
    except Exception as notif_error:
        logger.error(f"Error enviando notificación de eliminación de proyecto: {notif_error}")
    
    return jsonify({'success': True, 'message': 'Proyecto desactivado'})


@projects_bp.route('/<int:project_id>/assignments', methods=['POST'])
@auth_required()
def create_project_assignment(project_id):
    """Asigna un empleado a un proyecto con porcentaje."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    project = Project.query.get(project_id)
    if not project or not project.active:
        return jsonify({'success': False, 'message': 'Proyecto no encontrado'}), 404

    data = request.get_json() or {}
    employee_id = data.get('employee_id')
    if not employee_id:
        return jsonify({'success': False, 'message': 'employee_id es requerido'}), 400

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404

    allocation_percent = data.get('allocation_percent')
    if allocation_percent is not None:
        try:
            allocation_percent = float(allocation_percent)
            if allocation_percent < 0 or allocation_percent > 100:
                return jsonify({'success': False, 'message': 'El porcentaje debe estar entre 0 y 100'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Porcentaje inválido'}), 400

    assignment = ProjectAssignment(
        project_id=project.id,
        employee_id=employee.id,
        team_id=data.get('team_id'),
        role=data.get('role'),
        allocation_percent=allocation_percent,
        start_date=_parse_date(data.get('start_date')),
        end_date=_parse_date(data.get('end_date')),
        notes=data.get('notes'),
        active=True
    )

    db.session.add(assignment)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'El empleado ya está asignado a este proyecto'}), 409

    # Notificar al empleado sobre su asignación al proyecto
    try:
        NotificationService.notify_project_assignment(employee, project, current_user)
    except Exception as notif_error:
        logger.error(f"Error enviando notificación de asignación a proyecto: {notif_error}")

    return jsonify({'success': True, 'assignment': assignment.to_dict(include_employee=True)}), 201


@projects_bp.route('/<int:project_id>/assignments/<int:assignment_id>', methods=['PUT'])
@auth_required()
def update_project_assignment(project_id, assignment_id):
    """Actualiza una asignación de proyecto."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    assignment = ProjectAssignment.query.filter_by(id=assignment_id, project_id=project_id).first()
    if not assignment or not assignment.active:
        return jsonify({'success': False, 'message': 'Asignación no encontrada'}), 404

    data = request.get_json() or {}
    if 'role' in data:
        assignment.role = data['role']
    if 'allocation_percent' in data:
        try:
            allocation_percent = float(data['allocation_percent'])
            if allocation_percent < 0 or allocation_percent > 100:
                return jsonify({'success': False, 'message': 'El porcentaje debe estar entre 0 y 100'}), 400
            assignment.allocation_percent = allocation_percent
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Porcentaje inválido'}), 400
    if 'team_id' in data:
        assignment.team_id = data['team_id']
    if 'start_date' in data:
        assignment.start_date = _parse_date(data['start_date'])
    if 'end_date' in data:
        assignment.end_date = _parse_date(data['end_date'])
    if 'notes' in data:
        assignment.notes = data['notes']
    if 'active' in data:
        assignment.active = bool(data['active'])

    db.session.commit()
    return jsonify({'success': True, 'assignment': assignment.to_dict(include_employee=True)})


@projects_bp.route('/<int:project_id>/assignments/<int:assignment_id>', methods=['DELETE'])
@auth_required()
def delete_project_assignment(project_id, assignment_id):
    """Elimina una asignación de proyecto."""
    if not _can_manage_projects(current_user):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403

    assignment = ProjectAssignment.query.filter_by(id=assignment_id, project_id=project_id).first()
    if not assignment:
        return jsonify({'success': False, 'message': 'Asignación no encontrada'}), 404

    assignment.active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Asignación eliminada'})


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(value).date()
    except (ValueError, TypeError):
        return None

