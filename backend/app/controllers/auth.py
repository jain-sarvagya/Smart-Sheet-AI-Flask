# backend/app/controllers/auth.py
"""
Purpose: Controller containing authentication business logic.
Responsibilities:
- Validate input JSON payloads using Marshmallow schemas.
- Register new users: check for duplicate emails, hash passwords, and persist.
- Authenticate existing users: verify passwords and issue JWT access tokens.
- Fetch authenticated user profiles based on JWT identity keys.
"""

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema, UserSchema

# Instantiate schemas
register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()

def register_user():
    """
    Registers a new user.
    Flow: Validate payload -> Check duplicate -> Hash password -> Save -> Generate JWT -> Return response.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "Missing JSON request body"}), 400

    try:
        # Validate input parameters
        validated_data = register_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation Error", "messages": err.messages}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=validated_data['email']).first()
    if existing_user:
        return jsonify({"error": "Conflict", "message": "Email is already registered"}), 409

    # Create new User object
    user = User(
        name=validated_data['name'],
        email=validated_data['email']
    )
    user.set_password(validated_data['password'])

    try:
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT Access Token for instant login
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": user_schema.dump(user)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server Error", "message": f"Could not create user: {str(e)}"}), 500

def login_user():
    """
    Authenticates a user and issues a JWT token.
    Flow: Validate credentials -> Match password -> Return JWT + Profile.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "Missing credentials payload"}), 400

    try:
        validated_data = login_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation Error", "messages": err.messages}), 400

    # Look up user by email
    user = User.query.filter_by(email=validated_data['email']).first()
    if not user or not user.check_password(validated_data['password']):
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user_schema.dump(user)
    }), 200

@jwt_required()
def get_profile():
    """
    Retrieves the profile of the currently logged-in user.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"error": "Not Found", "message": "User not found"}), 404

    return jsonify({
        "user": user_schema.dump(user)
    }), 200
