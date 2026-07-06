# backend/app/config.py
"""
Purpose: Centralize application configuration loading from environment variables.
Responsibilities:
- Load environment variables from .env file.
- Provide configuration schemas for Development and Production environments.
- Enforce secure defaults and limits (e.g. upload file size).
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Clear conflicting system environment variables to prevent ADC override
os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
os.environ.pop('GOOGLE_API_KEY', None)

class Config:
    """Base Configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_change_in_production')
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_jwt_secret_key_change_in_production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Token validity period

    # Database Settings (Default fallback to SQLite if Postgres url is missing or fails)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI:
        # Render may provide 'postgres://' or 'postgresql://' prefix. We normalize to 'postgresql+pg8000://'.
        if SQLALCHEMY_DATABASE_URI.startswith("postgresql://"):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+pg8000://", 1)
        elif SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql+pg8000://", 1)
    else:
        # Construct path for local SQLite db
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'smart_sheet.db'))
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    # Storage Settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024)) # 100 MB

    # ImageKit configuration
    IMAGEKIT_PUBLIC_KEY = os.environ.get('IMAGEKIT_PUBLIC_KEY', '').strip() or None
    IMAGEKIT_PRIVATE_KEY = os.environ.get('IMAGEKIT_PRIVATE_KEY', '').strip() or None
    IMAGEKIT_URL_ENDPOINT = os.environ.get('IMAGEKIT_URL_ENDPOINT', '').strip() or None

    # Gemini AI configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip() or None
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.1-flash-lite').strip()

class DevelopmentConfig(Config):
    """Development Configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production Configuration."""
    DEBUG = False
    # Ensure production environment enforces strict settings (like actual PostgreSQL)
    # and has a real secret key
    
# Map configuration classes
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
