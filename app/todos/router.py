"""
Todo domain FastAPI router.
Handles HTTP endpoints, form inputs, and HTMX HTML responses.
"""

import os
from typing import Optional
from fastapi import APIRouter, Request, Form, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
import app.todos.repository as repository
import app.todos.schemas as schemas
import app.todos.service as service

from app.core.dependencies import get_optional_user
import app.users.schemas as user_schemas

router = APIRouter(tags=["Todos"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

active_sort_preference = "created_at"


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[user_schemas.UserRead] = Depends(get_optional_user)
):
    """Renders main dashboard page with todo items."""
    user_id = user.id if user else None
    todos = service.list_formatted_todos(db, user_id=user_id)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"todos": todos, "current_sort": active_sort_preference, "user": user}
    )


@router.get("/todos", response_class=HTMLResponse)
def get_todos_partial(
    request: Request,
    sort_by: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: Optional[user_schemas.UserRead] = Depends(get_optional_user)
):
    """HTMX partial endpoint returning sorted todo list HTML."""
    global active_sort_preference
    if sort_by:
        active_sort_preference = sort_by
    user_id = user.id if user else None
    todos = service.list_formatted_todos(db, sort_by=sort_by, user_id=user_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos, "current_sort": active_sort_preference}
    )


@router.post("/add", response_class=HTMLResponse)
def add_todo(
    request: Request,
    title: str = Form(...),
    priority: str = Form("medium"),
    deadline: str = Form(""),
    karma: int = Form(0),
    db: Session = Depends(get_db),
    user: Optional[user_schemas.UserRead] = Depends(get_optional_user)
):
    """Creates a new todo task."""
    user_id = user.id if user else None
    if title.strip():
        todo_in = schemas.TodoCreate(
            title=title.strip(),
            priority=priority,
            deadline=deadline.strip(),
            karma=karma
        )
        repository.create_todo(db, todo_in, user_id=user_id)
    todos = service.list_formatted_todos(db, user_id=user_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@router.post("/toggle/{todo_id}", response_class=HTMLResponse)
def toggle_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """Toggles todo completed state."""
    repository.toggle_todo_completion(db, todo_id)
    todos = service.list_formatted_todos(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@router.delete("/delete/{todo_id}", response_class=HTMLResponse)
def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """Deletes a todo task and associated checklist items."""
    repository.delete_todo(db, todo_id)
    todos = service.list_formatted_todos(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@router.post("/log-time/{todo_id}", response_class=HTMLResponse)
def log_time(
    request: Request,
    todo_id: int,
    seconds: int = Form(...),
    db: Session = Depends(get_db)
):
    """Logs elapsed stopwatch seconds to a task."""
    if seconds > 0:
        db_todo = repository.get_todo_by_id(db, todo_id)
        if db_todo:
            repository.update_todo(
                db,
                todo_id,
                schemas.TodoUpdate(time_spent=db_todo.time_spent + seconds)
            )
    todos = service.list_formatted_todos(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@router.post("/update-priority/{todo_id}", response_class=HTMLResponse)
def update_priority(
    request: Request,
    todo_id: int,
    priority: str = Form(...),
    db: Session = Depends(get_db)
):
    """Updates todo priority level."""
    repository.update_todo(db, todo_id, schemas.TodoUpdate(priority=priority))
    todos = service.list_formatted_todos(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@router.post("/update-deadline/{todo_id}", response_class=HTMLResponse)
def update_deadline(
    request: Request,
    todo_id: int,
    deadline: str = Form(""),
    db: Session = Depends(get_db)
):
    """Updates todo target deadline."""
    repository.update_todo(db, todo_id, schemas.TodoUpdate(deadline=deadline.strip()))
    todos = service.list_formatted_todos(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@router.post("/update-karma/{todo_id}", response_class=HTMLResponse)
def update_karma(
    request: Request,
    todo_id: int,
    karma: int = Form(0),
    db: Session = Depends(get_db)
):
    """Updates todo karma score."""
    repository.update_todo(db, todo_id, schemas.TodoUpdate(karma=karma))
    todos = service.list_formatted_todos(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )


@router.get("/task/{todo_id}/details", response_class=HTMLResponse)
def get_task_details(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """Renders task detail modal view."""
    todo = service.get_formatted_todo(db, todo_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/task_detail.html",
        context={"todo": todo}
    )


@router.post("/update-description/{todo_id}", response_class=HTMLResponse)
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
    """Updates detailed task fields via modal drawer."""
    update_in = schemas.TodoUpdate(
        description=description,
        priority=priority,
        deadline=deadline,
        karma=karma
    )
    if title and title.strip():
        update_in.title = title.strip()

    repository.update_todo(db, todo_id, update_in)
    return service.render_task_detail_modal_with_oob(request, templates, db, todo_id, saved_success=True)


# CHECKLIST SUB-TASK ENDPOINTS
@router.post("/task/{todo_id}/checklist/add", response_class=HTMLResponse)
def add_checklist_item(
    request: Request,
    todo_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """Adds a sub-checklist item to a todo task."""
    if text.strip():
        repository.add_checklist_item(db, todo_id=todo_id, text=text.strip())
    return service.render_task_detail_modal_with_oob(request, templates, db, todo_id)


@router.post("/task/{todo_id}/checklist/{item_id}/toggle", response_class=HTMLResponse)
def toggle_checklist_item(
    request: Request,
    todo_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Toggles completion state of a sub-checklist item."""
    repository.toggle_checklist_item(db, item_id=item_id)
    return service.render_task_detail_modal_with_oob(request, templates, db, todo_id)


@router.delete("/task/{todo_id}/checklist/{item_id}/delete", response_class=HTMLResponse)
def delete_checklist_item(
    request: Request,
    todo_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Deletes a sub-checklist item."""
    repository.delete_checklist_item(db, item_id=item_id)
    return service.render_task_detail_modal_with_oob(request, templates, db, todo_id)
