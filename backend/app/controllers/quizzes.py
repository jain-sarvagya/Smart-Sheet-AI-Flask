# backend/app/controllers/quizzes.py
"""
Purpose: Controller managing Quiz operations.
Responsibilities:
- Verify document ownership and check if status is 'ready'.
- Check if quizzes are already generated (cached) to prevent duplicate API generation fees.
- Call GeminiService to generate a list of multiple choice questions based on document text.
- Persist new quizzes into the database.
- Retrieve all generated quizzes for a specific document.
"""

from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.document import Document
from app.models.quiz import Quiz
from app.schemas.quiz import QuizSchema
from app.services.gemini import GeminiService

quiz_schema = QuizSchema(many=True)

@jwt_required()
def generate_quizzes(doc_id):
    """
    Generates understanding test quizzes for a document.
    Returns existing ones if they have already been generated.
    """
    current_user_id = int(get_jwt_identity())
    
    # 1. Fetch document and verify ownership
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    if document.status != 'ready':
        return jsonify({"error": "Bad Request", "message": "Document is not ready for generation"}), 400

    # Retrieve requested count from request body or query parameter (default to 5)
    from flask import request
    req_data = request.get_json(silent=True) or {}
    count = req_data.get('count') or request.args.get('count', 5, type=int)
    try:
        count = int(count)
        if count < 3: count = 3
        if count > 15: count = 15
    except (TypeError, ValueError):
        count = 5

    # 2. Delete existing quizzes for this document to generate a fresh set
    try:
        Quiz.query.filter_by(document_id=doc_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f"Could not clear old quizzes: {e}")

    # 3. Concatenate document chunks for context input
    chunks = sorted(document.chunks, key=lambda c: c.chunk_index)
    if not chunks:
        return jsonify({"error": "Bad Request", "message": "No text content found for this document"}), 400

    full_text = "\n".join([chunk.chunk_text for chunk in chunks])

    # 4. Invoke Gemini API
    gemini_service = GeminiService(
        api_key=current_app.config['GEMINI_API_KEY'],
        model_name=current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
    )
    current_app.logger.info(f"Triggering Gemini quiz generation for Document ID {doc_id} with count {count}")
    
    try:
        quizzes_data = gemini_service.generate_quizzes(full_text, count=count)
    except Exception as e:
        current_app.logger.error(f"Gemini quiz generation failed: {e}")
        return jsonify({"error": "API Error", "message": f"Quiz generation failed: {str(e)}"}), 502

    # 5. Persist to DB
    new_quizzes = []
    for item in quizzes_data:
        quiz_item = Quiz(
            document_id=doc_id,
            question=item.get("question", "N/A"),
            option_a=item.get("option_a", "N/A"),
            option_b=item.get("option_b", "N/A"),
            option_c=item.get("option_c", "N/A"),
            option_d=item.get("option_d", "N/A"),
            correct_answer=item.get("correct_answer", "A"),
            explanation=item.get("explanation", "No explanation provided.")
        )
        db.session.add(quiz_item)
        new_quizzes.append(quiz_item)

    try:
        db.session.commit()
        return jsonify({
            "message": "Quizzes generated successfully",
            "quizzes": quiz_schema.dump(new_quizzes)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server Error", "message": f"Failed to save quizzes: {str(e)}"}), 500

@jwt_required()
def get_quizzes(doc_id):
    """
    Fetches generated quizzes for a specific document.
    """
    current_user_id = int(get_jwt_identity())
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    quizzes = Quiz.query.filter_by(document_id=doc_id).all()
    return jsonify({
        "quizzes": quiz_schema.dump(quizzes)
    }), 200
