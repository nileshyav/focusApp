"""
Pomodoro domain business service layer.
Handles logging and processing completed focus study sessions.
"""

from typing import Optional
from sqlalchemy.orm import Session

import app.pomodoro.repository as repository
import app.pomodoro.schemas as schemas


def log_focus_session(
    db: Session,
    duration_minutes: int = 25,
    todo_id: Optional[int] = None
) -> schemas.PomodoroSessionRead:
    """
    Logs a completed Pomodoro study session.

    Args:
        db (Session): Database session.
        duration_minutes (int): Duration of session in minutes.
        todo_id (Optional[int]): Associated task ID.

    Returns:
        PomodoroSessionRead: Validated Pydantic session response schema.
    """
    session_in = schemas.PomodoroSessionCreate(
        duration_minutes=duration_minutes,
        todo_id=todo_id
    )
    db_session = repository.create_pomodoro_session(db, session_in)
    return schemas.PomodoroSessionRead.model_validate(db_session)
