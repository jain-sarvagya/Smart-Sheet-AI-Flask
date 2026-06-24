# backend/app/__init__.py
"""
Purpose: Implement the Flask application factory.
Responsibilities:
- Initialize extensions (SQLAlchemy, JWT, Migrate, CORS, Marshmallow).
- Register all blueprints (API routes).
- Set up global error handlers (JSON error responses for server errors, validations, etc.).
- Ensure local uploads directory exists.
"""

import os
from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, jwt, migrate, cors, ma

def create_app(config_name=None):
    """
    Application factory pattern to create and configure a Flask application instance.
    """
    app = Flask(__name__)

    # 1. Load Configurations
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # 2. Check Database Connectivity & Fallback before initializing extensions
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if db_uri and not db_uri.startswith('sqlite'):
        from sqlalchemy import create_engine
        try:
            # Test connection to the configured database
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                pass
            engine.dispose()
        except Exception as e:
            print(f"\n[DATABASE WARNING] Connection to configured database failed: {e}")
            db_path = os.path.abspath(os.path.join(app.root_path, '..', 'smart_sheet.db'))
            print(f"[DATABASE WARNING] Falling back to SQLite local database ({db_path}) for this session.\n")
            app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    # 3. Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    ma.init_app(app)

    # 3. Ensure upload directories exist
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # 4. Check Gemini API Key configuration
    gemini_key = app.config.get('GEMINI_API_KEY')
    if not gemini_key or gemini_key == 'your_google_gemini_api_key_here' or not gemini_key.strip():
        print("\n" + "="*80)
        print("[GEMINI WARNING] GEMINI_API_KEY is not configured or is using the default placeholder!")
        print("To use all AI features (quizzes, flashcards, summaries, chat), please:")
        print("  1. Get an API key from Google AI Studio: https://aistudio.google.com/")
        print("  2. Open your backend/.env file and paste your key:")
        print("     GEMINI_API_KEY=AIzaSy...")
        print("="*80 + "\n")

    # 4. Global Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error.description)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": str(error.description)}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": str(error.description)}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Server Error: {error}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred on the server."}), 500

    # 5. Register Blueprints (Route registration)
    from app.routes.auth import auth_bp
    from app.routes.documents import doc_bp
    from app.routes.summaries import summary_bp
    from app.routes.flashcards import flashcard_bp
    from app.routes.quizzes import quiz_bp
    from app.routes.explanations import explanation_bp
    from app.routes.chat import chat_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(doc_bp, url_prefix='/api/documents')
    app.register_blueprint(summary_bp, url_prefix='/api/summaries')
    app.register_blueprint(flashcard_bp, url_prefix='/api/flashcards')
    app.register_blueprint(quiz_bp, url_prefix='/api/quizzes')
    app.register_blueprint(explanation_bp, url_prefix='/api/explanations')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    # Basic root status endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "Smart-Sheet AI Backend"}), 200

    return app
