from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db


# Router groups all ticket endpoints under /tickets in Swagger.
router = APIRouter(prefix="/tickets", tags=["Tickets"])


# Detect SQLite unique-constraint errors caused by duplicate ticket numbers.
def is_duplicate_ticket_number_error(error: IntegrityError) -> bool:
    message = str(error.orig).lower()
    return "unique" in message and "ticket_number" in message


# Create a ticket and return the saved database record.
@router.post(
    "",
    response_model=schemas.TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
) -> models.Ticket:
    try:
        return crud.create_ticket(db, ticket)
    except IntegrityError as exc:
        # Duplicate ticket numbers should return a clear client error.
        if is_duplicate_ticket_number_error(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket number already exists",
            ) from exc

        # Other integrity errors are still client-facing, but less specific.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error",
        ) from exc


# Return all tickets in the database.
@router.get("", response_model=list[schemas.TicketResponse])
def get_tickets(db: Session = Depends(get_db)) -> list[models.Ticket]:
    return crud.get_tickets(db)


# Return one ticket by id, or 404 if it does not exist.
@router.get("/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> models.Ticket:
    db_ticket = crud.get_ticket(db, ticket_id)
    if db_ticket is None:
        # FastAPI converts this into a JSON 404 response.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return db_ticket


# Partially update an existing ticket using only provided fields.
@router.patch("/{ticket_id}", response_model=schemas.TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    db: Session = Depends(get_db),
) -> models.Ticket:
    db_ticket = crud.get_ticket(db, ticket_id)
    if db_ticket is None:
        # Missing tickets cannot be updated.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    try:
        return crud.update_ticket(db, db_ticket, ticket_update)
    except IntegrityError as exc:
        # Keep database integrity failures from becoming generic 500 errors.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error",
        ) from exc


# Delete a ticket by id and return 204 when successful.
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Response:
    db_ticket = crud.get_ticket(db, ticket_id)
    if db_ticket is None:
        # Missing tickets cannot be deleted.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    crud.delete_ticket(db, db_ticket)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
