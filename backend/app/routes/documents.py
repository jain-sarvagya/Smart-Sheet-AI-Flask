# backend/app/routes/documents.py
"""
Purpose: Expose Document management endpoints.
Endpoints:
- POST /upload -> upload_document (Initiate PDF upload and processing)
- GET / -> list_documents (List current user's uploads)
- GET /<doc_id> -> get_document (Retrieve specific document details)
- DELETE /<doc_id> -> delete_document (Remove document and related study assets)
- GET /file/<filename> -> serve_local_file (Static serving of PDFs in fallback local storage mode)
"""

from flask import Blueprint
from app.controllers.documents import (
    upload_document,
    list_documents,
    get_document,
    delete_document,
    serve_local_file
)

doc_bp = Blueprint('documents', __name__)

doc_bp.route('/upload', methods=['POST'])(upload_document)
doc_bp.route('/', methods=['GET'])(list_documents)
doc_bp.route('/<int:doc_id>', methods=['GET'])(get_document)
doc_bp.route('/<int:doc_id>', methods=['DELETE'])(delete_document)
doc_bp.route('/file/<string:filename>', methods=['GET'])(serve_local_file)
