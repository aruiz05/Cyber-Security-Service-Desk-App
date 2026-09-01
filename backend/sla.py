from datetime import UTC, datetime, timedelta
from enum import Enum

from . import models
from .enums import TicketPriority


# Possible first-response SLA states for a ticket.
class SLAStatus(str, Enum):
    MET = "Met"
    BREACHED = "Breached"
    PENDING = "Pending"


# First-response SLA targets by priority, stored in minutes.
FIRST_RESPONSE_SLA_MINUTES: dict[TicketPriority, int] = {
    TicketPriority.CRITICAL: 60,
    TicketPriority.HIGH: 240,
    TicketPriority.MEDIUM: 480,
    TicketPriority.LOW: 1440,
}


# Return the current UTC time for SLA calculations.
def utc_now() -> datetime:
    return datetime.now(UTC)


# Normalize timestamps to timezone-aware UTC values.
def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


# Look up the first-response SLA target for a ticket priority.
def get_sla_target_minutes(priority: TicketPriority | str) -> int:
    return FIRST_RESPONSE_SLA_MINUTES[TicketPriority(priority)]


# Calculate how long it took to respond to a ticket.
def get_response_time_minutes(ticket: models.Ticket) -> float | None:
    if ticket.first_response_at is None:
        return None

    response_time = ensure_utc(ticket.first_response_at) - ensure_utc(ticket.created_at)
    return response_time.total_seconds() / 60


# Calculate how long it took to resolve a ticket.
def get_resolution_time_hours(ticket: models.Ticket) -> float | None:
    if ticket.resolved_at is None:
        return None

    resolution_time = ensure_utc(ticket.resolved_at) - ensure_utc(ticket.created_at)
    return resolution_time.total_seconds() / 3600


def evaluate_first_response_sla(
    ticket: models.Ticket,
    current_time: datetime | None = None,
) -> SLAStatus:
    # SLA is based on first response time, not total resolution time.
    target_minutes = get_sla_target_minutes(ticket.priority)

    if ticket.first_response_at is not None:
        # Responded tickets can be evaluated as met or breached.
        response_time_minutes = get_response_time_minutes(ticket)
        if response_time_minutes is not None and response_time_minutes <= target_minutes:
            return SLAStatus.MET

        return SLAStatus.BREACHED

    # Unresponded tickets are pending until their deadline passes.
    now = ensure_utc(current_time or utc_now())
    deadline = ensure_utc(ticket.created_at) + timedelta(minutes=target_minutes)

    if now > deadline:
        return SLAStatus.BREACHED

    return SLAStatus.PENDING


# Calculate SLA compliance while excluding pending tickets.
def calculate_compliance_percentage(met: int, breached: int) -> float:
    evaluable = met + breached
    if evaluable == 0:
        return 0.0

    return round((met / evaluable) * 100, 2)
