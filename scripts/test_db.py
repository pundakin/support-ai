"""
Script to test database connection and basic operations.
Run: python scripts/test_db.py
"""
import asyncio
import sys
from pathlib import Path

# Adding the project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import *
from app.db.session import get_session_factory


async def test_connection():
    """Check connection and basic insert/read."""
    try:
        factory = get_session_factory()

        async with factory() as session:
            # Simple query to check connection
            result = await session.scalar(text("SELECT 1"))
            print("✅ Database connection: successful")

            # Test insert (do not commit to avoid polluting the DB)
            test_ticket = Ticket(
                thread_id="test_session_123",
                user_input="Test ticket",
                category="technical",
                priority=TicketPriority.LOW,
                status=TicketStatus.NEW
            )
            session.add(test_ticket)
            await session.flush()  # Get id, but do not commit
            print(f"✅ Ticket object created: id={test_ticket.id}")

            # Test read
            ticket = await session.scalar(
                select(Ticket).where(Ticket.id == test_ticket.id)
            )
            if ticket:
                print(f"✅ Ticket object read: {ticket}")
            else:
                print("⚠️  Could not read the created object")

            # Rollback test changes
            await session.rollback()
            print("✅ Test changes rolled back")

        return True

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def main():
    print("🔍 Testing database connection...\n")

    success = await test_connection()

    print()
    if success:
        print("🎉 Database is ready for use!")
        return 0
    else:
        print("⚠️  Check DATABASE_URL and database availability")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))