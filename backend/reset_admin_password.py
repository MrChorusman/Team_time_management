#!/usr/bin/env python3
"""
Script para resetear la contraseña del admin usando Flask-Security-Too
"""
import os
import sys

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from models.user import User, db
from flask_security.utils import hash_password

def reset_admin_password():
    """Resetear contraseña del admin"""
    app = create_app()
    
    with app.app_context():
        admin_user = User.query.filter_by(email='admin@teamtime.com').first()
        
        if not admin_user:
            print("❌ Usuario admin no encontrado")
            return False
        
        # Nueva contraseña
        new_password = "Admin2025!"
        
        # Generar hash usando Flask-Security-Too
        password_hash = hash_password(new_password)
        
        # Actualizar contraseña
        admin_user.password = password_hash
        db.session.commit()
        
        print("✅ Contraseña del admin actualizada exitosamente")
        print(f"📧 Email: {admin_user.email}")
        print(f"🔐 Contraseña: {new_password}")
        print(f"🔑 Hash: {password_hash[:50]}...")
        
        return True

if __name__ == '__main__':
    try:
        reset_admin_password()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

