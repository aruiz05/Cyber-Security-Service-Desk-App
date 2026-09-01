from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .enums import AssignedTeam, Department, TicketCategory, TicketPriority, TicketStatus


# Allowed fields clients can use when sorting the ticket queue.
class TicketSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PRIORITY = "priority"
    STATUS = "status"
    CATEGORY = "category"
    TICKET_NUMBER = "ticket_number"


# Allowed sort directions for the ticket queue.
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TicketBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    requester_name: str = Field(..., max_length=100)
    requester_email: EmailStr
    department: Department
    category: TicketCategory


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    department: Department | None = None
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    assigned_team: AssignedTeam | None = None
    resolution_notes: str | None = None


class TicketResponse(TicketBase):
    id: int
    ticket_number: str
    priority: TicketPriority
    status: TicketStatus
    assigned_team: AssignedTeam
    created_at: datetime
    updated_at: datetime
    first_response_at: datetime | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Response shape for the paginated GET /tickets endpoint.
class TicketListResponse(BaseModel):
    # Current page of full ticket objects.
    items: list[TicketResponse]
    # Total tickets matching the active filters/search.
    total: int
    # Current page number returned to the client.
    page: int
    # Maximum number of tickets requested per page.
    page_size: int
    # Number of available pages for the current result set.
    total_pages: int
