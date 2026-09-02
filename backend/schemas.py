from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .enums import (
    AssignedTeam,
    Department,
    KnowledgeCategory,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


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


# Response model for GET /analytics/summary.
class AnalyticsSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    completed_tickets: int
    tickets_created_today: int
    tickets_resolved_this_week: int
    average_response_time_minutes: float
    average_resolution_time_hours: float
    sla_compliance_percentage: float


# Count of tickets for one category.
class CategoryCount(BaseModel):
    category: TicketCategory
    count: int


# Count of tickets for one status.
class StatusCount(BaseModel):
    status: TicketStatus
    count: int


# Count of tickets for one priority.
class PriorityCount(BaseModel):
    priority: TicketPriority
    count: int


# One day of created/resolved ticket trend data.
class TrendPoint(BaseModel):
    date: date
    created: int
    resolved: int


# SLA metrics for one priority level.
class SLAPrioritySummary(BaseModel):
    priority: TicketPriority
    target_minutes: int
    met: int
    breached: int
    pending: int
    compliance_percentage: float


# Overall SLA metrics plus per-priority breakdown.
class SLASummary(BaseModel):
    met: int
    breached: int
    pending: int
    compliance_percentage: float
    by_priority: list[SLAPrioritySummary]


class KnowledgeArticleBase(BaseModel):
    title: str = Field(..., max_length=200)
    summary: str = Field(..., max_length=500)
    content: str
    category: KnowledgeCategory


class KnowledgeArticleCreate(KnowledgeArticleBase):
    pass


class KnowledgeArticleUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str | None = None
    category: KnowledgeCategory | None = None


class KnowledgeArticleResponse(KnowledgeArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
