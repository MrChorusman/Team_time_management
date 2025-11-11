#!/usr/bin/env python3
"""
Sistema de autenticación simple y robusto
Reemplaza el sistema actual con uno más directo y funcional
"""

from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import psycopg2
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Crear blueprint
auth_simple_bp = Blueprint('auth_simple', __name__)

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        host = os.environ.get('SUPABASE_HOST')
        port = os.environ.get('SUPABASE_PORT', '6543')
        database = os.environ.get('SUPABASE_DB', 'postgres')
        user = os.environ.get('SUPABASE_USER', 'postgres')
        password = os.environ.get('SUPABASE_DB_PASSWORD')
        
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return connection
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return None

def verify_user_password(email, password):
    """Verificar credenciales de usuario"""
    try:
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión a la base de datos"
        
        cursor = conn.cursor()
        
        # Buscar usuario
        cursor.execute("""
            SELECT id, email, password, active, confirmed_at, first_name, last_name
            FROM "user" 
            WHERE email = %s
        """, (email.lower().strip(),))
        
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user_data:
            return None, "Usuario no encontrado"
        
        user_id, user_email, hashed_password, active, confirmed_at, first_name, last_name = user_data
        
        # Verificar si está activo
        if not active:
            return None, "Cuenta desactivada"
        
        # Verificar si está confirmado
        if not confirmed_at:
            return None, "Debes confirmar tu email antes de iniciar sesión"
        
        # Verificar contraseña
        if not check_password_hash(hashed_password, password):
            return None, "Credenciales inválidas"
        
        # Obtener roles del usuario
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.name
            FROM role r
            JOIN roles_users ru ON r.id = ru.role_id
            WHERE ru.user_id = %s
        """, (user_id,))
        
        roles = [{'name': row[0]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return {
            'id': user_id,
            'email': user_email,
            'first_name': first_name,
            'last_name': last_name,
            'active': active,
            'confirmed_at': confirmed_at,
            'roles': roles
        }, None
        
    except Exception as e:
        logger.error(f"Error verificando usuario: {e}")
        return None, f"Error interno: {str(e)}"

def create_user(email, password, first_name=None, last_name=None):
    """Crear nuevo usuario"""
    try:
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión a la base de datos"
        
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM \"user\" WHERE email = %s", (email.lower().strip(),))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None, "El usuario ya existe"
        
        # Hash de la contraseña
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        
        # Crear usuario (sin especificar ID para que use autoincremental)
        cursor.execute("""
            INSERT INTO "user" (email, password, active, confirmed_at, fs_uniquifier, first_name, last_name, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            email.lower().strip(),
            hashed_password,
            True,  # Activo por defecto
            None,  # NO confirmado hasta verificar email
            str(uuid.uuid4()),  # fs_uniquifier
            first_name,
            last_name
        ))
        
        # Obtener el ID generado
        user_id = cursor.fetchone()[0]
        
        # Asignar rol de viewer por defecto
        cursor.execute("SELECT id FROM role WHERE name = 'viewer'")
        role_result = cursor.fetchone()
        
        if role_result:
            role_id = role_result[0]
            cursor.execute("""
                INSERT INTO roles_users (user_id, role_id)
                VALUES (%s, %s)
            """, (user_id, role_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'id': user_id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'active': True,
            'confirmed_at': None,  # No confirmado hasta verificar email
            'needs_verification': True
        }, None
        
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        return None, f"Error interno: {str(e)}"

@auth_simple_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login simplificado"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email']
        password = data['password']
        
        # Verificar credenciales
        user_data, error = verify_user_password(email, password)
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 401
        
        # Crear sesión
        session['user_id'] = user_data['id']
        session['user_email'] = user_data['email']
        session['authenticated'] = True
        
        logger.info(f"Usuario {email} inició sesión exitosamente")
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'user': user_data,
            'redirect_url': '/dashboard'
        })
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_simple_bp.route('/register', methods=['POST'])
def register():
    """Endpoint de registro simplificado"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        email = data['email']
        password = data['password']
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Validaciones básicas
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Crear usuario
        user_data, error = create_user(email, password, first_name, last_name)
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        logger.info(f"Nuevo usuario registrado: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente. Por favor, verifica tu email para activar tu cuenta.',
            'user': user_data,
            'needs_verification': True
        })
        
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_simple_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint de logout simplificado"""
    try:
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logout exitoso'
        })
        
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_simple_bp.route('/check-session', methods=['GET'])
def check_session():
    """Verificar sesión actual"""
    try:
        if session.get('authenticated') and session.get('user_id'):
            # Obtener información completa del usuario desde la BD
            conn = get_db_connection()
            if not conn:
                return jsonify({
                    'authenticated': False
                }), 500
            
            cursor = conn.cursor()
            
            # Obtener datos del usuario
            cursor.execute("""
                SELECT id, email, first_name, last_name, active, confirmed_at
                FROM "user" 
                WHERE id = %s
            """, (session.get('user_id'),))
            
            user_data = cursor.fetchone()
            if not user_data:
                session.clear()
                return jsonify({
                    'authenticated': False
                })
            
            user_id, email, first_name, last_name, active, confirmed_at = user_data
            
            # Obtener roles del usuario
            cursor.execute("""
                SELECT r.name
                FROM role r
                JOIN roles_users ru ON r.id = ru.role_id
                WHERE ru.user_id = %s
            """, (user_id,))
            
            roles = [{'name': row[0]} for row in cursor.fetchall()]
            
            # Obtener información del empleado si existe
            cursor.execute("""
                SELECT e.id, e.full_name, e.team_id, t.name as team_name, e.approved
                FROM employee e
                LEFT JOIN team t ON e.team_id = t.id
                WHERE e.user_id = %s
            """, (user_id,))
            
            employee_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user_id,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'active': active,
                    'confirmed_at': confirmed_at.isoformat() if confirmed_at else None,
                    'roles': roles
                },
                'employee': {
                    'id': employee_data[0],
                    'full_name': employee_data[1],
                    'team_id': employee_data[2],
                    'team_name': employee_data[3],
                    'approved': employee_data[4]
                } if employee_data else None
            })
        else:
            return jsonify({
                'authenticated': False
            })
        
    except Exception as e:
        logger.error(f"Error verificando sesión: {e}")
        return jsonify({
            'authenticated': False
        }), 500

@auth_simple_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Endpoint para solicitar restablecimiento de contraseña"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email es requerido'
            }), 400
        
        email = data['email'].lower().strip()
        
        # Verificar si el usuario existe
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, first_name FROM \"user\" WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user_data:
            # Por seguridad, no revelamos si el email existe o no
            logger.info(f"Solicitud de restablecimiento de contraseña para email no registrado: {email}")
            return jsonify({
                'success': True,
                'message': 'Si el email está registrado, recibirás un enlace para restablecer tu contraseña'
            })
        
        # En una implementación completa, aquí se generaría un token único
        # y se enviaría un email con el enlace de restablecimiento
        logger.info(f"Solicitud de restablecimiento de contraseña para: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Si el email está registrado, recibirás un enlace para restablecer tu contraseña'
        })
        
    except Exception as e:
        logger.error(f"Error en forgot password: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@auth_simple_bp.route('/teams', methods=['GET'])
def get_teams():
    """Obtener lista de equipos disponibles"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM team ORDER BY name")
        teams = cursor.fetchall()
        cursor.close()
        conn.close()
        
        team_list = [team[0] for team in teams]
        
        # Si no hay equipos en la base de datos, devolver equipos por defecto
        if not team_list:
            team_list = [
                'Desarrollo Frontend',
                'Desarrollo Backend', 
                'Marketing Digital',
                'Ventas',
                'Recursos Humanos',
                'Monitorización',
                'Soporte Técnico'
            ]
        
        return jsonify({
            'success': True,
            'teams': team_list
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo equipos: {e}")
        return jsonify({
            'success': False,
            'message': f'Error obteniendo equipos: {str(e)}'
        }), 500

@auth_simple_bp.route('/autonomous-communities', methods=['GET'])
def get_autonomous_communities():
    """Obtener lista de comunidades autónomas españolas"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM autonomous_communities ORDER BY name")
        communities = cursor.fetchall()
        cursor.close()
        conn.close()
        
        community_list = [community[0] for community in communities]
        
        return jsonify({
            'success': True,
            'communities': community_list
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo comunidades autónomas: {e}")
        return jsonify({
            'success': False,
            'message': f'Error obteniendo comunidades: {str(e)}'
        }), 500

@auth_simple_bp.route('/employee/register', methods=['POST'])
def register_employee():
    """Registrar nuevo empleado"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['team_name', 'full_name', 'hours_monday_thursday', 'hours_friday', 
                          'annual_vacation_days', 'annual_free_hours', 'country', 'city', 'start_date']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        
        # Obtener team_id desde el nombre del equipo
        cursor.execute("SELECT id FROM team WHERE name = %s", (data['team_name'],))
        team_result = cursor.fetchone()
        
        if not team_result:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado. Contacta al administrador.'
            }), 400
        
        team_id = team_result[0]
        
        # Obtener user_id desde la sesión (por ahora usamos 3 como ejemplo - test@example.com)
        # En una implementación completa, esto vendría del token de sesión
        user_id = 3  # TODO: Obtener del contexto de autenticación
        
        # Insertar empleado
        cursor.execute("""
            INSERT INTO employee (
                user_id, full_name, team_id, hours_monday_thursday, hours_friday,
                hours_summer, has_summer_schedule, summer_months,
                annual_vacation_days, annual_hld_hours, country, region, city,
                active, approved, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
            RETURNING id
        """, (
            user_id,
            data['full_name'],
            team_id,
            data['hours_monday_thursday'],
            data['hours_friday'],
            data.get('summer_hours'),
            data.get('has_summer_schedule', False),
            data.get('summer_months'),
            data['annual_vacation_days'],
            data['annual_free_hours'],
            data['country'],
            data.get('region'),
            data['city'],
            True,  # active
            False  # approved (requiere aprobación)
        ))
        
        employee_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Nuevo empleado registrado: {data['full_name']} (ID: {employee_id})")
        
        return jsonify({
            'success': True,
            'message': 'Empleado registrado exitosamente. Esperando aprobación del administrador.',
            'employee_id': employee_id
        })
        
    except Exception as e:
        logger.error(f"Error registrando empleado: {e}")
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500

@auth_simple_bp.route('/teams/create', methods=['POST'])
def create_team():
    """Crear nuevo equipo"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Nombre del equipo es requerido'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        
        # Verificar si el equipo ya existe
        cursor.execute("SELECT id FROM team WHERE name = %s", (data['name'].strip(),))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Ya existe un equipo con ese nombre'
            }), 400
        
        # Crear equipo
        cursor.execute("""
            INSERT INTO team (name, description, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
            RETURNING id
        """, (data['name'].strip(), data.get('description', '')))
        
        team_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Nuevo equipo creado: {data['name']} (ID: {team_id})")
        
        return jsonify({
            'success': True,
            'message': 'Equipo creado exitosamente',
            'team': {
                'id': team_id,
                'name': data['name'],
                'description': data.get('description', '')
            }
        })
        
    except Exception as e:
        logger.error(f"Error creando equipo: {e}")
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500

@auth_simple_bp.route('/test', methods=['GET'])
def test_auth():
    """Endpoint de prueba para verificar que el sistema funciona"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Sistema de autenticación funcionando correctamente',
                'database_connection': 'OK'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            }), 500
        
    except Exception as e:
        logger.error(f"Error en test: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
