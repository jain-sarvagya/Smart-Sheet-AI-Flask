# backend/app/schemas/explanation.py
"""
Purpose: Define serialization schema for ConceptExplanations.
Responsibilities:
- Output concept definitions generated from document searches.
"""

from marshmallow import Schema, fields

class ConceptExplanationSchema(Schema):
    id = fields.Int(dump_only=True)
    document_id = fields.Int(dump_only=True)
    concept_name = fields.Str(dump_only=True)
    explanation = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
