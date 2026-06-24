# backend/app/extensions.py
"""
Purpose: Initialize Flask extensions to avoid circular imports.
This module instantiates the core extensions (SQLAlchemy, JWT, Migrate, CORS, Marshmallow)
which will be attached to the Flask app factory during initialization.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_marshmallow import Marshmallow

class BaseModel(Model):
    """Custom Base Model to support explicit type checking / dynamic constructors."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Initialize extensions without binding to a specific app instance
db = SQLAlchemy(model_class=BaseModel)
jwt = JWTManager()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()

