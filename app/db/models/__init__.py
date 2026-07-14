"""
Central import for all models.

Importing this module ensures that all models are registered
in Base metadata before working with the database.
"""

from .history import TicketHistory
from .ticket import Ticket, TicketPriority, TicketStatus

# Export for convenience
__all__ = [
    "Ticket",
    "TicketPriority",
    "TicketStatus",
    "TicketHistory"
]