# backend/app/models/__init__.py
"""
Purpose: Expose all database models in a single module.
This allows SQLAlchemy and Flask-Migrate to detect all models when initializing,
and enables cleaner imports throughout the codebase.
"""

from app.models.user import User
from app.models.document import Document
from app.models.chunk import Chunk
from app.models.summary import Summary
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz
from app.models.explanation import ConceptExplanation
from app.models.chat import ChatMessage

__all__ = [
    'User',
    'Document',
    'Chunk',
    'Summary',
    'Flashcard',
    'Quiz',
    'ConceptExplanation',
    'ChatMessage'
]
