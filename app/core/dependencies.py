"""
Core Authentication Dependencies.
Extracts session cookies and provides current user context to FastAPI endpoints.
"""

from typing import Optional
from fastapi import Request, HTTPException, status
import app.users.schemas as schemas

COOKIE_NAME = "sb-access-token"


def get_optional_user(request: Request) -> Optional[schemas.UserRead]:
    """
    Retrieves current user if authenticated, or None if guest.

    Args:
        request (Request): Incoming FastAPI request.

    Returns:
        Optional[schemas.UserRead]: User schema if session cookie is valid.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    from app.users.service import get_current_user_from_token
    return get_current_user_from_token(token)


def get_current_user(request: Request) -> schemas.UserRead:
    """
    Requires an authenticated user session. Raises 401 HTTP exception if guest.

    Args:
        request (Request): Incoming FastAPI request.

    Returns:
        schemas.UserRead: Authenticated user schema.
    """
    user = get_optional_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
