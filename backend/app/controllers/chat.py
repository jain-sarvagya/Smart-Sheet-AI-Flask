# backend/app/controllers/chat.py
"""
Purpose: Controller managing document-aware chatbot dialogue.
Responsibilities:
- Verify document ownership.
- Fetch conversation history for current user/document.
- Delegate query, chunks, and history to RAGEngine.
- Persist both user prompt and assistant response to database.
- Return assistant message structure.
- Retrieve chronological chat histories.
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.document import Document
from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageSchema
from app.services.rag import RAGEngine

message_schema = ChatMessageSchema()
messages_schema = ChatMessageSchema(many=True)

@jwt_required()
def query_chatbot(doc_id):
    """
    Submits a user message and returns a grounded RAG-chatbot answer.
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get("message"):
        return jsonify({"error": "Bad Request", "message": "Missing message in request body"}), 400

    user_query = data.get("message").strip()

    # 1. Fetch document and verify ownership
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    if document.status != 'ready':
        return jsonify({"error": "Bad Request", "message": "Document is not ready for querying"}), 400

    try:
        # 2. Get past chat history for context injection
        chat_history = ChatMessage.query.filter_by(
            document_id=doc_id, 
            user_id=current_user_id
        ).order_by(ChatMessage.created_at.asc()).all()

        # 3. Retrieve chunks and generate answer via RAG
        rag_engine = RAGEngine(
            api_key=current_app.config['GEMINI_API_KEY'],
            chat_model=current_app.config.get('GEMINI_MODEL', 'gemini-3.1-flash-lite')
        )
        answer = rag_engine.query_document(user_query, document.chunks, chat_history)

        # 4. Save both User Message and Assistant Message to Database
        user_message = ChatMessage(
            document_id=doc_id,
            user_id=current_user_id,
            sender='user',
            message=user_query
        )
        
        assistant_message = ChatMessage(
            document_id=doc_id,
            user_id=current_user_id,
            sender='assistant',
            message=answer
        )

        db.session.add(user_message)
        db.session.add(assistant_message)
        db.session.commit()

        return jsonify({
            "message": "Query processed successfully",
            "chat": message_schema.dump(assistant_message)
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Chat error: {e}")
        return jsonify({"error": "Server Error", "message": f"Chat query failed: {str(e)}"}), 500

@jwt_required()
def get_chat_history(doc_id):
    """
    Retrieves complete chat dialogue logs for a document.
    """
    current_user_id = int(get_jwt_identity())
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    chat_history = ChatMessage.query.filter_by(
        document_id=doc_id, 
        user_id=current_user_id
    ).order_by(ChatMessage.created_at.asc()).all()

    return jsonify({
        "history": messages_schema.dump(chat_history)
    }), 200
