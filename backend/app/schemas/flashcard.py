# backend/app/schemas/flashcard.py
"""
Purpose: Define serialization schema for Flashcards.
Responsibilities:
- Output card lists detailing questions, answers, and study difficulties.
"""

from marshmallow import Schema, fields

class FlashcardSchema(Schema):
    id = fields.Int(dump_only=True)
    document_id = fields.Int(dump_only=True)
    question = fields.Str(dump_only=True)
    answer = fields.Str(dump_only=True)
    difficulty = fields.Str(dump_only=True)
