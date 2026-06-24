# backend/app/models/document.py
"""
Purpose: Define the Document model for uploaded PDF metadata.
Responsibilities:
- Store document details (title, file URL, status, total pages).
- Establish relationships to the User owner and child learning assets.
- Support status track: processing, ready, failed.
"""

from datetime import datetime, timezone
from app.extensions import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='processing', nullable=False)  # processing, ready, failed
    total_pages = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Bidirectional relationships
    user = db.relationship('User', back_populates='documents')
    chunks = db.relationship('Chunk', back_populates='document', cascade='all, delete-orphan', lazy=True)
    summaries = db.relationship('Summary', back_populates='document', cascade='all, delete-orphan', lazy=True)
    flashcards = db.relationship('Flashcard', back_populates='document', cascade='all, delete-orphan', lazy=True)
    quizzes = db.relationship('Quiz', back_populates='document', cascade='all, delete-orphan', lazy=True)
    explanations = db.relationship('ConceptExplanation', back_populates='document', cascade='all, delete-orphan', lazy=True)
    chat_messages = db.relationship('ChatMessage', back_populates='document', cascade='all, delete-orphan', lazy=True)

    def __init__(self, user_id=None, title=None, file_url=None, status=None, total_pages=None, **kwargs):
        if user_id is not None:
            kwargs['user_id'] = user_id
        if title is not None:
            kwargs['title'] = title
        if file_url is not None:
            kwargs['file_url'] = file_url
        if status is not None:
            kwargs['status'] = status
        if total_pages is not None:
            kwargs['total_pages'] = total_pages
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Document {self.title} ({self.status})>"
