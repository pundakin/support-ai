from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete

from app.api.schemas.ticket import TicketCreate, TicketUpdate
from app.db.models import Ticket, TicketHistory, TicketPriority, TicketStatus


async def create_ticket(session: AsyncSession, ticket_in: TicketCreate) -> Ticket:
    """
    Creates a new ticket in the database.

    Args:
        session: Async SQLAlchemy session
        ticket_in: Validated data from TicketCreate schema

    Returns:
        Created Ticket object with assigned id
    """
    # Convert string values to enum if provided
    priority_enum = TicketPriority(ticket_in.priority) if ticket_in.priority else TicketPriority.MEDIUM

    db_ticket = Ticket(
        thread_id=ticket_in.thread_id,
        user_input=ticket_in.user_input,
        category=ticket_in.category,
        priority=priority_enum,
        tags=ticket_in.tags,
        status=TicketStatus.NEW
    )

    session.add(db_ticket)
    await session.flush()  # Get id without commit
    await session.refresh(db_ticket)  # Load default values (created_at, etc.)

    return db_ticket


async def get_ticket_by_id(session: AsyncSession, ticket_id: int) -> Ticket | None:
    """
    Gets a ticket by id.

    Returns:
        Ticket object or None if not found
    """
    result = await session.scalar(
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.history))
    )
    return result


async def get_tickets_by_thread(
    session: AsyncSession,
    thread_id: str,
    skip: int = 0,
    limit: int = 100
) -> tuple[list[Ticket], int]:
    """
    Gets a list of tickets for a session with pagination.

    Returns:
        Tuple (list of tickets, total number of tickets for the session)
    """
    # Query to get the total count (for pagination)
    count_stmt = select(func.count()).select_from(Ticket).where(Ticket.thread_id == thread_id)
    total = await session.scalar(count_stmt)

    # Query to get data with pagination
    stmt = (
        select(Ticket)
        .where(Ticket.thread_id == thread_id)
        .order_by(Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await session.scalars(stmt)
    tickets = result.all()

    return tickets, total


async def update_ticket(
    session: AsyncSession,
    ticket_id: int,
    ticket_update: TicketUpdate
) -> Ticket | None:
    """
    Partially updates a ticket.

    Only provided fields (non-None values) are updated.

    Returns:
        Updated Ticket object or None if not found
    """
    # Collect only provided fields
    update_data = ticket_update.model_dump(exclude_unset=True, exclude_none=True)

    if not update_data:
        # Nothing to update — return current value
        return await get_ticket_by_id(session, ticket_id)

    # Convert strings to enum if needed
    if "priority" in update_data:
        update_data["priority"] = TicketPriority(update_data["priority"])
    if "status" in update_data:
        update_data["status"] = TicketStatus(update_data["status"])

    # Execute UPDATE query
    stmt = (
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(**update_data)
        .returning(Ticket)
    )

    result = await session.scalar(stmt)
    await session.commit()

    # If needed — load related data
    if result:
        await session.refresh(result, attribute_names=["history"])

    return result


async def delete_ticket(session: AsyncSession, ticket_id: int) -> bool:
    """
    Deletes a ticket by id.

    Returns:
        True if deleted, False if not found
    """
    stmt = delete(Ticket).where(Ticket.id == ticket_id)
    result = await session.execute(stmt)

    await session.commit()

    return result.rowcount > 0


async def add_ticket_history(
    session: AsyncSession,
    ticket_id: int,
    event_type: str,
    old_value: str | None = None,
    new_value: str | None = None
) -> TicketHistory:
    """
    Adds a record to the ticket change history.

    Returns:
        Created TicketHistory object
    """
    history = TicketHistory(
        ticket_id=ticket_id,
        event_type=event_type,
        old_value=old_value,
        new_value=new_value
    )

    session.add(history)
    await session.flush()

    return history