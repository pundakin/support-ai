from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# === Schemas for creating a ticket ===

class TicketCreate(BaseModel):
    """
    Schema for creating a new ticket.
    
    Used for input validation in the POST /tickets endpoint.
    """
    thread_id: str = Field(..., min_length=1, max_length=64, description="Session identifier")
    user_input: str = Field(..., min_length=1, max_length=10000, description="Ticket text")
    category: str | None = Field(default=None, max_length=64, description="Ticket category")
    priority: str | None = Field(default="medium", pattern="^(low|medium|high|critical)$", description="Priority")
    tags: list[str] | None = Field(default=None, description="Ticket tags")


# === Schemas for updating a ticket ===

class TicketUpdate(BaseModel):
    """
    Schema for partial ticket update.
    
    All fields are optional — only provided fields are updated.
    """
    category: str | None = Field(default=None, max_length=64)
    priority: str | None = Field(default=None, pattern="^(low|medium|high|critical)$")
    tags: list[str] | None = Field(default=None)
    status: str | None = Field(default=None, pattern="^(new|in_progress|resolved|closed)$")


# === Schemas for response ===

class TicketBase(BaseModel):
    """Base schema with common ticket fields."""
    thread_id: str
    user_input: str
    category: str | None = None
    priority: str
    tags: list[str] | None = None
    status: str


class TicketResponse(TicketBase):
    """
    Complete response schema with metadata.
    
    Used for serializing responses in GET endpoints.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class TicketListResponse(BaseModel):
    """Schema for a list of tickets with pagination."""
    model_config = ConfigDict(from_attributes=True)
    
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int