# backend/app/routes/summaries.py
"""
Purpose: Expose Summary generation and retrieval endpoints.
Endpoints:
- POST /generate/<doc_id> -> generate_summary
- GET /<doc_id> -> get_summary
"""

from flask import Blueprint
from app.controllers.summaries import generate_summary, get_summary

summary_bp = Blueprint('summaries', __name__)

summary_bp.route('/generate/<int:doc_id>', methods=['POST'])(generate_summary)
summary_bp.route('/<int:doc_id>', methods=['GET'])(get_summary)
