"""
Decoradores de autorización para endpoints de la API.

Este módulo proporciona decoradores que verifican roles de usuario
para controlar el acceso a endpoints específicos.

Uso:
    @auth_bp.route('/admin/settings')
    @auth_required()
    @admin_required()
    def admin_settings():
        ...
"""

from functools import wraps
from flask import jsonify
from flask_security import current_user
import logging

logger = logging.getLogger(__name__)


def roles_required(*required_roles):
    """
    Decorador que verifica que el usuario tenga al menos uno de los roles especificados.
    Debe usarse DESPUÉS de @auth_required()
    
    Args:
        *required_roles: Nombres de los roles requeridos (al menos uno debe coincidir)
    
    Returns:
        Función decorada que verifica roles antes de ejecutar
    
    Raises:
        401: Si el usuario no está autenticado
        403: Si el usuario no tiene ninguno de los roles requeridos
    
    Ejemplo:
        @auth_bp.route('/manager/team')
        @auth_required()
        @roles_required('admin', 'manager')
        def manage_team():
            # Solo admins o managers pueden acceder
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificar autenticación
            if not current_user.is_authenticated:
                logger.warning(
                    f"Usuario no autenticado intentó acceder a {fn.__name__}"
                )
                return jsonify({
                    'success': False,
                    'message': 'Autenticación requerida'
                }), 401
            
            # Obtener roles del usuario
            user_roles = [role.name for role in current_user.roles]
            
            # Verificar si tiene al menos uno de los roles requeridos
            if not any(role in user_roles for role in required_roles):
                logger.warning(
                    f"Usuario {current_user.email} (roles: {user_roles}) "
                    f"intentó acceder a {fn.__name__} que requiere roles: {required_roles}"
                )
                return jsonify({
                    'success': False,
                    'message': f'Acceso denegado. Rol requerido: {", ".join(required_roles)}'
                }), 403
            
            # Usuario tiene permiso, ejecutar función
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def admin_required():
    """
    Decorador que verifica que el usuario tenga el rol 'admin'.
    Alias de convenience para roles_required('admin')
    
    Returns:
        Función decorada que verifica rol admin
    
    Ejemplo:
        @admin_bp.route('/settings')
        @auth_required()
        @admin_required()
        def admin_settings():
            # Solo admins pueden acceder
            ...
    """
    return roles_required('admin')


def manager_or_admin_required():
    """
    Decorador que verifica que el usuario sea manager o admin.
    Alias de convenience para roles_required('admin', 'manager')
    
    Returns:
        Función decorada que verifica rol manager o admin
    
    Ejemplo:
        @teams_bp.route('/<int:team_id>/members', methods=['POST'])
        @auth_required()
        @manager_or_admin_required()
        def add_team_member(team_id):
            # Solo managers o admins pueden añadir miembros
            ...
    """
    return roles_required('admin', 'manager')


def employee_or_above_required():
    """
    Decorador que verifica que el usuario tenga rol employee, manager o admin.
    
    Returns:
        Función decorada que verifica rol employee o superior
    
    Ejemplo:
        @reports_bp.route('/my-hours')
        @auth_required()
        @employee_or_above_required()
        def my_hours():
            # Empleados, managers y admins pueden ver sus horas
            ...
    """
    return roles_required('admin', 'manager', 'employee')


def owns_resource_or_admin(resource_user_id_param='user_id'):
    """
    Decorador que verifica que el usuario sea admin O sea el dueño del recurso.
    
    Args:
        resource_user_id_param: Nombre del parámetro que contiene el user_id del recurso
    
    Returns:
        Función decorada que verifica ownership o rol admin
    
    Ejemplo:
        @employees_bp.route('/<int:user_id>/profile')
        @auth_required()
        @owns_resource_or_admin('user_id')
        def get_employee_profile(user_id):
            # Solo el empleado o un admin pueden ver el perfil
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificar autenticación
            if not current_user.is_authenticated:
                logger.warning(
                    f"Usuario no autenticado intentó acceder a {fn.__name__}"
                )
                return jsonify({
                    'success': False,
                    'message': 'Autenticación requerida'
                }), 401
            
            # Verificar si es admin (tiene acceso total)
            user_roles = [role.name for role in current_user.roles]
            if 'admin' in user_roles:
                return fn(*args, **kwargs)
            
            # Si no es admin, verificar ownership
            resource_user_id = kwargs.get(resource_user_id_param)
            
            if resource_user_id is None:
                logger.error(
                    f"Parámetro {resource_user_id_param} no encontrado en kwargs de {fn.__name__}"
                )
                return jsonify({
                    'success': False,
                    'message': 'Error de configuración del endpoint'
                }), 500
            
            if current_user.id != resource_user_id:
                logger.warning(
                    f"Usuario {current_user.email} (ID: {current_user.id}) "
                    f"intentó acceder a recurso de usuario ID: {resource_user_id}"
                )
                return jsonify({
                    'success': False,
                    'message': 'Acceso denegado. Solo puedes acceder a tus propios recursos.'
                }), 403
            
            # Usuario es dueño del recurso
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def check_permission(permission_checker):
    """
    Decorador genérico que acepta una función de verificación de permisos.
    
    Args:
        permission_checker: Función que recibe current_user y devuelve (bool, error_message)
    
    Returns:
        Función decorada que verifica permisos personalizados
    
    Ejemplo:
        def can_edit_team(user, team_id):
            # Lógica personalizada
            if user.is_admin or user.manages_team(team_id):
                return True, None
            return False, "No tienes permiso para editar este equipo"
        
        @teams_bp.route('/<int:team_id>', methods=['PUT'])
        @auth_required()
        @check_permission(lambda user: can_edit_team(user, team_id))
        def edit_team(team_id):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    'success': False,
                    'message': 'Autenticación requerida'
                }), 401
            
            # Ejecutar verificación personalizada
            has_permission, error_message = permission_checker(current_user)
            
            if not has_permission:
                logger.warning(
                    f"Usuario {current_user.email} no tiene permiso para {fn.__name__}: {error_message}"
                )
                return jsonify({
                    'success': False,
                    'message': error_message or 'Acceso denegado'
                }), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator

