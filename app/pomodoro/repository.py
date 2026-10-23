"""
Pomodoro domain database access repository.
Handles persistence operations for focus sessions using SQLAlchemy.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.pomodoro.models import PomodoroSession
from app.pomodoro.schemas import PomodoroSessionCreate


def create_pomodoro_session(db: Session, session_in: PomodoroSessionCreate) -> PomodoroSession:
    """Inserts a completed focus Pomodoro session record into database."""
    session = PomodoroSession(
        duration_minutes=session_in.duration_minutes,
        todo_id=session_in.todo_id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_all_pomodoro_sessions(db: Session) -> List[PomodoroSession]:
    """Retrieves all logged Pomodoro sessions."""
    return db.query(PomodoroSession).order_by(PomodoroSession.completed_at.desc()).all()
