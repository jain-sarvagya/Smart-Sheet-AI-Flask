# backend/tests/test_integration.py
"""
Purpose: Integration tests verifying authentication routes and database persistence.
Responsibilities:
- Configure temporary in-memory SQLite database.
- Verify user registration API response.
- Verify login API, JWT token generation, and payload structure.
- Verify profile API accesses under protected routes.
"""

import json
import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app('development')
    app.config.update({
        'TESTING': True,
        'JWT_SECRET_KEY': 'testing-secret-key'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_user_registration_and_login(client):
    """Test user registration, password hashing, and login token exchange."""
    # 1. Register User
    reg_payload = {
        "name": "Alice Developer",
        "email": "alice@example.com",
        "password": "securepassword123"
    }
    
    response = client.post(
        '/api/auth/register',
        data=json.dumps(reg_payload),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "access_token" in data
    assert data["user"]["email"] == "alice@example.com"
    
    # Verify in DB
    user = User.query.filter_by(email="alice@example.com").first()
    assert user is not None
    assert user.name == "Alice Developer"
    assert user.check_password("securepassword123") is True
    assert user.check_password("wrongpassword") is False

    # 2. Login User
    login_payload = {
        "email": "alice@example.com",
        "password": "securepassword123"
    }
    
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    login_data = json.loads(response.data)
    assert "access_token" in login_data
    token = login_data["access_token"]

    # 3. Access Protected Profile
    response = client.get(
        '/api/auth/profile',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    profile_data = json.loads(response.data)
    assert profile_data["user"]["email"] == "alice@example.com"
