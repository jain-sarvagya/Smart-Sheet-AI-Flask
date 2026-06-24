# backend/app/routes/explanations.py
"""
Purpose: Expose ConceptExplanation generation and retrieval endpoints.
Endpoints:
- POST /explain/<doc_id> -> explain_concept
- GET /<doc_id> -> get_explanations
"""

from flask import Blueprint
from app.controllers.explanations import explain_concept, get_explanations

explanation_bp = Blueprint('explanations', __name__)

explanation_bp.route('/explain/<int:doc_id>', methods=['POST'])(explain_concept)
explanation_bp.route('/<int:doc_id>', methods=['GET'])(get_explanations)
