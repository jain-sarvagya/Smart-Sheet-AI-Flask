# backend/tests/conftest.py
"""
Purpose: Pytest configuration file.
Responsibilities:
- Override DATABASE_URL environment variable to in-memory SQLite BEFORE any test modules are loaded.
This prevents import-ordering issues from evaluating the local production PostgreSQL configuration.
"""

import os
# Force in-memory SQLite database URI for all tests globally
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'development'
