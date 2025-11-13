# Middleware para mejorar compatibilidad con móviles
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

def init_mobile_compatibility(app):
    """Inicializa mejoras de compatibilidad para dispositivos móviles"""
    
    @app.after_request
    def add_mobile_headers(response):
        """Agrega headers útiles para dispositivos móviles"""
        # Headers para mejorar compatibilidad con proxies móviles
        origin = request.headers.get('Origin')
        if origin:
            # Verificar si el origen está en la lista permitida
            allowed_origins = app.config.get('CORS_ORIGINS', [])
            if origin in allowed_origins or '*' in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        # Headers adicionales para móviles
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Origin, Accept'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        # Headers de seguridad mejorados para móviles
        if request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    @app.before_request
    def handle_preflight():
        """Maneja peticiones OPTIONS (preflight) de CORS"""
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.status_code = 200
            return response
