# backend/app/services/pdf_processor.py
"""
Purpose: Parse uploaded PDF documents and extract text to populate database chunks.
Responsibilities:
- Use pdfplumber for high-quality text extraction (layout-aware).
- Fall back to PyPDF2 if pdfplumber fails.
- Extract total page count and text.
- Invoke the Chunker service to split text.
- Generate text embeddings for each chunk via Gemini.
- Persist chunks in the database.
- Transition Document status: ready / failed.
- Run asynchronously in a background thread.
"""

import os
import threading
import logging
import pdfplumber
import PyPDF2
from app.extensions import db
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.chunker import Chunker
from app.services.rag import RAGEngine

logger = logging.getLogger(__name__)

class PDFProcessor:
    @staticmethod
    def extract_text(file_path):
        """
        Attempts to extract text page-by-page from the PDF.
        Returns a tuple: (extracted_text, total_pages)
        """
        text_content = []
        total_pages = 0
        
        # 1. Attempt extraction using pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            full_text = "\n".join(text_content).strip()
            if full_text:
                logger.info(f"Successfully extracted text from {file_path} using pdfplumber. Pages: {total_pages}")
                return full_text, total_pages
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}, falling back to PyPDF2. Error: {e}")

        # 2. Fallback to PyPDF2
        text_content = []
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            full_text = "\n".join(text_content).strip()
            if full_text:
                logger.info(f"Successfully extracted text from {file_path} using PyPDF2. Pages: {total_pages}")
                return full_text, total_pages
        except Exception as e:
            logger.error(f"PyPDF2 fallback also failed for {file_path}. Error: {e}")
        
        return "", total_pages

    @classmethod
    def process_document_background(cls, app, document_id, file_path):
        """
        Wrapper to trigger the background thread for PDF processing.
        """
        # Start a daemon thread so it doesn't block server shutdown
        thread = threading.Thread(
            target=cls._run_processing_pipeline,
            args=(app, document_id, file_path),
            daemon=True
        )
        thread.start()

    @classmethod
    def _run_processing_pipeline(cls, app, document_id, file_path):
        """
        Executes the extraction, chunking, embedding, and storage pipeline.
        Runs inside app context to allow DB operations.
        """
        with app.app_context():
            logger.info(f"Starting processing pipeline for Document ID: {document_id}")
            document = db.session.get(Document, document_id)
            if not document:
                logger.error(f"Document ID {document_id} not found in database. Aborting.")
                return

            try:
                # 1. Extract text
                extracted_text, total_pages = cls.extract_text(file_path)
                if not extracted_text:
                    raise ValueError("Failed to extract any text from the PDF file.")

                # Update page count
                document.total_pages = total_pages
                
                # 2. Chunk text
                chunker = Chunker()
                chunks_data = chunker.split_text(extracted_text)
                if not chunks_data:
                    raise ValueError("Chunker generated 0 chunks from the text.")

                # 3. Create chunks and generate embeddings in bulk/batches
                rag_engine = RAGEngine(
                    api_key=app.config['GEMINI_API_KEY'],
                    chat_model=app.config.get('GEMINI_MODEL', 'gemini-3.1-flash-lite')
                )
                
                for item in chunks_data:
                    txt = item["chunk_text"]
                    idx = item["chunk_index"]
                    
                    # Generate embedding vector for the text chunk
                    embedding = None
                    try:
                        embedding = rag_engine.generate_embedding(txt)
                    except Exception as emb_err:
                        logger.warning(f"Failed to generate embedding for chunk {idx}: {emb_err}")
                    
                    chunk_obj = Chunk(
                        document_id=document_id,
                        chunk_text=txt,
                        chunk_index=idx,
                        embedding=embedding
                    )
                    db.session.add(chunk_obj)

                # Update document status to ready
                document.status = 'ready'
                db.session.commit()
                logger.info(f"Document ID {document_id} successfully processed and marked ready.")

            except Exception as e:
                db.session.rollback()
                logger.error(f"Pipeline failed for Document ID {document_id}: {e}")
                document.status = 'failed'
                db.session.commit()
            finally:
                # Clean up local temp file if it's placed in temp uploads
                # (but keeping it if we fallback to local storage mode)
                # If we are using ImageKit, we might delete local temp file
                is_imagekit_configured = all([
                    app.config['IMAGEKIT_PUBLIC_KEY'],
                    app.config['IMAGEKIT_PRIVATE_KEY'],
                    app.config['IMAGEKIT_URL_ENDPOINT']
                ])
                if is_imagekit_configured and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted local temporary file: {file_path}")
                    except Exception as cleanup_err:
                        logger.warning(f"Failed to delete temp file {file_path}: {cleanup_err}")
