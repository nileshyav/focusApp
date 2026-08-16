from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

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
