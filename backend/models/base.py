"""
Base module for SQLAlchemy database instance.
This ensures a single instance of db is used across all models.
"""
from flask_sqlalchemy import SQLAlchemy

# Single instance of SQLAlchemy
db = SQLAlchemy()

