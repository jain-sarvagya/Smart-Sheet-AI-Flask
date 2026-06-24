# backend/app/controllers/explanations.py
"""
Purpose: Controller managing ConceptExplanation operations.
Responsibilities:
- Verify document ownership.
- Cache check: return existing definition if already explained for this document.
- Use RAGEngine similarity to fetch top document chunks related to the concept.
- Invoke GeminiService to explain the concept based strictly on the retrieved context.
- Persist new concept definitions in database.
- Retrieve explanation history for a document.
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.document import Document
from app.models.explanation import ConceptExplanation
from app.schemas.explanation import ConceptExplanationSchema
from app.services.rag import RAGEngine
from app.services.gemini import GeminiService

explanation_schema = ConceptExplanationSchema()
explanations_schema = ConceptExplanationSchema(many=True)

@jwt_required()
def explain_concept(doc_id):
    """
    Generates a grounded explanation for a specific concept term.
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get("concept_name"):
        return jsonify({"error": "Bad Request", "message": "Missing concept_name in request body"}), 400

    concept_name = data.get("concept_name").strip()

    # 1. Fetch document and verify ownership
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    if document.status != 'ready':
        return jsonify({"error": "Bad Request", "message": "Document is not ready for explanations"}), 400

    # 2. Check if concept was already explained (cache hit)
    existing_explanation = ConceptExplanation.query.filter_by(
        document_id=doc_id, 
        concept_name=concept_name
    ).first()
    
    if existing_explanation:
        return jsonify({
            "message": "Explanation retrieved from cache",
            "explanation": explanation_schema.dump(existing_explanation)
        }), 200

    # 3. Retrieve relevant chunks using RAG retrieval (top 4 chunks)
    rag_engine = RAGEngine(
        api_key=current_app.config['GEMINI_API_KEY'],
        chat_model=current_app.config.get('GEMINI_MODEL', 'gemini-3.1-flash-lite')
    )
    relevant_chunks = rag_engine.retrieve_context(concept_name, document.chunks, top_k=4)
    
    if not relevant_chunks:
        return jsonify({"error": "Bad Request", "message": "No document content available to analyze concept."}), 400

    context_str = "\n\n".join([f"[Segment]: {c.chunk_text}" for c in relevant_chunks])

    # 4. Generate grounded explanation
    gemini_service = GeminiService(
        api_key=current_app.config['GEMINI_API_KEY'],
        model_name=current_app.config.get('GEMINI_MODEL', 'gemini-3.1-flash-lite')
    )
    explanation_text = gemini_service.generate_concept_explanation(concept_name, context_str)

    # 5. Persist to DB
    explanation = ConceptExplanation(
        document_id=doc_id,
        concept_name=concept_name,
        explanation=explanation_text
    )

    try:
        db.session.add(explanation)
        db.session.commit()
        return jsonify({
            "message": "Concept explained successfully",
            "explanation": explanation_schema.dump(explanation)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server Error", "message": f"Failed to save explanation: {str(e)}"}), 500

@jwt_required()
def get_explanations(doc_id):
    """
    Retrieves explanation history for a document.
    """
    current_user_id = int(get_jwt_identity())
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    explanations = ConceptExplanation.query.filter_by(document_id=doc_id).order_by(ConceptExplanation.created_at.desc()).all()
    return jsonify({
        "explanations": explanations_schema.dump(explanations)
    }), 200
