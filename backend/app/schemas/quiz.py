# backend/app/schemas/quiz.py
"""
Purpose: Define serialization schema for Quizzes.
Responsibilities:
- Output multi-choice quiz parameters (question, 4 choices, correct choice, reason).
"""

from marshmallow import Schema, fields

class QuizSchema(Schema):
    id = fields.Int(dump_only=True)
    document_id = fields.Int(dump_only=True)
    question = fields.Str(dump_only=True)
    option_a = fields.Str(dump_only=True)
    option_b = fields.Str(dump_only=True)
    option_c = fields.Str(dump_only=True)
    option_d = fields.Str(dump_only=True)
    correct_answer = fields.Str(dump_only=True)
    explanation = fields.Str(dump_only=True)
