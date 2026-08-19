from datetime import UTC, datetime
from enum import Enum as PythonEnum

from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from .enums import AssignedTeam, Department, TicketCategory, TicketPriority, TicketStatus


def utc_now() -> datetime:
    return datetime.now(UTC)


def enum_values(enum_class: type[PythonEnum]) -> list[str]:
    return [item.value for item in enum_class]


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requester_name: Mapped[str] = mapped_column(String(100), nullable=False)
    requester_email: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[Department] = mapped_column(
        SQLAlchemyEnum(Department, values_callable=enum_values),
        nullable=False,
    )
    category: Mapped[TicketCategory] = mapped_column(
        SQLAlchemyEnum(TicketCategory, values_callable=enum_values),
        nullable=False,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        SQLAlchemyEnum(TicketPriority, values_callable=enum_values),
        default=TicketPriority.MEDIUM,
        nullable=False,
    )
    status: Mapped[TicketStatus] = mapped_column(
        SQLAlchemyEnum(TicketStatus, values_callable=enum_values),
        default=TicketStatus.NEW,
        nullable=False,
    )
    assigned_team: Mapped[AssignedTeam] = mapped_column(
        SQLAlchemyEnum(AssignedTeam, values_callable=enum_values),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    first_response_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
