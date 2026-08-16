from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    time_spent = Column(Integer, default=0, nullable=False)
    description = Column(String, default="")
    priority = Column(String, default="medium", nullable=False, index=True)
    deadline = Column(String, default="", index=True)
    karma = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    checklist_items = relationship("ChecklistItem", back_populates="todo", cascade="all, delete-orphan")
    pomodoro_sessions = relationship("PomodoroSession", back_populates="todo")
