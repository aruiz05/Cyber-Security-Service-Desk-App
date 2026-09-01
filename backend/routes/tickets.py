from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..enums import AssignedTeam, Department, TicketCategory, TicketPriority, TicketStatus


# Router groups all ticket endpoints under /tickets in Swagge
router = APIRouter(prefix="/tickets", tags=["Tickets"])


# Detect SQLite unique-constraint errors caused by duplicate ticket numbers.
def is_duplicate_ticket_number_error(error: IntegrityError) -> bool:
    message = str(error.orig).lower()
    return "unique" in message and "ticket_number" in message


# Create a ticket and return the saved database record
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
        # Duplicate ticket numbers should return a clear client error
        if is_duplicate_ticket_number_error(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket number already exists",
            ) from exc

        # Other integrity errors are still client-facing, but less specific
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error",
        ) from exc


# Return a filtered, searchable, sortable, paginated ticket queue.
@router.get("", response_model=schemas.TicketListResponse)
def get_tickets(
    # Alias keeps the public query parameter named "status".
    ticket_status: TicketStatus | None = Query(default=None, alias="status"),
    # Enum-typed filters give Swagger valid values and FastAPI validation.
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    department: Department | None = None,
    assigned_team: AssignedTeam | None = None,
    # Optional text search across ticket number, title, description, and requester.
    search: str | None = None,
    # Defaults show newest tickets first.
    sort_by: schemas.TicketSortField = schemas.TicketSortField.CREATED_AT,
    sort_order: schemas.SortOrder = schemas.SortOrder.DESC,
    # Pagination bounds prevent invalid or oversized requests.
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> schemas.TicketListResponse:
    # CRUD layer handles database query construction.
    items, total = crud.get_tickets(
        db=db,
        ticket_status=ticket_status,
        category=category,
        priority=priority,
        department=department,
        assigned_team=assigned_team,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    # Calculate total pages from the filtered result count.
    total_pages = (total + page_size - 1) // page_size if total else 0

    # Return tickets plus pagination metadata.
    return schemas.TicketListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# Return one ticket by id, or 404 if it does not exist
@router.get("/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> models.Ticket:
    db_ticket = crud.get_ticket(db, ticket_id)
    if db_ticket is None:
        # FastAPI converts this into 404 response
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return db_ticket


# Partially update existing ticket using only provided fields
@router.patch("/{ticket_id}", response_model=schemas.TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    db: Session = Depends(get_db),
) -> models.Ticket:
    db_ticket = crud.get_ticket(db, ticket_id)
    if db_ticket is None:
        # Missing tickets cannot be updated
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    try:
        return crud.update_ticket(db, db_ticket, ticket_update)
    except IntegrityError as exc:
        # Keep database  failures from becoming generic 500 errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error",
        ) from exc


# Delete a ticket by id and return 204 when successful
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Response:
    db_ticket = crud.get_ticket(db, ticket_id)
    if db_ticket is None:
        # Missing tickets cannot be deleted
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    crud.delete_ticket(db, db_ticket)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
