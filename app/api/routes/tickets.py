from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.session import get_db_session
from app.crud import ticket as ticket_crud
from app.api.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse
)


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket_endpoint(
    ticket_in: TicketCreate,
    db: AsyncSession = Depends(get_db_session)
) -> TicketResponse:
    """
    Creates a new ticket.

    - **thread_id**: user session identifier
    - **user_input**: ticket text (1-10000 characters)
    - **priority**: low, medium, high or critical (default medium)
    """
    db_ticket = await ticket_crud.create_ticket(db, ticket_in)

    # Convert ORM object to Pydantic schema for response
    return TicketResponse.model_validate(db_ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket_endpoint(
    ticket_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> TicketResponse:
    """Gets a ticket by id."""
    db_ticket = await ticket_crud.get_ticket_by_id(db, ticket_id)

    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id={ticket_id} not found"
        )

    return TicketResponse.model_validate(db_ticket)


@router.get("/", response_model=TicketListResponse)
async def list_tickets_endpoint(
    thread_id: str = Query(..., min_length=1, description="Session identifier for filtering"),
    skip: int = Query(0, ge=0, description="Skip first N records"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db_session)
) -> TicketListResponse:
    """
    Gets a list of tickets for a session with pagination.

    - **thread_id**: required filtering parameter
    - **skip**: pagination offset (default 0)
    - **limit**: records per page (1-1000, default 100)
    """
    tickets, total = await ticket_crud.get_tickets_by_thread(db, thread_id, skip, limit)

    return TicketListResponse(
        items=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket_endpoint(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: AsyncSession = Depends(get_db_session)
) -> TicketResponse:
    """Partially updates a ticket by id."""
    db_ticket = await ticket_crud.update_ticket(db, ticket_id, ticket_update)

    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id={ticket_id} not found"
        )

    return TicketResponse.model_validate(db_ticket)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket_endpoint(
    ticket_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> None:
    """Deletes a ticket by id. Returns 204 with no response body."""
    success = await ticket_crud.delete_ticket(db, ticket_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id={ticket_id} not found"
        )

    return None