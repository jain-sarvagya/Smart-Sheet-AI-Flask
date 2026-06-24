# backend/app/routes/dashboard.py
"""
Purpose: Expose general user statistics dashboard endpoints.
Endpoints:
- GET / -> get_dashboard_stats
"""

from flask import Blueprint
from app.controllers.dashboard import get_dashboard_stats

dashboard_bp = Blueprint('dashboard', __name__)

dashboard_bp.route('/', methods=['GET'])(get_dashboard_stats)
