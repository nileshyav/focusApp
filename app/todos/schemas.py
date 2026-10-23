"""
Todo domain Pydantic validation and serialization schemas.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ChecklistItemBase(BaseModel):
    text: str
    completed: bool = False


class ChecklistItemCreate(ChecklistItemBase):
    pass


class ChecklistItemUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None


class ChecklistItemRead(ChecklistItemBase):
    id: int
    todo_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


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
