# backend/app/models/quiz.py
"""
Purpose: Define the Quiz model for AI-generated multiple-choice questions.
Responsibilities:
- Store quiz question text.
- Store four distinct answers options (A, B, C, D).
- Store the correct answer flag letter (A, B, C, or D).
- Store the AI-generated pedagogical explanation for the correct answer.
"""

from app.extensions import db

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    explanation = db.Column(db.Text, nullable=False)

    # Bidirectional relationship
    document = db.relationship('Document', back_populates='quizzes')

    def __init__(self, document_id=None, question=None, option_a=None, option_b=None, option_c=None, option_d=None, correct_answer=None, explanation=None, **kwargs):
        if document_id is not None:
            kwargs['document_id'] = document_id
        if question is not None:
            kwargs['question'] = question
        if option_a is not None:
            kwargs['option_a'] = option_a
        if option_b is not None:
            kwargs['option_b'] = option_b
        if option_c is not None:
            kwargs['option_c'] = option_c
        if option_d is not None:
            kwargs['option_d'] = option_d
        if correct_answer is not None:
            kwargs['correct_answer'] = correct_answer
        if explanation is not None:
            kwargs['explanation'] = explanation
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Quiz {self.id} (Doc: {self.document_id})>"
