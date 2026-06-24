# backend/app/models/chunk.py
"""
Purpose: Define the Chunk model for PDF content chunks.
Responsibilities:
- Store document text fragments for fine-grained retrieval.
- Hold sequential index for reconstructed reads.
- Store optional embedding JSON array of float values for semantic search.
"""

from app.extensions import db

class Chunk(db.Model):
    __tablename__ = 'chunks'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    embedding = db.Column(db.JSON, nullable=True)  # List of floats for cosine similarity in Python

    # Bidirectional relationship
    document = db.relationship('Document', back_populates='chunks')

    def __init__(self, document_id=None, chunk_text=None, chunk_index=None, embedding=None, **kwargs):
        if document_id is not None:
            kwargs['document_id'] = document_id
        if chunk_text is not None:
            kwargs['chunk_text'] = chunk_text
        if chunk_index is not None:
            kwargs['chunk_index'] = chunk_index
        if embedding is not None:
            kwargs['embedding'] = embedding
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Chunk {self.document_id} [Index {self.chunk_index}]>"
