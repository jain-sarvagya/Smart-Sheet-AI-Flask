# backend/app/extensions.py
"""
Purpose: Initialize Flask extensions to avoid circular imports.
This module instantiates the core extensions (SQLAlchemy, JWT, Migrate, CORS, Marshmallow)
which will be attached to the Flask app factory during initialization.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
# pyrefly: ignore [missing-import]
from flask_marshmallow import Marshmallow

# Initialize extensions without binding to a specific app instance
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()
