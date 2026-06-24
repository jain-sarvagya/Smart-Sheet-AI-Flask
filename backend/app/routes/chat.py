# backend/app/routes/chat.py
"""
Purpose: Expose Chat chatbot endpoints.
Endpoints:
- POST /<doc_id> -> query_chatbot
- GET /<doc_id> -> get_chat_history
"""

from flask import Blueprint
from app.controllers.chat import query_chatbot, get_chat_history

chat_bp = Blueprint('chat', __name__)

chat_bp.route('/<int:doc_id>', methods=['POST'])(query_chatbot)
chat_bp.route('/<int:doc_id>', methods=['GET'])(get_chat_history)
