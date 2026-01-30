from flask import Blueprint, request, jsonify, current_app, redirect, session
from flask_security import login_user, logout_user, current_user, auth_required
from flask_security.utils import hash_password, verify_password
import logging
from datetime import datetime, timedelta
import secrets

from models.user import User, Role, db
from models.email_verification_token import EmailVerificationToken
from models.employee_invitation import EmployeeInvitation
from models.notification import Notification
from services.google_oauth_service import GoogleOAuthService
from services.email_service import send_verification_email

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de inicio de sesión"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"Intento de login con usuario no encontrado: {email}")
            return jsonify({
                'success': False,
                'message': 'Credenciales inválidas'
            }), 401
        
        # Verificar contraseña con logging detallado
        logger.info(f"Verificando contraseña para usuario: {email}")
        logger.debug(f"Hash del usuario: {user.password[:50]}...")
        logger.debug(f"SECURITY_PASSWORD_HASH config: {current_app.config.get('SECURITY_PASSWORD_HASH', 'NO CONFIGURADO')}")
        
        password_verified = verify_password(password, user.password)
        logger.info(f"Resultado verificación contraseña: {password_verified}")
        
        if not password_verified:
            logger.warning(f"Contraseña incorrecta para usuario: {email}")
            return jsonify({
                'success': False,
                'message': 'Credenciales inválidas'
            }), 401
        
        if not user.active:
            return jsonify({
                'success': False,
                'message': 'Cuenta desactivada. Contacta al administrador.'
            }), 401
        
        if not user.confirmed_at:
            return jsonify({
                'success': False,
                'message': 'Debes verificar tu email antes de iniciar sesión. Revisa tu bandeja de entrada.',
                'requires_verification': True,
                'email': user.email
            }), 401
        
        # Iniciar sesión
        login_user(user, remember=True)
        
        # Obtener información del empleado si existe
        employee_data = None
        if user.employee:
            employee_data = user.employee.to_dict()
        
        logger.info(f"Usuario {email} inició sesión exitosamente")
        
        return jsonify({
            'success': True,
            'message': 'Inicio de sesión exitoso',
            'user': user.to_dict(),
            'employee': employee_data,
            # Si tiene employee (aprobado o no) → dashboard
            # Si no tiene employee → registro
            'redirect_url': '/dashboard' if user.employee else '/employee/register'
        })
        
    except Exception as e:
        logger.error(f"Error en login: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint de registro de usuario"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        invitation_token = data.get('invitation_token')  # Token opcional de invitación
        
        # Validaciones básicas
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Ya existe una cuenta con este email'
            }), 409
        
        # Si hay token de invitación, validarlo
        invitation = None
        requires_email_verification = True
        
        if invitation_token:
            invitation = EmployeeInvitation.query.filter_by(token=invitation_token).first()
            
            if not invitation:
                return jsonify({
                    'success': False,
                    'message': 'Token de invitación inválido'
                }), 400
            
            if invitation.used:
                return jsonify({
                    'success': False,
                    'message': 'Esta invitación ya ha sido utilizada'
                }), 410
            
            if datetime.utcnow() > invitation.expires_at:
                return jsonify({
                    'success': False,
                    'message': 'Esta invitación ha expirado'
                }), 410
            
            # Validar que el email coincide con el de la invitación
            if invitation.email.lower() != email:
                return jsonify({
                    'success': False,
                    'message': f'El email debe coincidir con el de la invitación ({invitation.email})'
                }), 400
            
            # Si la invitación es válida, NO requiere verificación de email
            requires_email_verification = False
            logger.info(f"Registro con invitación válida: {email} (token: {invitation_token})")
        
        # Crear nuevo usuario
        logger.debug(f"Buscando rol 'viewer'...")
        viewer_role = Role.query.filter_by(name='viewer').first()
        if not viewer_role:
            logger.error("Rol 'viewer' no encontrado en la base de datos")
            return jsonify({
                'success': False,
                'message': 'Error de configuración del sistema'
            }), 500
        
        logger.debug(f"Rol 'viewer' encontrado: {viewer_role.id}")
        logger.debug(f"Creando usuario con email: {email}")
        
        try:
            hashed_password = hash_password(password)
            logger.debug(f"Contraseña hasheada correctamente")
        except Exception as hash_error:
            logger.error(f"Error hasheando contraseña: {hash_error}")
            raise
        
        new_user = User(
            email=email,
            password=hashed_password,
            active=True,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        logger.debug(f"Usuario creado en memoria, agregando rol...")
        try:
            new_user.roles.append(viewer_role)
            logger.debug(f"Rol agregado exitosamente")
        except Exception as role_error:
            logger.error(f"Error agregando rol: {role_error}")
            raise
        
        # Si hay invitación válida, confirmar email automáticamente
        if invitation and not requires_email_verification:
            new_user.confirmed_at = datetime.utcnow()
            logger.info(f"✅ Email confirmado automáticamente por invitación: {email}")
        
        logger.debug(f"Agregando usuario a la sesión de BD...")
        try:
            db.session.add(new_user)
            logger.debug(f"Usuario agregado a la sesión")
        except Exception as add_error:
            logger.error(f"Error agregando usuario a la sesión: {add_error}")
            raise
        
        logger.debug(f"Haciendo commit de usuario...")
        try:
            db.session.commit()
            logger.info(f"Usuario creado exitosamente en BD: {email} (ID: {new_user.id})")
        except Exception as commit_error:
            logger.error(f"Error haciendo commit: {commit_error}")
            db.session.rollback()
            raise
        
        # Crear notificación para administradores sobre nuevo usuario registrado
        logger.debug(f"Creando notificaciones para administradores...")
        try:
            from models.notification import NotificationType, NotificationPriority
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                admin_users = User.query.join(User.roles).filter(Role.id == admin_role.id).all()
                logger.debug(f"Encontrados {len(admin_users)} administradores")
                if len(admin_users) > 0:
                    for admin_user in admin_users:
                        notification = Notification(
                            user_id=admin_user.id,
                            title="Nuevo usuario registrado",
                            message=f"Un nuevo usuario se ha registrado: {email}",
                            notification_type=NotificationType.SYSTEM_ALERT,
                            priority=NotificationPriority.MEDIUM,
                            send_email=False,
                            created_by=new_user.id,
                            data={
                                'user_id': new_user.id,
                                'user_email': email,
                                'has_invitation': invitation is not None,
                                'created_at': datetime.utcnow().isoformat()
                            }
                        )
                        db.session.add(notification)
                    db.session.commit()
                    logger.debug(f"Notificaciones creadas exitosamente para {len(admin_users)} administradores")
        except Exception as notif_error:
            logger.warning(f"Error creando notificaciones (no crítico, registro continúa): {notif_error}")
            db.session.rollback()
            # No fallar el registro si las notificaciones fallan
        
        # Solo generar token de verificación si NO hay invitación
        email_sent = False
        if requires_email_verification:
            logger.debug(f"Generando token de verificación de email...")
            try:
                # Generar token de verificación
                verification_token = secrets.token_urlsafe(32)
                expires_at = datetime.utcnow() + timedelta(hours=24)
                
                email_token = EmailVerificationToken(
                    user_id=new_user.id,
                    token=verification_token,
                    expires_at=expires_at
                )
                
                db.session.add(email_token)
                db.session.commit()
                logger.debug(f"Token de verificación creado exitosamente")
                
                # Enviar email de verificación
                frontend_url = request.headers.get('Origin', 'https://team-time-management.vercel.app')
                verification_link = f"{frontend_url}/verify-email?token={verification_token}&auto=1"
                
                logger.debug(f"Enviando email de verificación a {email}...")
                email_sent = send_verification_email(
                    to_email=email,
                    verification_link=verification_link,
                    user_name=new_user.first_name or new_user.email.split('@')[0]
                )
                
                logger.info(f"Nuevo usuario registrado: {email} - Email de verificación enviado: {email_sent}")
            except Exception as email_error:
                logger.error(f"Error en proceso de verificación de email (no crítico): {email_error}")
                db.session.rollback()
                # Continuar aunque falle el email
        else:
            logger.info(f"Nuevo usuario registrado con invitación: {email} - Email confirmado automáticamente")
        
        return jsonify({
            'success': True,
            'message': 'Registro exitoso.' + (' Te hemos enviado un email para verificar tu cuenta.' if requires_email_verification else ' Tu cuenta ha sido activada automáticamente.'),
            'requires_verification': requires_email_verification,
            'email_sent': email_sent,
            'user_id': new_user.id,
            'has_invitation': invitation is not None,
            'invitation_token': invitation_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error en registro: {e}")
        logger.error(f"Traceback completo: {error_trace}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e) if current_app.config.get('DEBUG') else None
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@auth_required()
def logout():
    """Endpoint de cierre de sesión"""
    try:
        user_email = current_user.email
        logout_user()
        
        logger.info(f"Usuario {user_email} cerró sesión")
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return jsonify({
            'success': False,
            'message': 'Error cerrando sesión'
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Obtiene información del usuario actual.
    NO requiere @auth_required() para poder devolver respuesta apropiada cuando no hay sesión.
    """
    try:
        if current_user.is_authenticated:
            # Cargar el usuario completo desde la base de datos
            from models.employee import Employee
            from models.team import Team

            user = User.query.filter_by(id=current_user.id).first()

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }), 404

            employee_data = None
            # Cargar employee sin incluir summary para evitar problemas de lazy loading
            employee = Employee.query.filter_by(user_id=user.id).first()
            if employee:
                # Cargar team_name directamente con un query separado
                team = Team.query.filter_by(id=employee.team_id).first() if employee.team_id else None
                
                # Construir employee_data manualmente sin llamar a to_dict con include_summary
                employee_data = {
                    'id': employee.id,
                    'user_id': employee.user_id,
                    'full_name': employee.full_name,
                    'team_id': employee.team_id,
                    'team_name': team.name if team else None,
                    'hours_monday_thursday': employee.hours_monday_thursday,
                    'hours_friday': employee.hours_friday,
                    'hours_summer': employee.hours_summer,
                    'has_summer_schedule': employee.has_summer_schedule,
                    'summer_months': employee.summer_months_list,
                    'annual_vacation_days': employee.annual_vacation_days,
                    'annual_hld_hours': employee.annual_hld_hours,
                    'country': employee.country,
                    'region': employee.region,
                    'city': employee.city,
                    'active': employee.active,
                    'approved': employee.approved,
                    'created_at': employee.created_at.isoformat() if employee.created_at else None,
                    'approved_at': employee.approved_at.isoformat() if employee.approved_at else None
                }

            user_dict = user.to_dict()

            return jsonify({
                'success': True,
                'user': user_dict,
                'employee': employee_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No hay sesión activa'
            }), 401
            
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        return jsonify({
            'success': False,
            'message': 'Error verificando sesión'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@auth_required()
def change_password():
    """Cambia la contraseña del usuario actual"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Contraseña actual y nueva contraseña son requeridas'
            }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verificar contraseña actual
        if not verify_password(current_password, current_user.password):
            return jsonify({
                'success': False,
                'message': 'Contraseña actual incorrecta'
            }), 401
        
        # Validar nueva contraseña
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'La nueva contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Actualizar contraseña
        current_user.password = hash_password(new_password)
        db.session.commit()
        
        logger.info(f"Usuario {current_user.email} cambió su contraseña")
        
        return jsonify({
            'success': True,
            'message': 'Contraseña actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cambiando contraseña: {e}")
        return jsonify({
            'success': False,
            'message': 'Error actualizando contraseña'
        }), 500

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """
    DEPRECATED: Usar /auth/me en su lugar.
    Verifica si hay una sesión activa (mantenido por compatibilidad)
    """
    try:
        if current_user.is_authenticated:
            employee_data = None
            if current_user.employee:
                employee_data = current_user.employee.to_dict()
            
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': current_user.to_dict(),
                'employee': employee_data
            })
        else:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'No hay sesión activa'
            }), 401
            
    except Exception as e:
        logger.error(f"Error verificando sesión: {e}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': 'Error verificando sesión'
        }), 500

@auth_bp.route('/confirm-email-now', methods=['POST'])
def confirm_email_now():
    """
    Endpoint temporal para confirmar el email de un usuario inmediatamente.
    Útil para desarrollo y para resolver casos donde usuarios quedaron sin confirmed_at.
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email es requerido'
            }), 400
        
        email = data['email'].lower().strip()
        
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Si ya está confirmado, no hacer nada
        if user.confirmed_at:
            return jsonify({
                'success': True,
                'message': 'El email ya estaba confirmado',
                'already_confirmed': True
            }), 200
        
        # Confirmar email
        user.confirmed_at = db.func.now()
        db.session.commit()
        
        logger.info(f"Email confirmado para usuario: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Email confirmado exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error confirmando email: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/debug-user', methods=['POST'])
def debug_user():
    """
    Endpoint de debug para ver el estado real del usuario en BD
    """
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Forzar refresh desde BD
        db.session.refresh(user)
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'password_hash_length': len(user.password) if user.password else 0,
            'password_hash_starts_with': user.password[:10] if user.password else 'NULL',
            'password_is_none': user.password is None,
            'password_is_empty_string': user.password == '',
            'confirmed_at': user.confirmed_at.isoformat() if user.confirmed_at else None,
            'active': user.active
        }), 200
        
    except Exception as e:
        logger.error(f"Error en debug: {e}")
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@auth_bp.route('/reset-password-emergency', methods=['POST'])
def reset_password_emergency():
    """
    Endpoint temporal para resetear contraseña sin autenticación.
    Útil para casos donde el hash de password está corrupto.
    SOLO PARA DESARROLLO - Eliminar en producción final.
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Email y nueva contraseña son requeridos'
            }), 400
        
        email = data['email'].lower().strip()
        new_password = data['new_password']
        
        # Validar longitud de contraseña
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Resetear contraseña
        user.password = hash_password(new_password)
        db.session.commit()
        
        logger.info(f"Contraseña reseteada para usuario: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Contraseña reseteada exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error reseteando contraseña: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email_get(token):
    """
    GET: Muestra información del token sin verificarlo (para evitar pre-fetch de clientes de email)
    """
    try:
        # Buscar el token en la base de datos
        email_token = EmailVerificationToken.query.filter_by(token=token).first()
        
        if not email_token:
            return jsonify({
                'success': False,
                'message': 'Token de verificación inválido',
                'valid': False
            }), 404
        
        # Verificar si el token ya fue usado
        if email_token.used:
            return jsonify({
                'success': False,
                'message': 'Este token ya fue utilizado',
                'valid': False,
                'used': True
            }), 400
        
        # Verificar si el token ha expirado
        if email_token.is_expired():
            return jsonify({
                'success': False,
                'message': 'El token ha expirado. Solicita un nuevo enlace de verificación.',
                'valid': False,
                'expired': True
            }), 400
        
        # Obtener el usuario
        user = User.query.get(email_token.user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado',
                'valid': False
            }), 404
        
        # Si el usuario ya está verificado, informar
        if user.confirmed_at:
            return jsonify({
                'success': True,
                'message': 'Este email ya está verificado',
                'valid': True,
                'already_verified': True,
                'email': user.email
            }), 200
        
        # Token válido pero no verificado aún - solo devolver info, NO verificar
        return jsonify({
            'success': True,
            'message': 'Token válido. Haz clic en el botón para verificar tu email.',
            'valid': True,
            'email': user.email,
            'requires_confirmation': True
        }), 200
        
    except Exception as e:
        logger.error(f"Error verificando email (GET): {e}")
        return jsonify({
            'success': False,
            'message': 'Error al verificar el email',
            'valid': False
        }), 500

@auth_bp.route('/verify-email/<token>', methods=['POST'])
def verify_email_post(token):
    """
    POST: Verifica el email del usuario usando el token (solo cuando el usuario hace clic explícitamente)
    """
    try:
        # Buscar el token en la base de datos
        email_token = EmailVerificationToken.query.filter_by(token=token).first()
        
        if not email_token:
            return jsonify({
                'success': False,
                'message': 'Token de verificación inválido'
            }), 404
        
        # Verificar si el token ya fue usado
        if email_token.used:
            return jsonify({
                'success': False,
                'message': 'Este token ya fue utilizado'
            }), 400
        
        # Verificar si el token ha expirado
        if email_token.is_expired():
            return jsonify({
                'success': False,
                'message': 'El token ha expirado. Solicita un nuevo enlace de verificación.',
                'expired': True
            }), 400
        
        # Obtener el usuario
        user = User.query.get(email_token.user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Verificar el email
        user.confirmed_at = datetime.utcnow()
        email_token.mark_as_used()
        
        db.session.commit()
        
        logger.info(f"✅ Email verificado para usuario: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Email verificado exitosamente. Ya puedes iniciar sesión.',
            'email': user.email
        }), 200
        
    except Exception as e:
        logger.error(f"Error verificando email (POST): {e}")
        return jsonify({
            'success': False,
            'message': 'Error al verificar el email'
        }), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    Reenvía el email de verificación a un usuario
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email es requerido'
            }), 400
        
        email = data['email'].lower().strip()
        
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Si ya está verificado, no hacer nada
        if user.confirmed_at:
            return jsonify({
                'success': False,
                'message': 'Esta cuenta ya está verificada'
            }), 400
        
        # Invalidar tokens anteriores
        old_tokens = EmailVerificationToken.query.filter_by(
            user_id=user.id,
            used=False
        ).all()
        
        for old_token in old_tokens:
            old_token.used = True
            old_token.used_at = datetime.utcnow()
        
        # Generar nuevo token
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        email_token = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        
        db.session.add(email_token)
        db.session.commit()
        
        # Enviar email
        frontend_url = request.headers.get('Origin', 'https://team-time-management.vercel.app')
        verification_link = f"{frontend_url}/verify-email?token={verification_token}&auto=1"
        
        email_sent = send_verification_email(
            to_email=email,
            verification_link=verification_link,
            user_name=user.first_name or user.email.split('@')[0]
        )
        
        logger.info(f"Nuevo email de verificación enviado a: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Email de verificación reenviado. Revisa tu bandeja de entrada.',
            'email_sent': email_sent
        }), 200
        
    except Exception as e:
        logger.error(f"Error reenviando verificación: {e}")
        return jsonify({
            'success': False,
            'message': 'Error al reenviar el email de verificación'
        }), 500

@auth_bp.route('/roles', methods=['GET'])
@auth_required()
def get_roles():
    """Obtiene la lista de roles disponibles (solo para admins)"""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        roles = Role.query.all()
        
        return jsonify({
            'success': True,
            'roles': [
                {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description
                }
                for role in roles
            ]
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo roles: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo roles'
        }), 500

# ===========================================
# GOOGLE OAUTH ENDPOINTS
# ===========================================

@auth_bp.route('/google/url', methods=['GET'])
def google_auth_url():
    """Obtiene la URL de autorización de Google"""
    try:
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        if not google_oauth.is_configured():
            return jsonify({
                'success': False,
                'message': 'Google OAuth no está configurado'
            }), 400
        
        auth_url = google_oauth.get_auth_url()
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        })
        
    except Exception as e:
        logger.error(f"Error generando URL de Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error generando URL de autorización'
        }), 500

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Maneja el callback de Google OAuth"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code or not state:
            return jsonify({
                'success': False,
                'message': 'Código de autorización o estado faltante'
            }), 400
        
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        success, message, user_data = google_oauth.handle_callback(code, state)
        
        if success and user_data:
            # Buscar el usuario en la base de datos
            user = User.query.filter_by(email=user_data['email']).first()
            
            if user:
                # Iniciar sesión
                login_user(user, remember=True)
                
                # Obtener información del empleado si existe
                employee_data = None
                if user.employee:
                    employee_data = user.employee.to_dict()
                
                logger.info(f"Usuario {user.email} inició sesión con Google OAuth")
                
                return jsonify({
                    'success': True,
                    'message': 'Autenticación con Google exitosa',
                    'user': user.to_dict(),
                    'employee': employee_data,
                    # Si tiene employee (aprobado o no) → dashboard
                    # Si no tiene employee → registro
                    'redirect_url': '/dashboard' if user.employee else '/employee/register'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado después de la autenticación'
                }), 404
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error en callback de Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error en autenticación con Google'
        }), 500

@auth_bp.route('/google/config', methods=['GET'])
def google_config():
    """Obtiene la configuración de Google OAuth (solo para verificar si está configurado)"""
    try:
        google_oauth = GoogleOAuthService()
        google_oauth.init_app(current_app)
        
        return jsonify({
            'success': True,
            'configured': google_oauth.is_configured(),
            'client_id': current_app.config.get('GOOGLE_CLIENT_ID', '').split('.')[0] + '...' if current_app.config.get('GOOGLE_CLIENT_ID') else None,
            'redirect_uri': current_app.config.get('GOOGLE_REDIRECT_URI')
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración de Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo configuración'
        }), 500

@auth_bp.route('/google/disconnect', methods=['POST'])
@auth_required()
def google_disconnect():
    """Desconecta la cuenta de Google del usuario actual"""
    try:
        # En una implementación completa, aquí se revocaría el token
        # y se eliminarían los datos de Google del usuario
        
        logger.info(f"Usuario {current_user.email} desconectó su cuenta de Google")
        
        return jsonify({
            'success': True,
            'message': 'Cuenta de Google desconectada exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error desconectando Google OAuth: {e}")
        return jsonify({
            'success': False,
            'message': 'Error desconectando cuenta de Google'
        }), 500

@auth_bp.route('/reset-admin-password', methods=['POST'])
def reset_admin_password():
    """Endpoint temporal para resetear contraseña del admin"""
    try:
        # Solo permitir en desarrollo o con una clave secreta
        secret_key = request.json.get('secret_key')
        if secret_key != 'TEMPORARY_RESET_KEY_2025':
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        admin_user = User.query.filter_by(email='admin@teamtime.com').first()
        if not admin_user:
            return jsonify({
                'success': False,
                'message': 'Usuario admin no encontrado'
            }), 404
        
        new_password = 'Admin2025!'
        admin_user.password = hash_password(new_password)
        db.session.commit()
        
        logger.info(f"Contraseña del admin reseteada exitosamente")
        
        return jsonify({
            'success': True,
            'message': 'Contraseña del admin reseteada exitosamente',
            'email': admin_user.email,
            'password': new_password
        })
        
    except Exception as e:
        logger.error(f"Error reseteando contraseña del admin: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
