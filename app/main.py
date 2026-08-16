"""
FastAPI Todo & Performance Analytics Application.
Follows PEP 8 guidelines, standard imports ordering, and modular architecture.
"""

import os
from typing import Optional

from fastapi import FastAPI, Request, Form, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.core.database import get_db, engine, Base
from app.utils.formatters import (
    fetch_todos_formatted,
    fetch_todo_formatted,
    render_detail_and_oob
)

# Ensure database tables exist if running locally
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI + HTMX Todo Analytics App")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

active_sort_preference = "created_at"


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    """Renders main dashboard page with todo items."""
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"todos": todos, "current_sort": active_sort_preference}
    )


@app.get("/performance", response_class=HTMLResponse)
def performance_report_page(request: Request, db: Session = Depends(get_db)):
    """Renders performance report and productivity metrics page."""
    report = crud.get_performance_data(db)
    return templates.TemplateResponse(
        request=request,
        name="performance.html",
        context={"report": report}
    )


@app.post("/pomodoro/complete")
def log_pomodoro_session(
    duration_minutes: int = Form(25),
    todo_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Logs a completed Pomodoro study session."""
    crud.create_pomodoro_session(db, duration_minutes=duration_minutes, todo_id=todo_id)
    return {"status": "success"}


@app.get("/todos", response_class=HTMLResponse)
def get_todos_partial(
    request: Request,
    sort_by: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """HTMX partial endpoint for returning sorted todo items."""
    global active_sort_preference
    if sort_by:
        active_sort_preference = sort_by
    todos = fetch_todos_formatted(db, sort_by=sort_by)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos, "current_sort": active_sort_preference}
    )


@app.post("/add", response_class=HTMLResponse)
def add_todo(
    request: Request,
    title: str = Form(...),
    priority: str = Form("medium"),
    deadline: str = Form(""),
    karma: int = Form(0),
    db: Session = Depends(get_db)
):
    """Adds a new todo task."""
    if title.strip():
        todo_in = schemas.TodoCreate(
            title=title.strip(),
            priority=priority,
            deadline=deadline.strip(),
            karma=karma
        )
        crud.create_todo(db, todo_in)
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@app.post("/toggle/{todo_id}", response_class=HTMLResponse)
def toggle_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """Toggles todo completed status."""
    crud.toggle_todo(db, todo_id)
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@app.delete("/delete/{todo_id}", response_class=HTMLResponse)
def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """Deletes a todo task and its checklist items."""
    crud.delete_todo(db, todo_id)
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@app.post("/log-time/{todo_id}", response_class=HTMLResponse)
def log_time(
    request: Request,
    todo_id: int,
    seconds: int = Form(...),
    db: Session = Depends(get_db)
):
    """Logs stopwatch elapsed time to a task."""
    if seconds > 0:
        db_todo = crud.get_todo(db, todo_id)
        if db_todo:
            crud.update_todo(
                db,
                todo_id,
                schemas.TodoUpdate(time_spent=db_todo.time_spent + seconds)
            )
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@app.post("/update-priority/{todo_id}", response_class=HTMLResponse)
def update_priority(
    request: Request,
    todo_id: int,
    priority: str = Form(...),
    db: Session = Depends(get_db)
):
    """Updates todo priority level."""
    crud.update_todo(db, todo_id, schemas.TodoUpdate(priority=priority))
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@app.post("/update-deadline/{todo_id}", response_class=HTMLResponse)
def update_deadline(
    request: Request,
    todo_id: int,
    deadline: str = Form(""),
    db: Session = Depends(get_db)
):
    """Updates todo target deadline."""
    crud.update_todo(db, todo_id, schemas.TodoUpdate(deadline=deadline.strip()))
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@app.post("/update-karma/{todo_id}", response_class=HTMLResponse)
def update_karma(
    request: Request,
    todo_id: int,
    karma: int = Form(0),
    db: Session = Depends(get_db)
):
    """Updates task karma score."""
    crud.update_todo(db, todo_id, schemas.TodoUpdate(karma=karma))
    todos = fetch_todos_formatted(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@app.get("/task/{todo_id}/details", response_class=HTMLResponse)
def get_task_details(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """Renders task detail modal view."""
    todo = fetch_todo_formatted(db, todo_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/task_detail.html",
        context={"todo": todo}
    )


@app.post("/update-description/{todo_id}", response_class=HTMLResponse)
def update_description(
    request: Request,
    todo_id: int,
    title: Optional[str] = Form(None),
    description: str = Form(""),
    priority: str = Form("medium"),
    deadline: str = Form(""),
    karma: int = Form(0),
    db: Session = Depends(get_db)
):
    """Updates detailed task description and fields via modal drawer."""
    update_in = schemas.TodoUpdate(
        description=description,
        priority=priority,
        deadline=deadline,
        karma=karma
    )
    if title and title.strip():
        update_in.title = title.strip()

    crud.update_todo(db, todo_id, update_in)
    return render_detail_and_oob(request, templates, db, todo_id, saved_success=True)


# CHECKLIST SUB-TASK ENDPOINTS
@app.post("/task/{todo_id}/checklist/add", response_class=HTMLResponse)
def add_checklist_item(
    request: Request,
    todo_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """Adds a sub-checklist item to a todo task."""
    if text.strip():
        crud.add_checklist_item(db, todo_id=todo_id, text=text.strip())
    return render_detail_and_oob(request, templates, db, todo_id)


@app.post("/task/{todo_id}/checklist/{item_id}/toggle", response_class=HTMLResponse)
def toggle_checklist_item(
    request: Request,
    todo_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Toggles checklist item completion state."""
    crud.toggle_checklist_item(db, item_id=item_id)
    return render_detail_and_oob(request, templates, db, todo_id)


@app.delete("/task/{todo_id}/checklist/{item_id}/delete", response_class=HTMLResponse)
def delete_checklist_item(
    request: Request,
    todo_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Deletes a checklist item from a task."""
    crud.delete_checklist_item(db, item_id=item_id)
    return render_detail_and_oob(request, templates, db, todo_id)
