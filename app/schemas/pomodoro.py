from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PomodoroSessionBase(BaseModel):
    duration_minutes: int = 25
    todo_id: Optional[int] = None

class PomodoroSessionCreate(PomodoroSessionBase):
    pass

class PomodoroSessionRead(PomodoroSessionBase):
    id: int
    user_id: Optional[str] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
