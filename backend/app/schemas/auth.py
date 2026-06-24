# backend/app/schemas/auth.py
"""
Purpose: Define data validation and serialization schemas for Authentication.
Responsibilities:
- Validate Register payloads (name, email, password length).
- Validate Login payloads (email formatting, password existence).
- Serialize User profiles, excluding password hashes.
"""

from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=50))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
