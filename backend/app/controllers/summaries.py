# # backend/app/controllers/summaries.py
# """
# Purpose: Controller managing Summary operations.
# Responsibilities:
# - Check if Document processing status is 'ready'.
# - Check if a Summary already exists for a document to prevent redundant API calls.
# - Fetch and merge text chunks in sequential order.
# - Request GeminiService to generate short/detailed summaries and takeaways.
# - Persist summaries in the database.
# - Retrieve existing summaries for view.
# """

# from flask import jsonify, current_app
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.extensions import db
# from app.models.document import Document
# from app.models.summary import Summary
# from app.schemas.summary import SummarySchema
# from app.services.gemini import GeminiService

# summary_schema = SummarySchema()

# @jwt_required()
# def generate_summary(doc_id):
#     """
#     Generates summary for a document using Gemini.
#     Returns existing if already generated.
#     """
#     current_user_id = int(get_jwt_identity())
    
#     # 1. Fetch document and verify ownership
#     document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
#     if not document:
#         return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

#     if document.status != 'ready':
#         return jsonify({"error": "Bad Request", "message": f"Document is not ready for generation. Status: {document.status}"}), 400

#     # 2. Check if summary already exists (cache hit)
#     existing_summary = Summary.query.filter_by(document_id=doc_id).first()
#     if existing_summary:
#         return jsonify({
#             "message": "Summary retrieved from cache",
#             "summary": summary_schema.dump(existing_summary)
#         }), 200

#     # 3. Concatenate document chunks for summary input
#     # Chunks are ordered sequentially
#     chunks = sorted(document.chunks, key=lambda c: c.chunk_index)
#     if not chunks:
#         return jsonify({"error": "Bad Request", "message": "No text content found for this document"}), 400

#     full_text = "\n".join([chunk.chunk_text for chunk in chunks])

#     # 4. Invoke Gemini API
#     gemini_service = GeminiService(
#         api_key=current_app.config['GEMINI_API_KEY'],
#         model_name=current_app.config.get('GEMINI_MODEL', 'gemini-2.5-flash')
#     )
#     logger = current_app.logger
#     logger.info(f"Triggering Gemini summary generation for Document ID {doc_id}")
    
#     try:
#         summary_data = gemini_service.generate_summary(full_text)
#     except Exception as e:
#         current_app.logger.error(f"Gemini summary generation failed: {e}")
#         return jsonify({"error": "API Error", "message": f"Summary generation failed: {str(e)}"}), 502

#     # 5. Persist to DB
#     summary = Summary(
#         document_id=doc_id,
#         short_summary=summary_data.get("short_summary", "No short summary generated."),
#         detailed_summary=summary_data.get("detailed_summary", "No detailed summary generated."),
#         key_takeaways=summary_data.get("key_takeaways", [])
#     )

#     try:
#         db.session.add(summary)
#         db.session.commit()
#         return jsonify({
#             "message": "Summary generated successfully",
#             "summary": summary_schema.dump(summary)
#         }), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": "Server Error", "message": f"Failed to save summary: {str(e)}"}), 500

# @jwt_required()
# def get_summary(doc_id):
#     """
#     Fetches the existing summary for a document.
#     """
#     current_user_id = int(get_jwt_identity())
#     document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
#     if not document:
#         return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

#     summary = Summary.query.filter_by(document_id=doc_id).first()
#     if not summary:
#         return jsonify({"error": "Not Found", "message": "Summary not yet generated for this document"}), 404

#     return jsonify({
#         "summary": summary_schema.dump(summary)
#     }), 200






# backend/app/controllers/summaries.py

from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback

from app.extensions import db
from app.models.document import Document
from app.models.summary import Summary
from app.schemas.summary import SummarySchema
from app.services.gemini import GeminiService

summary_schema = SummarySchema()


@jwt_required()
def generate_summary(doc_id):
    """
    Generates summary for a document using Gemini.
    Returns existing if already generated.
    """

    current_user_id = int(get_jwt_identity())

    # Fetch document
    document = Document.query.filter_by(
        id=doc_id,
        user_id=current_user_id
    ).first()

    if not document:
        return jsonify({
            "error": "Not Found",
            "message": "Document not found or unauthorized"
        }), 404

    if document.status != "ready":
        return jsonify({
            "error": "Bad Request",
            "message": f"Document is not ready. Status: {document.status}"
        }), 400

    # Check cache
    existing_summary = Summary.query.filter_by(
        document_id=doc_id
    ).first()

    if existing_summary:
        return jsonify({
            "message": "Summary retrieved from cache",
            "summary": summary_schema.dump(existing_summary)
        }), 200

    # Merge chunks
    chunks = sorted(
        document.chunks,
        key=lambda c: c.chunk_index
    )

    if not chunks:
        return jsonify({
            "error": "Bad Request",
            "message": "No text content found for this document"
        }), 400

    full_text = "\n".join(
        [chunk.chunk_text for chunk in chunks]
    )

    print("\n================ DEBUG ================")
    print("Document ID:", doc_id)
    print("Document Length:", len(full_text))
    print(
        "Gemini Model:",
        current_app.config.get(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )
    )
    print(
        "API Key Loaded:",
        bool(current_app.config.get("GEMINI_API_KEY"))
    )
    print("=======================================\n")

    gemini_service = GeminiService(
        api_key=current_app.config.get("GEMINI_API_KEY"),
        model_name=current_app.config.get(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )
    )

    try:
        summary_data = gemini_service.generate_summary(
            full_text
        )

        print("\n========== GEMINI RESPONSE ==========")
        print(summary_data)
        print("=====================================\n")

    except Exception as e:

        print("\n========== GEMINI ERROR ==========")
        traceback.print_exc()
        print("==================================\n")

        current_app.logger.error(
            f"Gemini summary generation failed: {e}"
        )

        return jsonify({
            "error": "API Error",
            "message": str(e)
        }), 502

    summary = Summary(
        document_id=doc_id,
        short_summary=summary_data.get(
            "short_summary",
            "No short summary generated."
        ),
        detailed_summary=summary_data.get(
            "detailed_summary",
            "No detailed summary generated."
        ),
        key_takeaways=summary_data.get(
            "key_takeaways",
            []
        )
    )

    try:
        db.session.add(summary)
        db.session.commit()

        return jsonify({
            "message": "Summary generated successfully",
            "summary": summary_schema.dump(summary)
        }), 201

    except Exception as e:

        db.session.rollback()

        traceback.print_exc()

        return jsonify({
            "error": "Server Error",
            "message": f"Failed to save summary: {str(e)}"
        }), 500


@jwt_required()
def get_summary(doc_id):

    current_user_id = int(get_jwt_identity())

    document = Document.query.filter_by(
        id=doc_id,
        user_id=current_user_id
    ).first()

    if not document:
        return jsonify({
            "error": "Not Found",
            "message": "Document not found or unauthorized"
        }), 404

    summary = Summary.query.filter_by(
        document_id=doc_id
    ).first()

    if not summary:
        return jsonify({
            "error": "Not Found",
            "message": "Summary not yet generated for this document"
        }), 404

    return jsonify({
        "summary": summary_schema.dump(summary)
    }), 200