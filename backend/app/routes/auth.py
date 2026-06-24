# backend/app/routes/auth.py
"""
Purpose: Expose authentication endpoints via Flask Blueprint.
Endpoints:
- POST /register -> register_user
- POST /login -> login_user
- GET /profile -> get_profile
"""

from flask import Blueprint
from app.controllers.auth import register_user, login_user, get_profile

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register', methods=['POST'])(register_user)
auth_bp.route('/login', methods=['POST'])(login_user)
auth_bp.route('/profile', methods=['GET'])(get_profile)
