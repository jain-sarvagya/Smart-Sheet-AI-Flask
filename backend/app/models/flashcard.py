# backend/app/models/flashcard.py
"""
Purpose: Define the Flashcard model for AI-generated card study assets.
Responsibilities:
- Store card question and answer prompt values.
- Store difficulty flag levels (Easy, Medium, Hard).
- Relate back to source Document.
"""

from app.extensions import db

class Flashcard(db.Model):
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='Medium', nullable=False)  # Easy, Medium, Hard

    # Bidirectional relationship
    document = db.relationship('Document', back_populates='flashcards')

    def __init__(self, document_id=None, question=None, answer=None, difficulty=None, **kwargs):
        if document_id is not None:
            kwargs['document_id'] = document_id
        if question is not None:
            kwargs['question'] = question
        if answer is not None:
            kwargs['answer'] = answer
        if difficulty is not None:
            kwargs['difficulty'] = difficulty
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Flashcard {self.id} [Difficulty: {self.difficulty}]>"
