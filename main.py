import os
import sqlite3
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Simple FastAPI + HTMX Todo App")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "todos.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

def fetch_todos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    todos = cursor.fetchall()
    conn.close()
    return todos

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="index.html", context={"todos": todos})

@app.post("/add", response_class=HTMLResponse)
def add_todo(request: Request, title: str = Form(...)):
    if title.strip():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (title, completed) VALUES (?, 0)", (title.strip(),))
        conn.commit()
        conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

@app.post("/toggle/{todo_id}", response_class=HTMLResponse)
def toggle_todo(request: Request, todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET completed = NOT completed WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

@app.delete("/delete/{todo_id}", response_class=HTMLResponse)
def delete_todo(request: Request, todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
