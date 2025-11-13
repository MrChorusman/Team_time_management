#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import create_app
from flask_security.utils import hash_password

app = create_app()
with app.app_context():
    password = sys.argv[1] if len(sys.argv) > 1 else 'Prueba123456'
    hashed = hash_password(password)
    print(hashed)

