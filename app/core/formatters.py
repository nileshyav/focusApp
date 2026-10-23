"""
Core presentation formatters and UI helper functions.
Follows PEP 8 guidelines and strict type annotations.
"""

from datetime import datetime, date
from typing import Dict, Optional


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
