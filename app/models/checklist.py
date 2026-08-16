from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todo_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(String, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    todo = relationship("Todo", back_populates="checklist_items")
