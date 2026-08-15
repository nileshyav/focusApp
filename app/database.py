import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "todos.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            priority TEXT NOT NULL DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_todos(filter_by: str = "all", search_query: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, title, completed, priority, created_at FROM todos WHERE 1=1"
    params = []
    
    if filter_by == "active":
        query += " AND completed = 0"
    elif filter_by == "completed":
        query += " AND completed = 1"
        
    if search_query:
        query += " AND title LIKE ?"
        params.append(f"%{search_query}%")
        
    query += " ORDER BY completed ASC, id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    todos = [dict(row) for row in rows]
    conn.close()
    return todos

def get_todo(todo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, completed, priority, created_at FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_todo(title: str, priority: str = "medium"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todos (title, priority) VALUES (?, ?)", (title.strip(), priority))
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_todo(todo_id)

def toggle_todo(todo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET completed = NOT completed WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return get_todo(todo_id)

def update_todo(todo_id: int, title: str, priority: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET title = ?, priority = ? WHERE id = ?", (title.strip(), priority, todo_id))
    conn.commit()
    conn.close()
    return get_todo(todo_id)

def delete_todo(todo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()

def delete_completed():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE completed = 1")
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM todos")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 1")
    completed = cursor.fetchone()[0]
    conn.close()
    
    active = total - completed
    pct = int((completed / total * 100)) if total > 0 else 0
    return {
        "total": total,
        "active": active,
        "completed": completed,
        "pct": pct
    }
