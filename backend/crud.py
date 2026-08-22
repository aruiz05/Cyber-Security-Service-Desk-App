from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


# Create and persist a new ticket record.
def create_ticket(db: Session, ticket: schemas.TicketCreate) -> models.Ticket:
    # Convert the validated Pydantic schema into a SQLAlchemy model.
    db_ticket = models.Ticket(**ticket.model_dump())
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


# Retrieve every ticket currently stored in the database.
def get_tickets(db: Session) -> list[models.Ticket]:
    return list(db.scalars(select(models.Ticket)).all())


# Apply a partial update to an existing ticket.
def update_ticket(
    db: Session,
    db_ticket: models.Ticket,
    ticket_update: schemas.TicketUpdate,
) -> models.Ticket:
    # Only include fields the request actually sent.
    update_data = ticket_update.model_dump(exclude_unset=True)

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
