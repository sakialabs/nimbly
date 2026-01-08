"""
Authentication endpoints and logic
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import logging
import uuid

from api.database import get_db
from api.models import User
from api.schemas import MagicLinkRequest, MagicLinkResponse, TokenVerifyResponse, ErrorResponse
from api.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def create_magic_link_token(email: str) -> str:
    """Create a JWT token for magic link authentication"""
    expire = datetime.utcnow() + timedelta(seconds=settings.magic_link_expiry_seconds)
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "magic_link"
    }
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    logger.debug(f"Created magic link token for {email}, expires at {expire}")
    return token

def create_session_token(user_id: str, email: str) -> str:
    """Create a JWT session token"""
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "type": "session"
    }
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    logger.debug(f"Created session token for user {user_id}, expires at {expire}")
    return token

def verify_token(token: str, expected_type: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != expected_type:
            logger.warning(f"Token type mismatch: expected {expected_type}, got {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

@router.post("/request-magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """
    Request a magic link for passwordless authentication.
    
    In development mode, the magic link is logged to the console instead of being emailed.
    The link expires after 15 minutes (900 seconds).
    
    **Request Body:**
    - email: Valid email address
    
    **Response:**
    - message: Confirmation message
    - expires_in: Token expiry time in seconds
    
    **Example:**
    ```json
    {
        "email": "user@example.com"
    }
    ```
    
    **Response Example:**
    ```json
    {
        "message": "Magic link sent to user@example.com",
        "expires_in": 900
    }
    ```
    """
    email = request.email
    request_id = str(uuid.uuid4())[:8]
    
    logger.info(f"[{request_id}] Magic link requested for {email}")
    
    # Create magic link token
    token = create_magic_link_token(email)
    
    # In development, log the magic link to console
    magic_link = f"http://localhost:8000/api/auth/verify?token={token}"
    logger.info(f"[{request_id}] Magic link generated for {email}")
    print(f"\n🔗 Magic Link for {email}:\n{magic_link}\n")
    
    return MagicLinkResponse(
        message=f"Magic link sent to {email}",
        expires_in=settings.magic_link_expiry_seconds
    )

@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_magic_link(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify a magic link token and create or authenticate a user session.
    
    This endpoint validates the magic link token and returns a long-lived session token
    that can be used for subsequent API requests.
    
    **Query Parameters:**
    - token: The magic link token from the email/console
    
    **Response:**
    - user_id: UUID of the user
    - email: User's email address
    - session_token: JWT token for API authentication (valid for 30 days)
    
    **Errors:**
    - 401: Invalid or expired token
    
    **Example:**
    ```
    GET /api/auth/verify?token=eyJhbGc...
    ```
    
    **Response Example:**
    ```json
    {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "user@example.com",
        "session_token": "eyJhbGc..."
    }
    ```
    
    Use the session_token in subsequent requests:
    ```
    Authorization: Bearer <session_token>
    ```
    """
    request_id = str(uuid.uuid4())[:8]
    
    # Verify the magic link token
    payload = verify_token(token, "magic_link")
    email = payload.get("sub")
    
    if not email:
        logger.error(f"[{request_id}] Token missing email subject")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    logger.info(f"[{request_id}] Verifying magic link for {email}")
    
    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"[{request_id}] Created new user: {email} (user_id={user.id})")
    else:
        logger.info(f"[{request_id}] User authenticated: {email} (user_id={user.id})")
    
    # Create session token
    session_token = create_session_token(user.id, user.email)
    
    return TokenVerifyResponse(
        user_id=user.id,
        email=user.email,
        session_token=session_token
    )

def get_current_user(
    token: str,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from session token.
    """
    payload = verify_token(token, "session")
    user_id = payload.get("sub")
    
    if not user_id:
        logger.error("Session token missing user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User not found for ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

