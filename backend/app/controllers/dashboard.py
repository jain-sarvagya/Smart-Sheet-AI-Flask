# backend/app/controllers/dashboard.py
"""
Purpose: Controller managing general user statistics dashboard.
Responsibilities:
- Compute total count of uploaded documents.
- Compute total count of flashcards created.
- Compute total count of quizzes created.
- Fetch list of recent document uploads along with their status details.
"""

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz
from app.schemas.document import DocumentSchema

document_schema = DocumentSchema(many=True)

@jwt_required()
def get_dashboard_stats():
    """
    Compiles aggregate counts and lists recent activity details.
    """
    current_user_id = int(get_jwt_identity())

    try:
        # 1. Total Documents
        total_documents = Document.query.filter_by(user_id=current_user_id).count()

        # 2. Total Flashcards (Joining on Document user ownership)
        total_flashcards = db.session.query(db.func.count(Flashcard.id))\
            .join(Document, Flashcard.document_id == Document.id)\
            .filter(Document.user_id == current_user_id).scalar() or 0

        # 3. Total Quizzes (Joining on Document user ownership)
        total_quizzes = db.session.query(db.func.count(Quiz.id))\
            .join(Document, Quiz.document_id == Document.id)\
            .filter(Document.user_id == current_user_id).scalar() or 0

        # 4. Fetch 5 most recent documents
        recent_documents = Document.query.filter_by(user_id=current_user_id)\
            .order_by(Document.created_at.desc()).limit(5).all()

        return jsonify({
            "stats": {
                "total_documents": total_documents,
                "total_flashcards": total_flashcards,
                "total_quizzes": total_quizzes
            },
            "recent_uploads": document_schema.dump(recent_documents)
        }), 200

    except Exception as e:
        return jsonify({"error": "Server Error", "message": f"Failed to load dashboard: {str(e)}"}), 500
