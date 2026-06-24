# backend/run.py
"""
Purpose: Run entrypoint for the Flask backend application.
Responsibilities:
- Create the app instance via application factory.
- Define basic CLI shell context to easily inspect database models.
- Run the development server when executed directly.
"""

import os
from app import create_app, db
from app.models import User, Document, Chunk, Summary, Flashcard, Quiz, ConceptExplanation, ChatMessage

app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Automatically create tables in development/local setups
with app.app_context():
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    """Expose database and models directly to the flask shell CLI."""
    return {
        'db': db,
        'User': User,
        'Document': Document,
        'Chunk': Chunk,
        'Summary': Summary,
        'Flashcard': Flashcard,
        'Quiz': Quiz,
        'ConceptExplanation': ConceptExplanation,
        'ChatMessage': ChatMessage
    }

if __name__ == '__main__':
    # Default Flask port is 5000
    app.run(host='0.0.0.0', port=5000)
