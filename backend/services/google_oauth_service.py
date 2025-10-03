from flask import current_app, session, redirect, url_for
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
import logging
from typing import Dict, Optional, Tuple

from models.user import User, Role, db

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Servicio para manejar autenticación con Google OAuth 2.0"""
    
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        self.flow = None
    
    def init_app(self, app):
        """Inicializa el servicio con la aplicación Flask"""
        self.client_id = app.config.get('GOOGLE_CLIENT_ID')
        self.client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = app.config.get('GOOGLE_REDIRECT_URI')
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("Google OAuth no configurado completamente")
            return
        
        # Configurar OAuth flow
        self.flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=[
                'openid',
                'email',
                'profile'
            ]
        )
        self.flow.redirect_uri = self.redirect_uri
    
    def is_configured(self) -> bool:
        """Verifica si Google OAuth está configurado"""
        return all([self.client_id, self.client_secret, self.redirect_uri, self.flow])
    
    def get_auth_url(self) -> str:
        """Genera la URL de autorización de Google"""
        if not self.is_configured():
            raise ValueError("Google OAuth no está configurado")
        
        # Generar URL de autorización
        auth_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Guardar state en la sesión para verificación
        session['oauth_state'] = state
        
        return auth_url
    
    def handle_callback(self, code: str, state: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Maneja el callback de Google OAuth
        
        Returns:
            Tuple[success, message, user_data]
        """
        if not self.is_configured():
            return False, "Google OAuth no está configurado", None
        
        # Verificar state
        if session.get('oauth_state') != state:
            logger.error("Estado OAuth no coincide")
            return False, "Error de seguridad en la autenticación", None
        
        try:
            # Intercambiar código por token
            self.flow.fetch_token(code=code)
            
            # Obtener información del usuario
            credentials = self.flow.credentials
            request_session = requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request_session, self.client_id
            )
            
            # Extraer información del usuario
            google_id = id_info['sub']
            email = id_info['email']
            name = id_info.get('name', '')
            given_name = id_info.get('given_name', '')
            family_name = id_info.get('family_name', '')
            picture = id_info.get('picture', '')
            
            # Limpiar state de la sesión
            session.pop('oauth_state', None)
            
            # Buscar o crear usuario
            user = self._find_or_create_user(
                google_id=google_id,
                email=email,
                name=name,
                given_name=given_name,
                family_name=family_name,
                picture=picture
            )
            
            if user:
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'name': user.full_name,
                    'picture': getattr(user, 'google_picture', None),
                    'google_id': getattr(user, 'google_id', None)
                }
                return True, "Autenticación exitosa", user_data
            else:
                return False, "Error creando o encontrando usuario", None
                
        except Exception as e:
            logger.error(f"Error en callback de Google OAuth: {e}")
            return False, f"Error en autenticación: {str(e)}", None
    
    def _find_or_create_user(self, google_id: str, email: str, name: str, 
                           given_name: str, family_name: str, picture: str) -> Optional[User]:
        """
        Busca un usuario existente o crea uno nuevo basado en información de Google
        """
        try:
            # Buscar usuario existente por email
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Actualizar información de Google si no existe
                if not hasattr(user, 'google_id') or not user.google_id:
                    # Agregar campos de Google si no existen
                    self._add_google_fields_to_user(user)
                
                # Actualizar información
                user.google_id = google_id
                user.google_picture = picture
                if not user.first_name and given_name:
                    user.first_name = given_name
                if not user.last_name and family_name:
                    user.last_name = family_name
                
                db.session.commit()
                logger.info(f"Usuario existente actualizado con datos de Google: {email}")
                
            else:
                # Crear nuevo usuario
                user = self._create_user_from_google(
                    google_id=google_id,
                    email=email,
                    name=name,
                    given_name=given_name,
                    family_name=family_name,
                    picture=picture
                )
                
                if user:
                    logger.info(f"Nuevo usuario creado desde Google: {email}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error buscando/creando usuario: {e}")
            db.session.rollback()
            return None
    
    def _add_google_fields_to_user(self, user: User):
        """Agrega campos de Google al modelo de usuario si no existen"""
        # Esto requeriría una migración de base de datos
        # Por ahora, usamos campos existentes o agregamos nuevos campos
        if not hasattr(user, 'google_id'):
            # En una implementación real, esto requeriría una migración
            # Por ahora, usamos el campo username para almacenar google_id
            user.username = getattr(user, 'google_id', None)
    
    def _create_user_from_google(self, google_id: str, email: str, name: str,
                                given_name: str, family_name: str, picture: str) -> Optional[User]:
        """Crea un nuevo usuario basado en información de Google"""
        try:
            # Obtener rol por defecto
            viewer_role = Role.query.filter_by(name='viewer').first()
            if not viewer_role:
                logger.error("Rol 'viewer' no encontrado")
                return None
            
            # Crear nuevo usuario
            new_user = User(
                email=email,
                password='',  # Sin contraseña para usuarios OAuth
                first_name=given_name or name.split()[0] if name else '',
                last_name=family_name or ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                active=True,
                confirmed_at=db.func.now(),  # Confirmar automáticamente
                username=google_id  # Usar google_id como username temporal
            )
            
            # Asignar rol
            new_user.roles.append(viewer_role)
            
            db.session.add(new_user)
            db.session.commit()
            
            return new_user
            
        except Exception as e:
            logger.error(f"Error creando usuario desde Google: {e}")
            db.session.rollback()
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoca un token de Google"""
        try:
            from google_auth_oauthlib.flow import Flow
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }
            )
            
            # Revocar token
            flow.revoke_token(token)
            return True
            
        except Exception as e:
            logger.error(f"Error revocando token: {e}")
            return False
    
    def get_user_info_from_token(self, token: str) -> Optional[Dict]:
        """Obtiene información del usuario desde un token"""
        try:
            request_session = requests.Request()
            id_info = id_token.verify_oauth2_token(token, request_session, self.client_id)
            
            return {
                'sub': id_info['sub'],
                'email': id_info['email'],
                'name': id_info.get('name', ''),
                'given_name': id_info.get('given_name', ''),
                'family_name': id_info.get('family_name', ''),
                'picture': id_info.get('picture', '')
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información del usuario: {e}")
            return None
