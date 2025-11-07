#!/usr/bin/env python3
"""Script para resetear contraseña de usuario"""
import sys
from flask_security.utils import hash_password
from models import db, User
from main import create_app

def reset_password(email, new_password):
    """Resetear contraseña de un usuario"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Usuario {email} no encontrado")
            return False
        
        # Hashear la nueva contraseña
        hashed_password = hash_password(new_password)
        user.password = hashed_password
        
        # Guardar cambios
        db.session.commit()
        
        print(f"✅ Contraseña actualizada para {email}")
        print(f"   Nueva contraseña: {new_password}")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python reset_password.py <email> <nueva_contraseña>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    reset_password(email, password)

