import os
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.database import (
    init_db, get_todos, get_todo, add_todo, toggle_todo, 
    update_todo, delete_todo, delete_completed, get_stats
)

app = FastAPI(title="FastAPI HTMX Todo Application")

# Absolute paths for templates & static directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2 Templates setup
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    todos = get_todos()
    stats = get_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"todos": todos, "stats": stats}
    )

@app.get("/todos", response_class=HTMLResponse)
def read_todos(request: Request, filter: str = "all", q: str = ""):
    todos = get_todos(filter_by=filter, search_query=q)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos}
    )

@app.post("/todos", response_class=HTMLResponse)
def create_todo(request: Request, title: str = Form(...), priority: str = Form("medium")):
    add_todo(title=title, priority=priority)
    todos = get_todos()
    stats = get_stats()
    
    list_html = templates.get_template("partials/todo_list.html").render(request=request, todos=todos)
    stats_html = templates.get_template("partials/stats.html").render(request=request, stats=stats)
    return HTMLResponse(content=list_html + "\n" + stats_html)

@app.patch("/todos/{todo_id}/toggle", response_class=HTMLResponse)
def toggle_todo_status(request: Request, todo_id: int):
    updated_todo = toggle_todo(todo_id)
    stats = get_stats()
    
    item_html = templates.get_template("partials/todo_item.html").render(request=request, todo=updated_todo)
    stats_html = templates.get_template("partials/stats.html").render(request=request, stats=stats)
    return HTMLResponse(content=item_html + "\n" + stats_html)

@app.get("/todos/{todo_id}/edit", response_class=HTMLResponse)
def get_edit_form(request: Request, todo_id: int):
    todo = get_todo(todo_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_edit.html",
        context={"todo": todo}
    )

@app.get("/todos/{todo_id}/item", response_class=HTMLResponse)
def get_todo_item(request: Request, todo_id: int):
    todo = get_todo(todo_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_item.html",
        context={"todo": todo}
    )

@app.put("/todos/{todo_id}", response_class=HTMLResponse)
def edit_todo(request: Request, todo_id: int, title: str = Form(...), priority: str = Form("medium")):
    updated_todo = update_todo(todo_id, title=title, priority=priority)
    stats = get_stats()
    
    item_html = templates.get_template("partials/todo_item.html").render(request=request, todo=updated_todo)
    stats_html = templates.get_template("partials/stats.html").render(request=request, stats=stats)
    return HTMLResponse(content=item_html + "\n" + stats_html)

@app.delete("/todos/{todo_id}", response_class=HTMLResponse)
def remove_todo(request: Request, todo_id: int):
    delete_todo(todo_id)
    stats = get_stats()
    
    stats_html = templates.get_template("partials/stats.html").render(request=request, stats=stats)
    return HTMLResponse(content=stats_html)

@app.post("/todos/clear-completed", response_class=HTMLResponse)
def clear_completed_todos(request: Request):
    delete_completed()
    todos = get_todos()
    stats = get_stats()
    
    list_html = templates.get_template("partials/todo_list.html").render(request=request, todos=todos)
    stats_html = templates.get_template("partials/stats.html").render(request=request, stats=stats)
    return HTMLResponse(content=list_html + "\n" + stats_html)
