# backend/app/controllers/documents.py
"""
Purpose: Controller managing document operations.
Responsibilities:
- Validate PDF upload formats.
- Delegate PDF storage uploads to the StorageService (ImageKit/local fallback).
- Insert initial Document metadata in the database as 'processing'.
- Trigger the background processing thread (PDFProcessor) to chunk and parse.
- Retrieve lists of user-owned documents.
- Serve local files if local fallback storage was used.
- Delete documents, utilizing cascade deletes to clean up all database relations.
"""

import os
from flask import request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.document import Document
from app.schemas.document import DocumentSchema
from app.services.imagekit import StorageService
from app.services.pdf_processor import PDFProcessor

document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)

def allowed_file(filename):
    """Checks if the file extension is PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@jwt_required()
def upload_document():
    """
    Handles uploading a PDF file.
    Saves file -> Registers in DB -> Initiates background chunking/parsing.
    """
    # 1. Verify file exists in request
    if 'file' not in request.files:
        return jsonify({"error": "Bad Request", "message": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Bad Request", "message": "No file selected for uploading"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported Media Type", "message": "Only PDF files are supported"}), 415

    current_user_id = int(get_jwt_identity())

    # 2. Upload file via StorageService
    storage_service = StorageService(
        public_key=current_app.config['IMAGEKIT_PUBLIC_KEY'],
        private_key=current_app.config['IMAGEKIT_PRIVATE_KEY'],
        url_endpoint=current_app.config['IMAGEKIT_URL_ENDPOINT'],
        upload_folder=current_app.config['UPLOAD_FOLDER']
    )

    try:
        # If we need a temporary path for the processor, we can save file locally first
        # storage_service does this or uploads to ImageKit.
        file_url = storage_service.upload_file(file, file.filename)
        
        # Determine local file path for extraction
        # If local fallback was used, the file is saved directly in UPLOAD_FOLDER
        if file_url.startswith("/api/documents/file/"):
            filename = file_url.split("/")[-1]
            local_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        else:
            # If ImageKit was used, save file temporarily for processing, then delete it
            temp_filename = f"temp_{current_user_id}_{file.filename}"
            local_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], temp_filename)
            file.seek(0)
            file.save(local_file_path)

        # 3. Save Document entry in database with status 'processing'
        document = Document(
            user_id=current_user_id,
            title=file.filename,
            file_url=file_url,
            status='processing'
        )
        db.session.add(document)
        db.session.commit()

        # 4. Trigger background processor thread
        # We pass flask app instance explicitly so it can bind db contexts
        flask_app = current_app._get_current_object()
        PDFProcessor.process_document_background(flask_app, document.id, local_file_path)

        return jsonify({
            "message": "Document uploaded successfully. Processing started.",
            "document": document_schema.dump(document)
        }), 202

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server Error", "message": f"Upload process failed: {str(e)}"}), 500

@jwt_required()
def list_documents():
    """
    Lists all documents owned by the currently authenticated user.
    """
    current_user_id = int(get_jwt_identity())
    documents = Document.query.filter_by(user_id=current_user_id).order_by(Document.created_at.desc()).all()
    return jsonify({
        "documents": documents_schema.dump(documents)
    }), 200

@jwt_required()
def get_document(doc_id):
    """
    Retrieves metadata details for a specific document.
    """
    current_user_id = int(get_jwt_identity())
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404
    
    return jsonify({
        "document": document_schema.dump(document)
    }), 200

@jwt_required()
def delete_document(doc_id):
    """
    Deletes a document and all related learning assets (cascade delete).
    Also tries to delete the file if stored locally.
    """
    current_user_id = int(get_jwt_identity())
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    if not document:
        return jsonify({"error": "Not Found", "message": "Document not found or unauthorized"}), 404

    try:
        # Check if local storage was used and delete physical file
        if document.file_url.startswith("/api/documents/file/"):
            filename = document.file_url.split("/")[-1]
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                
        # Perform cascade DB deletion
        db.session.delete(document)
        db.session.commit()
        return jsonify({"message": "Document and all related assets deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server Error", "message": f"Could not delete document: {str(e)}"}), 500

def serve_local_file(filename):
    """
    Serves a locally stored PDF document.
    """
    directory = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory, filename)
