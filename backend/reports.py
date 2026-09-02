import csv
from datetime import UTC, date, datetime, time, timedelta
from io import StringIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import crud, models
from .enums import AssignedTeam, Department, TicketCategory, TicketPriority, TicketStatus


TICKET_REPORT_HEADERS = [
    "Ticket Number",
    "Title",
    "Category",
    "Priority",
    "Status",
    "Assigned Team",
    "Department",
    "Requester Name",
    "Requester Email",
    "Created At",
    "Updated At",
    "First Response At",
    "Resolved At",
    "Resolution Notes",
]


# Convert enum values and None values into CSV-friendly text.
def format_value(value) -> str:
    if value is None:
        return ""

    if hasattr(value, "value"):
        return value.value

    return str(value)


# Convert optional datetimes into readable CSV text.
def format_datetime(value: datetime | None) -> str:
    if value is None:
        return ""

    return value.isoformat(sep=" ", timespec="seconds")


# Convert a date-only query parameter into the start of that UTC day.
def start_of_day(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=UTC)


# Build report filters from existing ticket filters plus optional date bounds.
def build_report_filters(
    ticket_status: TicketStatus | None = None,
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    department: Department | None = None,
    assigned_team: AssignedTeam | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list:
    filters = crud.build_ticket_filters(
        ticket_status=ticket_status,
        category=category,
        priority=priority,
        department=department,
        assigned_team=assigned_team,
    )

    if start_date is not None:
        # Include tickets created on or after the start date.
        filters.append(models.Ticket.created_at >= start_of_day(start_date))

    if end_date is not None:
        # Add one day and use a less-than comparison so the end date is inclusive.
        exclusive_end = start_of_day(end_date + timedelta(days=1))
        filters.append(models.Ticket.created_at < exclusive_end)

    return filters


# Retrieve all tickets that should be included in the CSV export.
def get_report_tickets(
    db: Session,
    ticket_status: TicketStatus | None = None,
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    department: Department | None = None,
    assigned_team: AssignedTeam | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[models.Ticket]:
    filters = build_report_filters(
        ticket_status=ticket_status,
        category=category,
        priority=priority,
        department=department,
        assigned_team=assigned_team,
        start_date=start_date,
        end_date=end_date,
    )

    query = (
        select(models.Ticket)
        .where(*filters)
        .order_by(models.Ticket.created_at.desc(), models.Ticket.id.desc())
    )

    return list(db.scalars(query).all())


# Render tickets into a CSV string with a stable column order.
def generate_ticket_csv(tickets: list[models.Ticket]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(TICKET_REPORT_HEADERS)

    for ticket in tickets:
        writer.writerow(
            [
                ticket.ticket_number,
                ticket.title,
                format_value(ticket.category),
                format_value(ticket.priority),
                format_value(ticket.status),
                format_value(ticket.assigned_team),
                format_value(ticket.department),
                ticket.requester_name,
                ticket.requester_email,
                format_datetime(ticket.created_at),
                format_datetime(ticket.updated_at),
                format_datetime(ticket.first_response_at),
                format_datetime(ticket.resolved_at),
                ticket.resolution_notes or "",
            ]
        )

    return output.getvalue()
