# backend/app/models/explanation.py
"""
Purpose: Define the ConceptExplanation model for storing AI explanations.
Responsibilities:
- Store the concept term or prompt requested by the user.
- Store the grounded AI-generated explanation.
- Relate back to the parent Document.
"""

from datetime import datetime, timezone
from app.extensions import db

class ConceptExplanation(db.Model):
    __tablename__ = 'concept_explanations'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    concept_name = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Bidirectional relationship
    document = db.relationship('Document', back_populates='explanations')

    def __init__(self, document_id=None, concept_name=None, explanation=None, **kwargs):
        if document_id is not None:
            kwargs['document_id'] = document_id
        if concept_name is not None:
            kwargs['concept_name'] = concept_name
        if explanation is not None:
            kwargs['explanation'] = explanation
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ConceptExplanation '{self.concept_name}' (Doc: {self.document_id})>"
