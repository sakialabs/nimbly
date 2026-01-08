"""
Integration tests for authentication endpoints
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt

from api.config import settings
from api.models import User


def test_magic_link_request(client):
    """Test requesting a magic link"""
    response = client.post(
        "/api/auth/request-magic-link",
        json={"email": "test@example.com"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "expires_in" in data
    assert data["expires_in"] == settings.magic_link_expiry_seconds


def test_magic_link_verify_creates_new_user(client, db_session):
    """Test that verifying a magic link creates a new user"""
    email = "newuser@example.com"
    
    # Create a valid magic link token
    expire = datetime.utcnow() + timedelta(seconds=900)
    token = jwt.encode(
        {"sub": email, "exp": expire, "type": "magic_link"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # Verify token
    response = client.get(f"/api/auth/verify?token={token}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "user_id" in data
    assert "session_token" in data
    
    # Verify user was created in database
    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    assert str(user.id) == data["user_id"]


def test_magic_link_verify_existing_user(client, db_session):
    """Test that verifying a magic link for existing user doesn't create duplicate"""
    email = "existing@example.com"
    
    # Create user
    user = User(email=email)
    db_session.add(user)
    db_session.commit()
    
    # Create magic link token
    expire = datetime.utcnow() + timedelta(seconds=900)
    token = jwt.encode(
        {"sub": email, "exp": expire, "type": "magic_link"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # Verify token
    response = client.get(f"/api/auth/verify?token={token}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert str(user.id) == data["user_id"]
    
    # Verify no duplicate users
    user_count = db_session.query(User).filter(User.email == email).count()
    assert user_count == 1


def test_expired_magic_link_rejected(client):
    """Test that expired magic links are rejected"""
    email = "test@example.com"
    
    # Create expired token
    expire = datetime.utcnow() - timedelta(seconds=1)
    token = jwt.encode(
        {"sub": email, "exp": expire, "type": "magic_link"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    response = client.get(f"/api/auth/verify?token={token}")
    
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_invalid_token_rejected(client):
    """Test that invalid tokens are rejected"""
    response = client.get("/api/auth/verify?token=invalid_token")
    
    assert response.status_code == 401


def test_session_token_authentication(client, db_session):
    """Test that session tokens work for authenticated requests"""
    email = "sessiontest@example.com"
    
    # Create user
    user = User(email=email)
    db_session.add(user)
    db_session.commit()
    
    # Create session token
    expire = datetime.utcnow() + timedelta(days=30)
    session_token = jwt.encode(
        {"sub": str(user.id), "email": email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # Use session token to access protected endpoint
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    
    assert response.status_code == 200


def test_missing_authorization_header(client):
    """Test that requests without authorization are rejected"""
    response = client.get("/api/receipts")
    
    assert response.status_code == 422  # Missing required header


def test_invalid_authorization_format(client):
    """Test that invalid authorization format is rejected"""
    response = client.get(
        "/api/receipts",
        headers={"Authorization": "InvalidFormat token123"}
    )
    
    assert response.status_code == 401
