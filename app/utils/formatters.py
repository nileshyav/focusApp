"""
Formatting utilities and helpers for UI rendering and HTMX responses.
Follows PEP 8 guidelines with strict type annotations.
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas


def calculate_deadline_info(deadline_str: Optional[str]) -> Dict[str, str]:
    """
    Calculates remaining days until deadline and returns UI badge styling dictionary.

    Args:
        deadline_str (Optional[str]): ISO date string (YYYY-MM-DD) or empty string.

    Returns:
        Dict[str, str]: Dictionary containing badge text, status label, and CSS classes.
    """
    if not deadline_str:
        return {
            "text": "Set deadline",
            "status": "none",
            "class": "bg-slate-800/80 text-slate-400 border-white/10 hover:border-white/30"
        }
    try:
        due_date = datetime.strptime(deadline_str.split("T")[0], "%Y-%m-%d").date()
        today = date.today()
        diff = (due_date - today).days

        if diff == 0:
            return {
                "text": "⚠️ Due Today",
                "status": "today",
                "class": "bg-amber-500/20 text-amber-300 border-amber-500/40"
            }
        elif diff == 1:
            return {
                "text": "⏳ 1 day left",
                "status": "future",
                "class": "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"
            }
        elif diff > 1:
            return {
                "text": f"⏳ {diff} days left",
                "status": "future",
                "class": "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"
            }
        elif diff == -1:
            return {
                "text": "🚨 1 day overdue",
                "status": "overdue",
                "class": "bg-rose-500/20 text-rose-300 border-rose-500/40"
            }
        else:
            return {
                "text": f"🚨 {abs(diff)} days overdue",
                "status": "overdue",
                "class": "bg-rose-500/20 text-rose-300 border-rose-500/40"
            }
    except Exception:
        return {
            "text": "Set deadline",
            "status": "none",
            "class": "bg-slate-800/80 text-slate-400 border-white/10"
        }


def fetch_checklist_items_formatted(db: Session, todo_id: int) -> Dict[str, Any]:
    """
    Fetches sub-checklist items for a todo task formatted for template context.
    """
    items = crud.get_checklist_items(db, todo_id=todo_id)
    items_dict = [schemas.ChecklistItemRead.model_validate(i).model_dump() for i in items]
    total = len(items_dict)
    completed_count = sum(1 for item in items_dict if item.get("completed"))
    return {
        "checklist_items": items_dict,
        "total": total,
        "completed_count": completed_count,
        "has_checklist": total > 0
    }


def fetch_todos_formatted(db: Session, sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches all todos ordered by preference and enriches them with UI badge metadata.
    """
    todos_orm = crud.get_todos(db, sort_by=sort_by)
    todos = []
    for t in todos_orm:
        t_dict = schemas.TodoRead.model_validate(t).model_dump()
        t_dict["deadline_info"] = calculate_deadline_info(t_dict.get("deadline"))
        t_dict["checklist_info"] = fetch_checklist_items_formatted(db, t_dict["id"])
        todos.append(t_dict)
    return todos


def fetch_todo_formatted(db: Session, todo_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a single todo enriched with deadline badge and checklist info.
    """
    t_orm = crud.get_todo(db, todo_id)
    if not t_orm:
        return None
    t_dict = schemas.TodoRead.model_validate(t_orm).model_dump()
    t_dict["deadline_info"] = calculate_deadline_info(t_dict.get("deadline"))
    t_dict["checklist_info"] = fetch_checklist_items_formatted(db, t_dict["id"])
    return t_dict


def render_detail_and_oob(
    request: Request,
    templates: Jinja2Templates,
    db: Session,
    todo_id: int,
    saved_success: bool = False
) -> HTMLResponse:
    """
    Renders task detail modal HTML combined with HTMX Out-Of-Band (OOB) todo list updates.
    """
    todo = fetch_todo_formatted(db, todo_id)
    todos = fetch_todos_formatted(db)

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
