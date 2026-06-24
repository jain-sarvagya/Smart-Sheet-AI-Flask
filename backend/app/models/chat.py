# backend/app/models/chat.py
"""
Purpose: Define the ChatMessage model for the document-grounded chatbot history.
Responsibilities:
- Store message author sender role (user or assistant).
- Store textual message contents.
- Keep track of timestamps for chronological listing.
"""

from datetime import datetime, timezone
from app.extensions import db

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Bidirectional relationships
    document = db.relationship('Document', back_populates='chat_messages')
    user = db.relationship('User', back_populates='chat_messages')

    def __init__(self, document_id=None, user_id=None, sender=None, message=None, **kwargs):
        if document_id is not None:
            kwargs['document_id'] = document_id
        if user_id is not None:
            kwargs['user_id'] = user_id
        if sender is not None:
            kwargs['sender'] = sender
        if message is not None:
            kwargs['message'] = message
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ChatMessage {self.id} [Sender: {self.sender}]>"
