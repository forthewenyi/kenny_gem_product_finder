"""
Authentication middleware for password-protected portfolio access.
Uses JWT tokens and Secret Manager for secure password storage.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours for portfolio demo

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme
security = HTTPBearer(auto_error=False)


def get_access_password() -> str:
    """
    Get the access password from environment variable.
    In production, this comes from Google Cloud Secret Manager.
    """
    password = os.getenv("PORTFOLIO_ACCESS_PASSWORD")
    if not password:
        raise RuntimeError(
            "PORTFOLIO_ACCESS_PASSWORD not set. "
            "This must be configured in Secret Manager for Cloud Run deployment."
        )
    return password


def verify_password(plain_password: str) -> bool:
    """Verify if the provided password matches the access password."""
    stored_password = get_access_password()
    return plain_password == stored_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> bool:
    """Verify if the JWT token is valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("access") == "granted"
    except JWTError:
        return False


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Dependency to verify authentication.
    Checks for Bearer token in Authorization header.
    """
    # Allow health check endpoint without auth
    if request.url.path == "/health":
        return {"access": "granted"}

    # Allow login endpoint without auth
    if request.url.path == "/api/auth/login":
        return {"access": "granted"}

    # Allow CORS preflight
    if request.method == "OPTIONS":
        return {"access": "granted"}

    # Check for authorization header
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide access code.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access code.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access": "granted"}


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Optional authentication - returns None if not authenticated.
    Useful for endpoints that have different behavior for authenticated users.
    """
    if not credentials:
        return None

    token = credentials.credentials
    if verify_token(token):
        return {"access": "granted"}

    return None
