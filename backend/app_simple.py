import os
from flask import Flask, jsonify

def create_app(config_name=None):
    """Factory function to create Flask app"""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'dev-salt')
    
    # CORS básico
    from flask_cors import CORS
    CORS(app, origins=['*'])
    
    @app.route('/')
    def hello():
        return jsonify({
            'message': 'Team Time Management API',
            'status': 'running',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'message': 'API is healthy',
            'timestamp': str(datetime.now())
        })
    
    return app

# Crear aplicación
app = create_app()

if __name__ == '__main__':
    from datetime import datetime
    app.run(host='0.0.0.0', port=5000, debug=True)