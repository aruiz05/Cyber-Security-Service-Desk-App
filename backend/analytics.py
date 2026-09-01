from collections import Counter
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas, sla
from .enums import TicketCategory, TicketPriority, TicketStatus


# Statuses still considered active work.
OPEN_STATUSES = {
    TicketStatus.NEW,
    TicketStatus.IN_PROGRESS,
    TicketStatus.WAITING_FOR_USER,
}

# Statuses considered completed work.
COMPLETED_STATUSES = {
    TicketStatus.RESOLVED,
    TicketStatus.CLOSED,
}


# Start of the current UTC calendar day.
def start_of_today_utc() -> datetime:
    today = sla.utc_now().date()
    return datetime.combine(today, time.min, tzinfo=UTC)


# Monday start of the current UTC week.
def start_of_week_utc() -> datetime:
    today = sla.utc_now().date()
    monday = today - timedelta(days=today.weekday())
    return datetime.combine(monday, time.min, tzinfo=UTC)


# Load tickets for calculations that need timestamp comparisons.
def get_all_tickets(db: Session) -> list[models.Ticket]:
    return list(db.scalars(select(models.Ticket)).all())


# Count every ticket in the database.
def count_tickets(db: Session) -> int:
    return db.scalar(select(func.count(models.Ticket.id))) or 0


# Count tickets whose status is in the supplied status group.
def count_tickets_with_statuses(db: Session, statuses: set[TicketStatus]) -> int:
    return (
        db.scalar(
            select(func.count(models.Ticket.id)).where(models.Ticket.status.in_(statuses))
        )
        or 0
    )


# Count tickets created during the current UTC day.
def count_tickets_created_today(db: Session) -> int:
    today_start = start_of_today_utc()
    tomorrow_start = today_start + timedelta(days=1)

    return (
        db.scalar(
            select(func.count(models.Ticket.id)).where(
                models.Ticket.created_at >= today_start,
                models.Ticket.created_at < tomorrow_start,
            )
        )
        or 0
    )


# Count tickets resolved during the current Monday-start UTC week.
def count_tickets_resolved_this_week(db: Session) -> int:
    week_start = start_of_week_utc()
    next_week_start = week_start + timedelta(days=7)

    return (
        db.scalar(
            select(func.count(models.Ticket.id)).where(
                models.Ticket.resolved_at.is_not(None),
                models.Ticket.resolved_at >= week_start,
                models.Ticket.resolved_at < next_week_start,
            )
        )
        or 0
    )


# Average only tickets that actually have a first response timestamp.
def average_response_time_minutes(tickets: list[models.Ticket]) -> float:
    response_times = [
        response_time
        for ticket in tickets
        if (response_time := sla.get_response_time_minutes(ticket)) is not None
    ]
    if not response_times:
        return 0.0

    return round(sum(response_times) / len(response_times), 2)


# Average only tickets that actually have a resolution timestamp.
def average_resolution_time_hours(tickets: list[models.Ticket]) -> float:
    resolution_times = [
        resolution_time
        for ticket in tickets
        if (resolution_time := sla.get_resolution_time_hours(ticket)) is not None
    ]
    if not resolution_times:
        return 0.0

    return round(sum(resolution_times) / len(resolution_times), 2)


def get_sla_counts(
    tickets: list[models.Ticket],
    current_time: datetime | None = None,
) -> Counter[str]:
    # Count met, breached, and pending SLA outcomes.
    counts: Counter[str] = Counter()
    now = current_time or sla.utc_now()

    for ticket in tickets:
        sla_status = sla.evaluate_first_response_sla(ticket, now)
        counts[sla_status.value] += 1

    return counts


# Build the high-level analytics summary response.
def get_summary(db: Session) -> schemas.AnalyticsSummary:
    tickets = get_all_tickets(db)
    sla_counts = get_sla_counts(tickets)

    met = sla_counts[sla.SLAStatus.MET.value]
    breached = sla_counts[sla.SLAStatus.BREACHED.value]

    return schemas.AnalyticsSummary(
        total_tickets=count_tickets(db),
        open_tickets=count_tickets_with_statuses(db, OPEN_STATUSES),
        completed_tickets=count_tickets_with_statuses(db, COMPLETED_STATUSES),
        tickets_created_today=count_tickets_created_today(db),
        tickets_resolved_this_week=count_tickets_resolved_this_week(db),
        average_response_time_minutes=average_response_time_minutes(tickets),
        average_resolution_time_hours=average_resolution_time_hours(tickets),
        sla_compliance_percentage=sla.calculate_compliance_percentage(met, breached),
    )


# Group ticket counts by an enum-backed model field.
def get_grouped_counts(db: Session, field, enum_class):
    rows = db.execute(
        select(field, func.count(models.Ticket.id)).group_by(field)
    ).all()
    count_by_value = {value: count for value, count in rows}

    return [
        {"value": enum_value, "count": count_by_value.get(enum_value, 0)}
        for enum_value in enum_class
    ]


# Count tickets by category.
def get_category_counts(db: Session) -> list[schemas.CategoryCount]:
    return [
        schemas.CategoryCount(category=row["value"], count=row["count"])
        for row in get_grouped_counts(db, models.Ticket.category, TicketCategory)
    ]


# Count tickets by status.
def get_status_counts(db: Session) -> list[schemas.StatusCount]:
    return [
        schemas.StatusCount(status=row["value"], count=row["count"])
        for row in get_grouped_counts(db, models.Ticket.status, TicketStatus)
    ]


# Count tickets by priority in severity order.
def get_priority_counts(db: Session) -> list[schemas.PriorityCount]:
    priority_order = [
        TicketPriority.CRITICAL,
        TicketPriority.HIGH,
        TicketPriority.MEDIUM,
        TicketPriority.LOW,
    ]
    rows = db.execute(
        select(models.Ticket.priority, func.count(models.Ticket.id)).group_by(
            models.Ticket.priority
        )
    ).all()
    count_by_priority = {priority: count for priority, count in rows}

    return [
        schemas.PriorityCount(
            priority=priority,
            count=count_by_priority.get(priority, 0),
        )
        for priority in priority_order
    ]


# Return daily created/resolved counts for a continuous date range.
def get_ticket_trends(db: Session, days: int = 30) -> list[schemas.TrendPoint]:
    today = sla.utc_now().date()
    start_date = today - timedelta(days=days - 1)
    start_datetime = datetime.combine(start_date, time.min, tzinfo=UTC)

    # Aggregate created tickets by calendar date.
    created_rows = db.execute(
        select(func.date(models.Ticket.created_at), func.count(models.Ticket.id))
        .where(models.Ticket.created_at >= start_datetime)
        .group_by(func.date(models.Ticket.created_at))
    ).all()

    # Aggregate resolved tickets by calendar date.
    resolved_rows = db.execute(
        select(func.date(models.Ticket.resolved_at), func.count(models.Ticket.id))
        .where(
            models.Ticket.resolved_at.is_not(None),
            models.Ticket.resolved_at >= start_datetime,
        )
        .group_by(func.date(models.Ticket.resolved_at))
    ).all()

    created_counts = {date.fromisoformat(day): count for day, count in created_rows}
    resolved_counts = {date.fromisoformat(day): count for day, count in resolved_rows}

    # Include zero-count days so dashboard charts can use a continuous timeline.
    return [
        schemas.TrendPoint(
            date=start_date + timedelta(days=offset),
            created=created_counts.get(start_date + timedelta(days=offset), 0),
            resolved=resolved_counts.get(start_date + timedelta(days=offset), 0),
        )
        for offset in range(days)
    ]


# Build the overall and per-priority SLA summary response.
def get_sla_summary(db: Session) -> schemas.SLASummary:
    tickets = get_all_tickets(db)
    overall_counts = get_sla_counts(tickets)
    by_priority = []

    for priority in [
        TicketPriority.CRITICAL,
        TicketPriority.HIGH,
        TicketPriority.MEDIUM,
        TicketPriority.LOW,
    ]:
        # Break out SLA outcomes for each priority level.
        priority_tickets = [ticket for ticket in tickets if ticket.priority == priority]
        priority_counts = get_sla_counts(priority_tickets)
        priority_met = priority_counts[sla.SLAStatus.MET.value]
        priority_breached = priority_counts[sla.SLAStatus.BREACHED.value]

        by_priority.append(
            schemas.SLAPrioritySummary(
                priority=priority,
                target_minutes=sla.get_sla_target_minutes(priority),
                met=priority_met,
                breached=priority_breached,
                pending=priority_counts[sla.SLAStatus.PENDING.value],
                compliance_percentage=sla.calculate_compliance_percentage(
                    priority_met,
                    priority_breached,
                ),
            )
        )

    met = overall_counts[sla.SLAStatus.MET.value]
    breached = overall_counts[sla.SLAStatus.BREACHED.value]

    return schemas.SLASummary(
        met=met,
        breached=breached,
        pending=overall_counts[sla.SLAStatus.PENDING.value],
        compliance_percentage=sla.calculate_compliance_percentage(met, breached),
        by_priority=by_priority,
    )
