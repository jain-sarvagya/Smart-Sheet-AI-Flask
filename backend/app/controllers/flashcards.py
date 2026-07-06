# backend/app/controllers/flashcards.py
"""
Purpose: Controller managing Flashcard operations.
Responsibilities:
- Verify document ownership and check if status is 'ready'.
- Check if flashcards are already generated (cached) to prevent duplicate API generation fees.
- Call GeminiService to generate a list of QA flashcards based on document text.
- Persist new flashcards into the database.
- Retrieve all generated flashcards for a specific document.
"""

from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.schemas.flashcard import FlashcardSchema
from app.services.gemini import GeminiService

flashcard_schema = FlashcardSchema(many=True)

@jwt_required()
def generate_flashcards(doc_id):
    """
    Generates study flashcards for a document.
    Returns existing ones if they have already been generated.
    """
    current_user_id = int(get_jwt_identity())
    
    # 1. Fetch document and verify ownership
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    if document.status != 'ready':
        return jsonify({"error": "Bad Request", "message": "Document is not ready for generation"}), 400

    # 2. Check if flashcards already exist (cache hit)
    existing_cards = Flashcard.query.filter_by(document_id=doc_id).all()
    if existing_cards:
        return jsonify({
            "message": "Flashcards retrieved from cache",
            "flashcards": flashcard_schema.dump(existing_cards)
        }), 200

    # 3. Concatenate document chunks for context input
    chunks = sorted(document.chunks, key=lambda c: c.chunk_index)
    if not chunks:
        return jsonify({"error": "Bad Request", "message": "No text content found for this document"}), 400

    full_text = "\n".join([chunk.chunk_text for chunk in chunks])

    # 4. Invoke Gemini API
    gemini_service = GeminiService(
        api_key=current_app.config['GEMINI_API_KEY'],
        model_name=current_app.config.get('GEMINI_MODEL', 'gemini-3.1-flash-lite')
    )
    current_app.logger.info(f"Triggering Gemini flashcard generation for Document ID {doc_id}")
    
    try:
        cards_data = gemini_service.generate_flashcards(full_text)
    except Exception as e:
        current_app.logger.error(f"Gemini flashcard generation failed: {e}")
        return jsonify({"error": "API Error", "message": f"Flashcard generation failed: {str(e)}"}), 502

    # 5. Persist to DB
    new_cards = []
    for item in cards_data:
        card = Flashcard(
            document_id=doc_id,
            question=item.get("question", "N/A"),
            answer=item.get("answer", "N/A"),
            difficulty=item.get("difficulty", "Medium")
        )
        db.session.add(card)
        new_cards.append(card)

    try:
        db.session.commit()
        return jsonify({
            "message": "Flashcards generated successfully",
            "flashcards": flashcard_schema.dump(new_cards)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server Error", "message": f"Failed to save flashcards: {str(e)}"}), 500

@jwt_required()
def get_flashcards(doc_id):
    """
    Fetches generated flashcards for a specific document.
    """
    current_user_id = int(get_jwt_identity())
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    cards = Flashcard.query.filter_by(document_id=doc_id).all()
    return jsonify({
        "flashcards": flashcard_schema.dump(cards)
    }), 200
