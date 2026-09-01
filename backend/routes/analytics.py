from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import analytics, schemas
from ..database import get_db


# Router groups all analytics endpoints under /analytics in Swagger.
router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Return top-level ticket and SLA summary metrics.
@router.get("/summary", response_model=schemas.AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)) -> schemas.AnalyticsSummary:
    return analytics.get_summary(db)


# Return ticket counts by cybersecurity category.
@router.get("/categories", response_model=list[schemas.CategoryCount])
def get_category_counts(db: Session = Depends(get_db)) -> list[schemas.CategoryCount]:
    return analytics.get_category_counts(db)


# Return ticket counts by workflow status.
@router.get("/status", response_model=list[schemas.StatusCount])
def get_status_counts(db: Session = Depends(get_db)) -> list[schemas.StatusCount]:
    return analytics.get_status_counts(db)


# Return ticket counts by priority.
@router.get("/priorities", response_model=list[schemas.PriorityCount])
def get_priority_counts(db: Session = Depends(get_db)) -> list[schemas.PriorityCount]:
    return analytics.get_priority_counts(db)


# Return daily created/resolved ticket counts for a date range.
@router.get("/trends", response_model=list[schemas.TrendPoint])
def get_ticket_trends(
    # Limit the trend window to a practical range for the API.
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> list[schemas.TrendPoint]:
    return analytics.get_ticket_trends(db, days=days)


# Return overall and per-priority first-response SLA results.
@router.get("/sla", response_model=schemas.SLASummary)
def get_sla_summary(db: Session = Depends(get_db)) -> schemas.SLASummary:
    return analytics.get_sla_summary(db)
