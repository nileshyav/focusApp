"""
FastAPI Main Application Module.
Assembles feature routers in a Domain-Driven Modular Monolith architecture.
"""

from fastapi import FastAPI
from app.core.database import engine, Base
from app.todos.router import router as todos_router
from app.pomodoro.router import router as pomodoro_router
from app.analytics.router import router as analytics_router
from app.users.router import router as users_router

app = FastAPI(title="FastAPI Modular Monolith Todo & Analytics App")

# Register domain feature routers
app.include_router(users_router)
app.include_router(todos_router)
app.include_router(pomodoro_router)
app.include_router(analytics_router)
