# backend/app/models/user.py
"""
Purpose: Define the User model for database persistence.
Responsibilities:
- Store user details (name, email, hashed password).
- Provide helper methods for password hashing and verification.
- Establish relationships with uploaded documents and chat messages.
"""

from datetime import datetime, timezone
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships - cascade deletes ensure that when a user is deleted, all their data is cleaned up
    documents = db.relationship('Document', back_populates='user', cascade='all, delete-orphan', lazy=True)
    chat_messages = db.relationship('ChatMessage', back_populates='user', cascade='all, delete-orphan', lazy=True)

    def __init__(self, name=None, email=None, password_hash=None, **kwargs):
        if name is not None:
            kwargs['name'] = name
        if email is not None:
            kwargs['email'] = email
        if password_hash is not None:
            kwargs['password_hash'] = password_hash
        super().__init__(**kwargs)

    def set_password(self, password):
        """Hashes the password and sets password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies input password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
