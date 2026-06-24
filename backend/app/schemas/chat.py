# backend/app/schemas/chat.py
"""
Purpose: Define serialization schema for ChatMessage.
Responsibilities:
- Output scrolling message histories for chatbot queries.
"""

from marshmallow import Schema, fields

class ChatMessageSchema(Schema):
    id = fields.Int(dump_only=True)
    document_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    sender = fields.Str(dump_only=True)
    message = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
