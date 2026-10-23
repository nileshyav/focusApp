"""
User domain FastAPI router.
Handles HTTP endpoints for authentication, login/signup forms, cookies, and logout.
"""

import os
from typing import Optional
from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import app.users.schemas as schemas
import app.users.service as service
from app.core.dependencies import get_optional_user, COOKIE_NAME

router = APIRouter(tags=["Authentication"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: Optional[schemas.UserRead] = Depends(get_optional_user)):
    """Renders login page view."""
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"user": None, "error": None}
    )


@router.post("/login", response_class=HTMLResponse)
def handle_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    """Processes user login form submission and sets session cookie."""
    login_in = schemas.UserLogin(email=email.strip(), password=password)
    result = service.sign_in_user(login_in)

    if not result.get("success"):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"user": None, "error": result.get("error", "Invalid login credentials.")}
        )

    access_token = result.get("access_token")
    response = RedirectResponse(url="/", status_code=303)
    if access_token:
        response.set_cookie(
            key=COOKIE_NAME,
            value=access_token,
            httponly=True,
            samesite="lax",
            max_age=86400 * 7  # 7 days
        )
    return response


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, user: Optional[schemas.UserRead] = Depends(get_optional_user)):
    """Renders signup page view."""
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={"user": None, "error": None, "message": None}
    )


@router.post("/signup", response_class=HTMLResponse)
def handle_signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    """Processes user registration form submission."""
    try:
        signup_in = schemas.UserSignup(email=email.strip(), password=password)
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"user": None, "error": "Password must be at least 6 characters long."}
        )

    result = service.sign_up_user(signup_in)

    if not result.get("success"):
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"user": None, "error": result.get("error", "Signup failed.")}
        )

    access_token = result.get("access_token")
    if access_token:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key=COOKIE_NAME,
            value=access_token,
            httponly=True,
            samesite="lax",
            max_age=86400 * 7
        )
        return response
    else:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"user": None, "message": result.get("message", "Registration successful! Please log in.")}
        )


@router.post("/dev-login")
def handle_dev_login(email: str = Form("dev@local.com")):
    """Local offline development 1-click bypass login."""
    access_token = f"dev_token_{email.strip()}"
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=86400 * 7
    )
    return response


@router.post("/logout")
def handle_logout():
    """Logs out user and clears session cookie."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key=COOKIE_NAME)
    return response
