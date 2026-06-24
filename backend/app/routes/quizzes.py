# backend/app/routes/quizzes.py
"""
Purpose: Expose Quiz generation and retrieval endpoints.
Endpoints:
- POST /generate/<doc_id> -> generate_quizzes
- GET /<doc_id> -> get_quizzes
"""

from flask import Blueprint
from app.controllers.quizzes import generate_quizzes, get_quizzes

quiz_bp = Blueprint('quizzes', __name__)

quiz_bp.route('/generate/<int:doc_id>', methods=['POST'])(generate_quizzes)
quiz_bp.route('/<int:doc_id>', methods=['GET'])(get_quizzes)
