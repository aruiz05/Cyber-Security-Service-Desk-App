from sqlalchemy import case, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas, ticket_logic
from .enums import AssignedTeam, Department, TicketCategory, TicketPriority, TicketStatus


# Convert an allowed sort option into a SQLAlchemy expression.
def get_ticket_sort_expression(sort_by: schemas.TicketSortField):
    if sort_by == schemas.TicketSortField.PRIORITY:
        # Sort priority by business severity instead of alphabetically.
        return case(
            (models.Ticket.priority == TicketPriority.LOW, 1),
            (models.Ticket.priority == TicketPriority.MEDIUM, 2),
            (models.Ticket.priority == TicketPriority.HIGH, 3),
            (models.Ticket.priority == TicketPriority.CRITICAL, 4),
            else_=0,
        )

    # Only expose known sortable fields instead of accepting raw column names.
    sortable_fields = {
        schemas.TicketSortField.CREATED_AT: models.Ticket.created_at,
        schemas.TicketSortField.UPDATED_AT: models.Ticket.updated_at,
        schemas.TicketSortField.STATUS: models.Ticket.status,
        schemas.TicketSortField.CATEGORY: models.Ticket.category,
        schemas.TicketSortField.TICKET_NUMBER: models.Ticket.ticket_number,
    }
    return sortable_fields[sort_by]


# Build SQLAlchemy WHERE conditions from optional query parameters.
def build_ticket_filters(
    ticket_status: TicketStatus | None = None,
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    department: Department | None = None,
    assigned_team: AssignedTeam | None = None,
    search: str | None = None,
) -> list:
    filters = []

    # Add exact-match filters only when the client supplied them.
    if ticket_status is not None:
        filters.append(models.Ticket.status == ticket_status)
    if category is not None:
        filters.append(models.Ticket.category == category)
    if priority is not None:
        filters.append(models.Ticket.priority == priority)
    if department is not None:
        filters.append(models.Ticket.department == department)
    if assigned_team is not None:
        filters.append(models.Ticket.assigned_team == assigned_team)

    if search is not None and search.strip():
        # Search useful text fields with case-insensitive partial matching.
        search_pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                models.Ticket.ticket_number.ilike(search_pattern),
                models.Ticket.title.ilike(search_pattern),
                models.Ticket.description.ilike(search_pattern),
                models.Ticket.requester_name.ilike(search_pattern),
                models.Ticket.requester_email.ilike(search_pattern),
            )
        )

    return filters


# Create and persist a new ticket record.
def create_ticket(db: Session, ticket: schemas.TicketCreate) -> models.Ticket:
    # Convert the validated Pydantic schema into a SQLAlchemy model.
    ticket_data = ticket_logic.build_new_ticket_data(db, ticket.model_dump())
    db_ticket = models.Ticket(**ticket_data)
    db.add(db_ticket)

    try:
        # Commit the new ticket so it is saved in SQLite.
        db.commit()
    except IntegrityError:
        # Roll back failed writes so the session can be reused safely.
        db.rollback()
        raise

    # Refresh loads database-generated values such as id and timestamps.
    db.refresh(db_ticket)
    return db_ticket


# Retrieve a single ticket by its database id.
def get_ticket(db: Session, ticket_id: int) -> models.Ticket | None:
    return db.get(models.Ticket, ticket_id)


# Retrieve tickets with optional filters, search, sorting, and pagination.
def get_tickets(
    db: Session,
    ticket_status: TicketStatus | None = None,
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    department: Department | None = None,
    assigned_team: AssignedTeam | None = None,
    search: str | None = None,
    sort_by: schemas.TicketSortField = schemas.TicketSortField.CREATED_AT,
    sort_order: schemas.SortOrder = schemas.SortOrder.DESC,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[models.Ticket], int]:
    filters = build_ticket_filters(
        ticket_status=ticket_status,
        category=category,
        priority=priority,
        department=department,
        assigned_team=assigned_team,
        search=search,
    )

    # Count is calculated before limit/offset so pagination metadata is correct.
    total = db.scalar(select(func.count(models.Ticket.id)).where(*filters)) or 0
    sort_expression = get_ticket_sort_expression(sort_by)

    # Add a secondary id sort so records with matching values stay stable.
    if sort_order == schemas.SortOrder.DESC:
        order_by = sort_expression.desc()
        secondary_order_by = models.Ticket.id.desc()
    else:
        order_by = sort_expression.asc()
        secondary_order_by = models.Ticket.id.asc()

    query = (
        select(models.Ticket)
        # Filtering and search happen in the database.
        .where(*filters)
        .order_by(order_by, secondary_order_by)
        # Pagination also happens in the database with OFFSET and LIMIT.
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(db.scalars(query).all()), total


# Apply a partial update to an existing ticket.
def update_ticket(
    db: Session,
    db_ticket: models.Ticket,
    ticket_update: schemas.TicketUpdate,
) -> models.Ticket:
    # Only include fields the request actually sent.
    update_data = ticket_update.model_dump(exclude_unset=True)

    # Set system-controlled timestamps when ticket status changes.
    ticket_logic.apply_status_timestamps(db_ticket, update_data)

    # Update each supplied field on the SQLAlchemy model.
    for field, value in update_data.items():
        setattr(db_ticket, field, value)

    try:
        # Commit the changed ticket to SQLite.
        db.commit()
    except IntegrityError:
        # Roll back failed writes so the session is not left in a bad state.
        db.rollback()
        raise

    # Refresh returns the latest database state, including updated timestamps.
    db.refresh(db_ticket)
    return db_ticket


# Delete an existing ticket from the database.
def delete_ticket(db: Session, db_ticket: models.Ticket) -> None:
    db.delete(db_ticket)
    db.commit()
