"""
Initialize database - Create all tables
Run this script to set up the database schema
"""

from app.core.database import engine, Base
from app.models import (
    User, Reminder, ReminderComment,
    Ticket, TicketMessage,
    Notification, Client, Case, Hearing, Document
)

def init_db():
    print("🗄️  Initializing database...")
    print("=" * 50)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database initialized successfully!")
        print("\n📊 Tables created:")
        print("   - users")
        print("   - reminders")
        print("   - reminder_comments")
        print("   - tickets")
        print("   - ticket_messages")
        print("   - notifications")
        print("   - clients")
        print("   - cases")
        print("   - hearings")
        print("   - documents")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    
    print("=" * 50)


if __name__ == "__main__":
    init_db()
