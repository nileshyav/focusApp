"""
Pomodoro domain Pydantic validation and serialization schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PomodoroSessionBase(BaseModel):
    duration_minutes: int = Field(default=25, ge=1, le=180)
    todo_id: Optional[int] = None


class PomodoroSessionCreate(PomodoroSessionBase):
    pass


class PomodoroSessionRead(PomodoroSessionBase):
    id: int
    user_id: Optional[str] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
