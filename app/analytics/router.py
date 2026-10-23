"""
Analytics domain FastAPI router.
Handles HTTP endpoints for rendering performance reports and metrics views.
"""

import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
import app.analytics.service as service

router = APIRouter(tags=["Analytics"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/performance", response_class=HTMLResponse)
def performance_report_page(request: Request, db: Session = Depends(get_db)):
    """Renders productivity metrics and focus analytics report page."""
    report = service.compute_performance_analytics(db)
    return templates.TemplateResponse(
        request=request,
        name="performance.html",
        context={"report": report}
    )
