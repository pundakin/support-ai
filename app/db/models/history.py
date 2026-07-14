from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func

from app.db.base import Base


class TicketHistory(Base):
    """
    Model for ticket change history.

    Table: ticket_history
    Used for auditing and debugging agent activity.
    """
    __tablename__ = "ticket_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Relationship to ticket
    ticket_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Event type: what changed
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)

    # Event data: values before and after
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Back-reference to ticket
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="history")

    def __repr__(self) -> str:
        return f""