"""
Todo domain business service layer.
Coordinates business logic, presentation formatting, and repository calls.
"""

from typing import List, Dict, Any, Optional
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import app.todos.repository as repository
import app.todos.schemas as schemas
from app.core.formatters import calculate_deadline_info


def fetch_checklist_summary(db: Session, todo_id: int) -> Dict[str, Any]:
    """Retrieves sub-checklist items and calculates completion metrics."""
    items = repository.get_checklist_items(db, todo_id=todo_id)
    items_dict = [schemas.ChecklistItemRead.model_validate(i).model_dump() for i in items]
    total = len(items_dict)
    completed_count = sum(1 for item in items_dict if item.get("completed"))
    return {
        "checklist_items": items_dict,
        "total": total,
        "completed_count": completed_count,
        "has_checklist": total > 0
    }


def list_formatted_todos(db: Session, sort_by: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all todos formatted with UI badge metadata and checklist progress."""
    todos_orm = repository.get_all_todos(db, sort_by=sort_by, user_id=user_id)
    todos = []
    for t in todos_orm:
        t_dict = schemas.TodoRead.model_validate(t).model_dump()
        t_dict["deadline_info"] = calculate_deadline_info(t_dict.get("deadline"))
        t_dict["checklist_info"] = fetch_checklist_summary(db, t_dict["id"])
        todos.append(t_dict)
    return todos


def get_formatted_todo(db: Session, todo_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single todo formatted for UI rendering."""
    t_orm = repository.get_todo_by_id(db, todo_id)
    if not t_orm:
        return None
    t_dict = schemas.TodoRead.model_validate(t_orm).model_dump()
    t_dict["deadline_info"] = calculate_deadline_info(t_dict.get("deadline"))
    t_dict["checklist_info"] = fetch_checklist_summary(db, todo_id)
    return t_dict


def render_task_detail_modal_with_oob(
    request: Request,
    templates: Jinja2Templates,
    db: Session,
    todo_id: int,
    saved_success: bool = False
) -> HTMLResponse:
    """Renders task detail modal and HTMX Out-Of-Band (OOB) todo list updates."""
    todo = get_formatted_todo(db, todo_id)
    todos = list_formatted_todos(db)

    modal_html = templates.get_template("partials/task_detail.html").render(
        request=request,
        todo=todo,
        saved_success=saved_success
    )
    list_html = templates.get_template("partials/todo_list.html").render(
        request=request,
        todos=todos
    )
    oob_list_html = f'<div id="todo-list" class="flex-1 overflow-y-auto w-full pr-1" hx-swap-oob="true">{list_html}</div>'

    return HTMLResponse(content=modal_html + "\n" + oob_list_html)
