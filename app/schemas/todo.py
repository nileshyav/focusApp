from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.checklist import ChecklistItemRead

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    deadline: Optional[str] = ""
    karma: int = Field(default=0, ge=0, le=5)

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[str] = None
    karma: Optional[int] = None
    completed: Optional[bool] = None
    time_spent: Optional[int] = None

class TodoRead(TodoBase):
    id: int
    user_id: Optional[str] = None
    completed: bool
    time_spent: int
    created_at: Optional[datetime] = None
    checklist_items: List[ChecklistItemRead] = []

    model_config = ConfigDict(from_attributes=True)
