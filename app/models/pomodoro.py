from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=True, index=True)
    todo_id = Column(Integer, ForeignKey("todos.id", ondelete="SET NULL"), nullable=True)
    duration_minutes = Column(Integer, default=25, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    todo = relationship("Todo", back_populates="pomodoro_sessions")
