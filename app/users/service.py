"""
User domain authentication service layer.
Interfaces with Supabase GoTrue Auth API and provides local offline dev fallback.
"""

from typing import Optional, Dict, Any
import jwt
from supabase import create_client, Client
from app.core.config import settings
import app.users.schemas as schemas

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Returns singleton Supabase client instance if credentials exist."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            return _supabase_client
        except Exception:
            return None
    return None


def sign_up_user(signup_in: schemas.UserSignup) -> Dict[str, Any]:
    """
    Registers a new user via Supabase Auth API.

    Returns:
        Dict[str, Any]: Dict containing success boolean, message, user_data, or error.
    """
    client = get_supabase_client()
    if not client:
        # Development offline fallback
        return {
            "success": True,
            "access_token": f"dev_token_{signup_in.email}",
            "user": schemas.UserRead(id=f"dev_user_{signup_in.email}", email=signup_in.email, is_dev=True)
        }

    try:
        res = client.auth.sign_up({"email": signup_in.email, "password": signup_in.password})
        if res.session:
            return {
                "success": True,
                "access_token": res.session.access_token,
                "user": schemas.UserRead(id=res.user.id, email=res.user.email)
            }
        else:
            return {
                "success": True,
                "access_token": None,
                "message": "Signup successful! Please check your email to confirm registration.",
                "user": schemas.UserRead(id=res.user.id, email=res.user.email)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_in_user(login_in: schemas.UserLogin) -> Dict[str, Any]:
    """
    Authenticates a user via Supabase Auth API.

    Returns:
        Dict[str, Any]: Dict containing access_token, user schema, or error.
    """
    client = get_supabase_client()
    if not client:
        # Development offline fallback
        return {
            "success": True,
            "access_token": f"dev_token_{login_in.email}",
            "user": schemas.UserRead(id=f"dev_user_{login_in.email}", email=login_in.email, is_dev=True)
        }

    try:
        res = client.auth.sign_in_with_password({"email": login_in.email, "password": login_in.password})
        if res.session:
            return {
                "success": True,
                "access_token": res.session.access_token,
                "user": schemas.UserRead(id=res.user.id, email=res.user.email)
            }
        return {"success": False, "error": "Invalid login session response."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_current_user_from_token(token: Optional[str]) -> Optional[schemas.UserRead]:
    """
    Decodes and validates user session token.

    Args:
        token (Optional[str]): JWT access token string or dev token string.

    Returns:
        Optional[schemas.UserRead]: Authenticated user object or None.
    """
    if not token:
        return None

    if token.startswith("dev_token_"):
        user_email = token.replace("dev_token_", "")
        return schemas.UserRead(id=f"dev_user_{user_email}", email=user_email, is_dev=True)

    client = get_supabase_client()
    if client:
        try:
            res = client.auth.get_user(token)
            if res and res.user:
                return schemas.UserRead(id=res.user.id, email=res.user.email)
        except Exception:
            pass

    # Try decoding unverified JWT payload for user ID as fallback
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        user_id = unverified.get("sub")
        email = unverified.get("email", "user@supabase.local")
        if user_id:
            return schemas.UserRead(id=user_id, email=email)
    except Exception:
        pass

    return None
