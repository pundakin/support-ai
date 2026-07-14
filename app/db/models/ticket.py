import enum
from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, DateTime, Enum, func

from app.db.base import Base

class TicketPriority(str, enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class TicketStatus(str, enum.Enum):
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'


class Ticket(Base):
    """
    Ticket model for support requests.

    Table: tickets
    """
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    thread_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_input: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority, name='ticket_priority'),
        default=TicketPriority.MEDIUM
    )
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name='ticket_status'),
        default=TicketStatus.NEW
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updates_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    history: Mapped[list["TicketHistory"]] = relationship(
        "TicketHistory",
        back_populates='ticket',
        cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f""