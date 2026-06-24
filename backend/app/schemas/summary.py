# backend/app/schemas/summary.py
"""
Purpose: Define serialization schema for Summaries.
Responsibilities:
- Output generated summary segments.
- Automatically serialize the key_takeaways JSON array field as a list of strings.
"""

from marshmallow import Schema, fields

class SummarySchema(Schema):
    id = fields.Int(dump_only=True)
    document_id = fields.Int(dump_only=True)
    short_summary = fields.Str(dump_only=True)
    detailed_summary = fields.Str(dump_only=True)
    key_takeaways = fields.List(fields.Str(), dump_only=True)
