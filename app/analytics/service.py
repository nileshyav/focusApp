"""
Analytics domain business service.
Aggregates cross-domain metrics from todos and pomodoro sessions.
"""

from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from sqlalchemy.orm import Session

import app.todos.repository as todo_repo
import app.pomodoro.repository as pomodoro_repo


def compute_performance_analytics(db: Session) -> Dict[str, Any]:
    """
    Computes performance analytics context dictionary for performance.html report.

    Args:
        db (Session): Database session.

    Returns:
        Dict[str, Any]: Complete analytics metrics context.
    """
    todos = todo_repo.get_all_todos(db)
    sessions = pomodoro_repo.get_all_pomodoro_sessions(db)

    total_tasks = len(todos)
    completed_tasks = sum(1 for t in todos if t.completed)
    active_tasks = total_tasks - completed_tasks
    completion_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    total_stopwatch_seconds = sum(t.time_spent for t in todos)
    total_pomodoro_minutes = sum(s.duration_minutes for s in sessions)
    total_focus_minutes = (total_stopwatch_seconds // 60) + total_pomodoro_minutes
    total_karma = sum(t.karma for t in todos if t.completed)

    # Priority Breakdown Stats
    priority_stats = {
        "high": sum(1 for t in todos if t.priority == "high"),
        "medium": sum(1 for t in todos if t.priority == "medium"),
        "low": sum(1 for t in todos if t.priority == "low")
    }

    # Weekly Focus Hours Breakdown (Mon - Sun)
    today = date.today()
    start_of_current_week = today - timedelta(days=today.weekday())
    start_of_prev_week = start_of_current_week - timedelta(days=7)

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    current_week_hours = [0.0] * 7
    previous_week_hours = [0.0] * 7

    for session in sessions:
        if session.completed_at:
            session_date = session.completed_at.date()
            if start_of_current_week <= session_date <= today:
                day_idx = session_date.weekday()
                current_week_hours[day_idx] += round(session.duration_minutes / 60.0, 2)
            elif start_of_prev_week <= session_date < start_of_current_week:
                day_idx = session_date.weekday()
                previous_week_hours[day_idx] += round(session.duration_minutes / 60.0, 2)

    this_week_hours_sum = round(sum(current_week_hours), 1)
    prev_week_hours_sum = round(sum(previous_week_hours), 1)

    if prev_week_hours_sum > 0:
        weekly_trend_pct = int(((this_week_hours_sum - prev_week_hours_sum) / prev_week_hours_sum) * 100)
    else:
        weekly_trend_pct = 100 if this_week_hours_sum > 0 else 0

    avg_daily_hours = round(this_week_hours_sum / 7.0, 1)

    completed_todos_with_karma = [t for t in todos if t.completed and t.karma > 0]
    if completed_todos_with_karma:
        avg_karma_score = round(sum(t.karma for t in completed_todos_with_karma) / len(completed_todos_with_karma), 1)
    else:
        avg_karma_score = 0.0

    weeks_data = [
        {"week_label": "Week 1", "hours": round(prev_week_hours_sum, 1)},
        {"week_label": "Week 2 (Current)", "hours": round(this_week_hours_sum, 1)}
    ]

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_completed_tasks": completed_tasks,
        "active_tasks": active_tasks,
        "completion_rate": completion_rate,
        "total_focus_minutes": total_focus_minutes,
        "total_pomodoro_sessions": len(sessions),
        "total_karma": total_karma,
        "this_week_hours_sum": this_week_hours_sum,
        "weekly_trend_pct": weekly_trend_pct,
        "avg_daily_hours": avg_daily_hours,
        "avg_karma_score": avg_karma_score,
        "priority_stats": priority_stats,
        "weeks_data": weeks_data,
        "days_of_week": days_of_week,
        "current_week_hours": current_week_hours,
        "previous_week_hours": previous_week_hours
    }
