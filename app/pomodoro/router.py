"""
Pomodoro domain FastAPI router.
Handles HTTP endpoints for logging focus study sessions.
"""

from typing import Optional
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
import app.pomodoro.service as service

router = APIRouter(tags=["Pomodoro Sessions"])


@router.post("/pomodoro/complete")
def log_pomodoro_session(
    duration_minutes: int = Form(25),
    todo_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Logs a completed Pomodoro study session."""
    service.log_focus_session(db, duration_minutes=duration_minutes, todo_id=todo_id)
    return {"status": "success"}
