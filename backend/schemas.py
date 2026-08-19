from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .enums import AssignedTeam, Department, TicketCategory, TicketPriority, TicketStatus


class TicketBase(BaseModel):
    ticket_number: str = Field(..., max_length=20)
    title: str = Field(..., max_length=200)
    description: str
    requester_name: str = Field(..., max_length=100)
    requester_email: EmailStr
    department: Department
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    assigned_team: AssignedTeam


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
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    first_response_at: datetime | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)
