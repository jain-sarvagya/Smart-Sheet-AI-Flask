# backend/app/routes/flashcards.py
"""
Purpose: Expose Flashcard generation and retrieval endpoints.
Endpoints:
- POST /generate/<doc_id> -> generate_flashcards
- GET /<doc_id> -> get_flashcards
"""

from flask import Blueprint
from app.controllers.flashcards import generate_flashcards, get_flashcards

flashcard_bp = Blueprint('flashcards', __name__)

flashcard_bp.route('/generate/<int:doc_id>', methods=['POST'])(generate_flashcards)
flashcard_bp.route('/<int:doc_id>', methods=['GET'])(get_flashcards)
