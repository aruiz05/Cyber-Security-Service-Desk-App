from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import reports
from ..database import get_db
from ..enums import AssignedTeam, Department, TicketCategory, TicketPriority, TicketStatus


# Router groups CSV export endpoints under /reports in Swagger.
router = APIRouter(prefix="/reports", tags=["Reports"])


# Download a CSV export of tickets with optional filters.
@router.get("/tickets.csv")
def download_ticket_report(
    # Alias keeps the public query parameter named "status".
    ticket_status: TicketStatus | None = Query(default=None, alias="status"),
    # Enum-typed filters give Swagger valid values and FastAPI validation.
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    department: Department | None = None,
    assigned_team: AssignedTeam | None = None,
    # Date filters apply to the ticket created_at date.
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> Response:
    if start_date is not None and end_date is not None and end_date < start_date:
        # A reversed range is a client input problem.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be on or after start_date",
        )

    tickets = reports.get_report_tickets(
        db=db,
        ticket_status=ticket_status,
        category=category,
        priority=priority,
        department=department,
        assigned_team=assigned_team,
        start_date=start_date,
        end_date=end_date,
    )
    csv_content = reports.generate_ticket_csv(tickets)

    # Content-Disposition tells browsers to download the CSV with this filename.
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="cybersecurity_ticket_report.csv"'
        },
    )
