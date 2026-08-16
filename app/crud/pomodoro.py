from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.pomodoro import PomodoroSession
from app.models.todo import Todo

def create_pomodoro_session(db: Session, duration_minutes: int = 25, todo_id: Optional[int] = None) -> PomodoroSession:
    session = PomodoroSession(duration_minutes=duration_minutes, todo_id=todo_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_performance_data(db: Session) -> Dict[str, Any]:
    sessions = db.query(PomodoroSession).all()
    
    total_sessions = len(sessions)
    total_focus_minutes = sum(s.duration_minutes for s in sessions)
    total_focus_hours = round(total_focus_minutes / 60.0, 1)

    total_completed_tasks = db.query(Todo).filter(Todo.completed == True).count()

    dates_set = {s.completed_at.strftime("%Y-%m-%d") for s in sessions if s.completed_at}
    active_days_count = max(1, len(dates_set))
    avg_daily_hours = round((total_focus_minutes / 60.0) / active_days_count, 1)

    today = date.today()
    start_of_current_week = today - timedelta(days=today.weekday())
    start_of_previous_week = start_of_current_week - timedelta(days=7)

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    current_week_hours = [0.0] * 7
    previous_week_hours = [0.0] * 7

    date_totals = {}
    for s in sessions:
        if s.completed_at:
            c_at = s.completed_at.strftime("%Y-%m-%d")
            date_totals[c_at] = date_totals.get(c_at, 0) + s.duration_minutes

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

    weeks_data = []
    for w in range(25, -1, -1):
        w_start = start_of_current_week - timedelta(weeks=w)
        w_end = w_start + timedelta(days=6)
        
        w_start_str = w_start.isoformat()
        w_end_str = w_end.isoformat()

        w_mins = sum(
            s.duration_minutes for s in sessions
            if s.completed_at and w_start_str <= s.completed_at.strftime("%Y-%m-%d") <= w_end_str
        )
        w_sessions = sum(
            1 for s in sessions
            if s.completed_at and w_start_str <= s.completed_at.strftime("%Y-%m-%d") <= w_end_str
        )
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

    sorted_dates = sorted(date_totals.keys(), reverse=True)[:14]
    daily_breakdown = []
    for d_str in sorted_dates:
        try:
            d_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
            day_name = d_obj.strftime("%a, %b %d")
        except Exception:
            day_name = d_str
        d_mins = date_totals[d_str]
        d_hrs = round(d_mins / 60.0, 1)
        d_sessions = sum(1 for s in sessions if s.completed_at and s.completed_at.strftime("%Y-%m-%d") == d_str)
        
        if d_hrs >= 3.0:
            intensity = {"label": "⚡ High Output", "class": "badge-primary"}
        elif d_hrs >= 1.5:
            intensity = {"label": "🔥 Good Focus", "class": "badge-secondary"}
        else:
            intensity = {"label": "🌱 Steady Progress", "class": "badge-accent"}

        daily_breakdown.append({
            "date": d_str,
            "day_name": day_name,
            "sessions": d_sessions,
            "minutes": d_mins,
            "hours": d_hrs,
            "intensity": intensity
        })

    all_todos = db.query(Todo).all()
    priority_counts = {}
    karma_total = 0
    karma_count = 0
    for t in all_todos:
        p = str(t.priority).lower()
        priority_counts[p] = priority_counts.get(p, 0) + 1
        if t.karma is not None:
            karma_total += t.karma
            karma_count += 1

    priority_stats = {
        "high": priority_counts.get("high", 0),
        "medium": priority_counts.get("medium", 0),
        "low": priority_counts.get("low", 0)
    }

    avg_karma_score = round(karma_total / karma_count, 1) if karma_count > 0 else 0.0

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
