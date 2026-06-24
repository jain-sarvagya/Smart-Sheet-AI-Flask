# backend/app/models/summary.py
"""
Purpose: Define the Summary model for storing AI-generated document summaries.
Responsibilities:
- Store short, punchy overview summary.
- Store detailed structured narrative summary.
- Store JSON-based array of bulleted key takeaways.
"""

from app.extensions import db

class Summary(db.Model):
    __tablename__ = 'summaries'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    short_summary = db.Column(db.Text, nullable=False)
    detailed_summary = db.Column(db.Text, nullable=False)
    key_takeaways = db.Column(db.JSON, nullable=False)  # Array of strings

    # Bidirectional relationship
    document = db.relationship('Document', back_populates='summaries')

    def __init__(self, document_id=None, short_summary=None, detailed_summary=None, key_takeaways=None, **kwargs):
        if document_id is not None:
            kwargs['document_id'] = document_id
        if short_summary is not None:
            kwargs['short_summary'] = short_summary
        if detailed_summary is not None:
            kwargs['detailed_summary'] = detailed_summary
        if key_takeaways is not None:
            kwargs['key_takeaways'] = key_takeaways
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Summary for Document {self.document_id}>"
