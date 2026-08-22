from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .enums import AssignedTeam, TicketCategory, TicketPriority, TicketStatus


CATEGORY_TEAM_ROUTING: dict[TicketCategory, AssignedTeam] = {
    TicketCategory.PHISHING: AssignedTeam.HUMAN_RISK_MANAGEMENT,
    TicketCategory.SOCIAL_ENGINEERING: AssignedTeam.HUMAN_RISK_MANAGEMENT,
    TicketCategory.PASSWORD_SECURITY: AssignedTeam.IDENTITY_AND_ACCESS_MANAGEMENT,
    TicketCategory.DATA_LOSS_PREVENTION: AssignedTeam.DATA_PROTECTION,
    TicketCategory.VULNERABILITY: AssignedTeam.VULNERABILITY_MANAGEMENT,
    TicketCategory.SECURITY_TRAINING: AssignedTeam.BUSINESS_AWARENESS,
    TicketCategory.SECURITY_AWARENESS: AssignedTeam.BUSINESS_AWARENESS,
    TicketCategory.ACCOUNT_SECURITY: AssignedTeam.IDENTITY_AND_ACCESS_MANAGEMENT,
    TicketCategory.OTHER: AssignedTeam.SECURITY_OPERATIONS,
}

CATEGORY_PRIORITY_DEFAULTS: dict[TicketCategory, TicketPriority] = {
    TicketCategory.PHISHING: TicketPriority.HIGH,
    TicketCategory.SOCIAL_ENGINEERING: TicketPriority.HIGH,
    TicketCategory.PASSWORD_SECURITY: TicketPriority.MEDIUM,
    TicketCategory.DATA_LOSS_PREVENTION: TicketPriority.CRITICAL,
    TicketCategory.VULNERABILITY: TicketPriority.HIGH,
    TicketCategory.SECURITY_TRAINING: TicketPriority.LOW,
    TicketCategory.SECURITY_AWARENESS: TicketPriority.LOW,
    TicketCategory.ACCOUNT_SECURITY: TicketPriority.HIGH,
    TicketCategory.OTHER: TicketPriority.MEDIUM,
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def get_assigned_team(category: TicketCategory) -> AssignedTeam:
    return CATEGORY_TEAM_ROUTING[category]


def get_default_priority(category: TicketCategory) -> TicketPriority:
    return CATEGORY_PRIORITY_DEFAULTS[category]


def get_highest_existing_ticket_number(db: Session) -> int:
    ticket_numbers = db.scalars(
        select(models.Ticket.ticket_number).where(
            models.Ticket.ticket_number.like("SEC-%")
        )
    ).all()

    highest_number = 0
    for ticket_number in ticket_numbers:
        number_part = ticket_number.removeprefix("SEC-")
        if number_part.isdigit():
            highest_number = max(highest_number, int(number_part))

    return highest_number


def get_ticket_counter(db: Session) -> models.TicketCounter:
    counter = db.get(models.TicketCounter, 1)
    if counter is None:
        counter = models.TicketCounter(
            id=1,
            next_number=get_highest_existing_ticket_number(db) + 1,
        )
        db.add(counter)
        db.flush()

    return counter


def generate_ticket_number(db: Session) -> str:
    counter = get_ticket_counter(db)
    highest_existing_number = get_highest_existing_ticket_number(db)

    if counter.next_number <= highest_existing_number:
        counter.next_number = highest_existing_number + 1

    ticket_number = f"SEC-{counter.next_number:06d}"
    counter.next_number += 1

    return ticket_number


def build_new_ticket_data(db: Session, ticket_data: dict) -> dict:
    category = ticket_data["category"]

    return {
        **ticket_data,
        "ticket_number": generate_ticket_number(db),
        "priority": get_default_priority(category),
        "status": TicketStatus.NEW,
        "assigned_team": get_assigned_team(category),
    }


def status_value(status: TicketStatus | str) -> str:
    if isinstance(status, TicketStatus):
        return status.value

    return status


def apply_status_timestamps(
    db_ticket: models.Ticket,
    update_data: dict,
) -> None:
    new_status = update_data.get("status")
    if new_status is None:
        return

    current_status = status_value(db_ticket.status)
    next_status = status_value(new_status)

    if (
        current_status == TicketStatus.NEW.value
        and next_status == TicketStatus.IN_PROGRESS.value
        and db_ticket.first_response_at is None
    ):
        db_ticket.first_response_at = utc_now()

    if (
        next_status == TicketStatus.RESOLVED.value
        and db_ticket.resolved_at is None
    ):
        db_ticket.resolved_at = utc_now()
