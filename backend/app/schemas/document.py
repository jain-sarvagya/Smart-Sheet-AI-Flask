# backend/app/schemas/document.py
"""
Purpose: Define data serialization schemas for Documents.
Responsibilities:
- Serialize uploaded document metadata (title, URL, total pages, status).
- Expose timestamp records.
"""

from marshmallow import Schema, fields

class DocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    file_url = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    total_pages = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
