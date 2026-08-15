import os
import sqlite3
import random
from datetime import datetime, date, timedelta
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="FastAPI + HTMX Todo App with Priorities, Deadlines, Karma, Checklists & Descriptions")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "todos.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

active_sort_preference = "created_at"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def seed_sample_database():
    """Sample data seeding disabled to keep clean user database."""
    pass

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            time_spent INTEGER NOT NULL DEFAULT 0,
            description TEXT DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'medium',
            deadline TEXT DEFAULT '',
            karma INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            todo_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (todo_id) REFERENCES todos(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            todo_id INTEGER,
            duration_minutes INTEGER NOT NULL DEFAULT 25,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (todo_id) REFERENCES todos(id) ON DELETE SET NULL
        )
    """)

    try:
        cursor.execute("ALTER TABLE todos ADD COLUMN time_spent INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE todos ADD COLUMN description TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE todos ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE todos ADD COLUMN deadline TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE todos ADD COLUMN karma INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_deadline ON todos(deadline)")

    conn.commit()
    conn.close()

    seed_sample_database()

init_db()

def calculate_deadline_info(deadline_str: str):
    if not deadline_str:
        return {"text": "Set deadline", "status": "none", "class": "bg-slate-800/80 text-slate-400 border-white/10 hover:border-white/30"}
    try:
        due_date = datetime.strptime(deadline_str.split("T")[0], "%Y-%m-%d").date()
        today = date.today()
        diff = (due_date - today).days
        
        if diff == 0:
            return {"text": "⚠️ Due Today", "status": "today", "class": "bg-amber-500/20 text-amber-300 border-amber-500/40"}
        elif diff == 1:
            return {"text": "⏳ 1 day left", "status": "future", "class": "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"}
        elif diff > 1:
            return {"text": f"⏳ {diff} days left", "status": "future", "class": "bg-indigo-500/20 text-indigo-300 border-indigo-500/40"}
        elif diff == -1:
            return {"text": "🚨 1 day overdue", "status": "overdue", "class": "bg-rose-500/20 text-rose-300 border-rose-500/40"}
        else:
            return {"text": f"🚨 {abs(diff)} days overdue", "status": "overdue", "class": "bg-rose-500/20 text-rose-300 border-rose-500/40"}
    except Exception:
        return {"text": "Set deadline", "status": "none", "class": "bg-slate-800/80 text-slate-400 border-white/10"}

def fetch_checklist_items(todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checklist_items WHERE todo_id = ? ORDER BY id ASC", (todo_id,))
    rows = cursor.fetchall()
    conn.close()
    items = [dict(r) for r in rows]
    total = len(items)
    completed_count = sum(1 for item in items if item['completed'])
    return {
        "checklist_items": items,
        "total": total,
        "completed_count": completed_count,
        "has_checklist": total > 0
    }

def fetch_todos(sort_by: str = None):
    global active_sort_preference
    if sort_by:
        active_sort_preference = sort_by
    else:
        sort_by = active_sort_preference

    conn = get_db()
    cursor = conn.cursor()
    
    if sort_by == "priority":
        query = """
            SELECT * FROM todos 
            ORDER BY completed ASC, 
                     CASE priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                        ELSE 4 
                     END ASC, 
                     id DESC
        """
    elif sort_by == "deadline":
        query = """
            SELECT * FROM todos 
            ORDER BY completed ASC, 
                     CASE WHEN deadline IS NULL OR deadline = '' THEN 1 ELSE 0 END ASC, 
                     deadline ASC, 
                     id DESC
        """
    else:
        query = "SELECT * FROM todos ORDER BY completed ASC, id DESC"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    todos = []
    for r in rows:
        todo_dict = dict(r)
        todo_dict["deadline_info"] = calculate_deadline_info(todo_dict.get("deadline", ""))
        todo_dict["checklist_info"] = fetch_checklist_items(todo_dict["id"])
        todos.append(todo_dict)
    return todos

def fetch_performance_data():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(duration_minutes), 0) FROM pomodoro_sessions")
    row = cursor.fetchone()
    total_sessions = row[0]
    total_focus_minutes = row[1]
    total_focus_hours = round(total_focus_minutes / 60.0, 1)

    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 1")
    total_completed_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT DATE(completed_at)) FROM pomodoro_sessions")
    active_days_count = max(1, cursor.fetchone()[0])
    avg_daily_hours = round((total_focus_minutes / 60.0) / active_days_count, 1)

    today = date.today()
    start_of_current_week = today - timedelta(days=today.weekday())
    start_of_previous_week = start_of_current_week - timedelta(days=7)

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    current_week_hours = [0.0] * 7
    previous_week_hours = [0.0] * 7

    cursor.execute("""
        SELECT DATE(completed_at) as session_date, SUM(duration_minutes) as total_mins
        FROM pomodoro_sessions
        WHERE DATE(completed_at) >= ?
        GROUP BY DATE(completed_at)
    """, (start_of_previous_week.isoformat(),))

    date_totals = {r["session_date"]: r["total_mins"] for r in cursor.fetchall()}

    this_week_mins = 0
    last_week_mins = 0

    for idx in range(7):
        cur_d = (start_of_current_week + timedelta(days=idx)).isoformat()
        prev_d = (start_of_previous_week + timedelta(days=idx)).isoformat()

        c_mins = date_totals.get(cur_d, 0)
        p_mins = date_totals.get(prev_d, 0)

        current_week_hours[idx] = round(c_mins / 60.0, 1)
        previous_week_hours[idx] = round(p_mins / 60.0, 1)

        this_week_mins += c_mins
        last_week_mins += p_mins

    this_week_hours_sum = round(this_week_mins / 60.0, 1)
    last_week_hours_sum = round(last_week_mins / 60.0, 1)

    if last_week_hours_sum > 0:
        weekly_trend_pct = round(((this_week_hours_sum - last_week_hours_sum) / last_week_hours_sum) * 100, 1)
    else:
        weekly_trend_pct = 100.0 if this_week_hours_sum > 0 else 0.0

    # Multi-Week Total Study Time (Last 26 Weeks / 6 Months Overview)
    weeks_data = []
    for w in range(25, -1, -1):
        w_start = start_of_current_week - timedelta(weeks=w)
        w_end = w_start + timedelta(days=6)
        
        cursor.execute("""
            SELECT COALESCE(SUM(duration_minutes), 0), COUNT(*)
            FROM pomodoro_sessions
            WHERE DATE(completed_at) >= ? AND DATE(completed_at) <= ?
        """, (w_start.isoformat(), w_end.isoformat()))
        w_row = cursor.fetchone()
        w_mins = w_row[0]
        w_sessions = w_row[1]
        w_hrs = round(w_mins / 60.0, 1)
        
        if w == 0:
            label = "This Week"
        elif w == 1:
            label = "Last Week"
        else:
            label = f"Wk {26-w} ({w_start.strftime('%b %d')})"

        weeks_data.append({
            "week_label": label,
            "date_range": f"{w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}",
            "hours": w_hrs,
            "minutes": w_mins,
            "sessions": w_sessions
        })

    cursor.execute("""
        SELECT DATE(completed_at) as log_date, 
               COUNT(*) as sessions, 
               SUM(duration_minutes) as mins
        FROM pomodoro_sessions
        GROUP BY DATE(completed_at)
        ORDER BY log_date DESC
        LIMIT 14
    """)
    daily_rows = cursor.fetchall()
    
    daily_breakdown = []
    for r in daily_rows:
        d_str = r["log_date"]
        try:
            d_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
            day_name = d_obj.strftime("%a, %b %d")
        except Exception:
            day_name = d_str
        d_mins = r["mins"] or 0
        d_hrs = round(d_mins / 60.0, 1)
        
        if d_hrs >= 3.0:
            intensity = {"label": "⚡ High Output", "class": "badge-primary"}
        elif d_hrs >= 1.5:
            intensity = {"label": "🔥 Good Focus", "class": "badge-secondary"}
        else:
            intensity = {"label": "🌱 Steady Progress", "class": "badge-accent"}

        daily_breakdown.append({
            "date": d_str,
            "day_name": day_name,
            "sessions": r["sessions"],
            "minutes": d_mins,
            "hours": d_hrs,
            "intensity": intensity
        })

    cursor.execute("SELECT priority, COUNT(*) as count FROM todos GROUP BY priority")
    priority_counts = {r["priority"].lower(): r["count"] for r in cursor.fetchall()}
    priority_stats = {
        "high": priority_counts.get("high", 0),
        "medium": priority_counts.get("medium", 0),
        "low": priority_counts.get("low", 0)
    }

    cursor.execute("SELECT COALESCE(ROUND(AVG(karma), 1), 0.0) FROM todos")
    avg_karma_score = cursor.fetchone()[0]

    conn.close()

    return {
        "total_sessions": total_sessions,
        "total_focus_hours": total_focus_hours,
        "total_completed_tasks": total_completed_tasks,
        "avg_daily_hours": avg_daily_hours,
        "this_week_hours_sum": this_week_hours_sum,
        "last_week_hours_sum": last_week_hours_sum,
        "weekly_trend_pct": weekly_trend_pct,
        "days_of_week": days_of_week,
        "current_week_hours": current_week_hours,
        "previous_week_hours": previous_week_hours,
        "weeks_data": weeks_data,
        "daily_breakdown": daily_breakdown,
        "priority_stats": priority_stats,
        "avg_karma_score": avg_karma_score
    }

def fetch_todo(todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        todo_dict = dict(row)
        todo_dict["deadline_info"] = calculate_deadline_info(todo_dict.get("deadline", ""))
        todo_dict["checklist_info"] = fetch_checklist_items(todo_dict["id"])
        return todo_dict
    return None

def render_detail_and_oob(request: Request, todo_id: int, saved_success: bool = False):
    todo = fetch_todo(todo_id)
    todos = fetch_todos()

    modal_html = templates.get_template("partials/task_detail.html").render(request=request, todo=todo, saved_success=saved_success)
    list_html = templates.get_template("partials/todo_list.html").render(request=request, todos=todos)

    oob_list_html = f'<div id="todo-list" class="flex-1 overflow-y-auto w-full pr-1" hx-swap-oob="true">{list_html}</div>'

    return HTMLResponse(content=modal_html + "\n" + oob_list_html)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="index.html", context={"todos": todos, "current_sort": active_sort_preference})

@app.get("/performance", response_class=HTMLResponse)
def performance_report_page(request: Request):
    report = fetch_performance_data()
    return templates.TemplateResponse(request=request, name="performance.html", context={"report": report})

@app.post("/pomodoro/complete")
def log_pomodoro_session(duration_minutes: int = Form(25), todo_id: int = Form(None)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pomodoro_sessions (todo_id, duration_minutes) VALUES (?, ?)",
        (todo_id, duration_minutes)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/todos", response_class=HTMLResponse)
def get_todos_partial(request: Request, sort_by: str = Query(None)):
    todos = fetch_todos(sort_by=sort_by)
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos, "current_sort": active_sort_preference})

@app.post("/add", response_class=HTMLResponse)
def add_todo(request: Request, title: str = Form(...), priority: str = Form("medium"), deadline: str = Form(""), karma: int = Form(0)):
    if title.strip():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO todos (title, completed, time_spent, description, priority, deadline, karma) VALUES (?, 0, 0, '', ?, ?, ?)",
            (title.strip(), priority.lower(), deadline.strip(), max(0, min(5, karma)))
        )
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
    cursor.execute("DELETE FROM checklist_items WHERE todo_id = ?", (todo_id,))
    conn.commit()
    conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

@app.post("/log-time/{todo_id}", response_class=HTMLResponse)
def log_time(request: Request, todo_id: int, seconds: int = Form(...)):
    if seconds > 0:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET time_spent = time_spent + ? WHERE id = ?", (seconds, todo_id))
        conn.commit()
        conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

@app.post("/update-priority/{todo_id}", response_class=HTMLResponse)
def update_priority(request: Request, todo_id: int, priority: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET priority = ? WHERE id = ?", (priority.lower(), todo_id))
    conn.commit()
    conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

@app.post("/update-deadline/{todo_id}", response_class=HTMLResponse)
def update_deadline(request: Request, todo_id: int, deadline: str = Form("")):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET deadline = ? WHERE id = ?", (deadline.strip(), todo_id))
    conn.commit()
    conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

@app.post("/update-karma/{todo_id}", response_class=HTMLResponse)
def update_karma(request: Request, todo_id: int, karma: int = Form(0)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET karma = ? WHERE id = ?", (max(0, min(5, karma)), todo_id))
    conn.commit()
    conn.close()
    todos = fetch_todos()
    return templates.TemplateResponse(request=request, name="partials/todo_list.html", context={"todos": todos})

@app.get("/task/{todo_id}/details", response_class=HTMLResponse)
def get_task_details(request: Request, todo_id: int):
    todo = fetch_todo(todo_id)
    return templates.TemplateResponse(request=request, name="partials/task_detail.html", context={"todo": todo})

@app.post("/update-description/{todo_id}", response_class=HTMLResponse)
def update_description(
    request: Request, 
    todo_id: int, 
    title: str = Form(None),
    description: str = Form(""), 
    priority: str = Form("medium"), 
    deadline: str = Form(""), 
    karma: int = Form(0)
):
    conn = get_db()
    cursor = conn.cursor()
    if title and title.strip():
        cursor.execute(
            "UPDATE todos SET title = ?, description = ?, priority = ?, deadline = ?, karma = ? WHERE id = ?", 
            (title.strip(), description.strip(), priority.lower(), deadline.strip(), max(0, min(5, karma)), todo_id)
        )
    else:
        cursor.execute(
            "UPDATE todos SET description = ?, priority = ?, deadline = ?, karma = ? WHERE id = ?", 
            (description.strip(), priority.lower(), deadline.strip(), max(0, min(5, karma)), todo_id)
        )
    conn.commit()
    conn.close()
    return render_detail_and_oob(request, todo_id, saved_success=True)

# CHECKLIST SUB-TODO ENDPOINTS
@app.post("/task/{todo_id}/checklist/add", response_class=HTMLResponse)
def add_checklist_item(request: Request, todo_id: int, text: str = Form(...)):
    if text.strip():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO checklist_items (todo_id, text, completed) VALUES (?, ?, 0)", (todo_id, text.strip()))
        conn.commit()
        conn.close()
    return render_detail_and_oob(request, todo_id)

@app.post("/task/{todo_id}/checklist/{item_id}/toggle", response_class=HTMLResponse)
def toggle_checklist_item(request: Request, todo_id: int, item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE checklist_items SET completed = NOT completed WHERE id = ? AND todo_id = ?", (item_id, todo_id))
    conn.commit()
    conn.close()
    return render_detail_and_oob(request, todo_id)

@app.delete("/task/{todo_id}/checklist/{item_id}/delete", response_class=HTMLResponse)
def delete_checklist_item(request: Request, todo_id: int, item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM checklist_items WHERE id = ? AND todo_id = ?", (item_id, todo_id))
    conn.commit()
    conn.close()
    return render_detail_and_oob(request, todo_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
