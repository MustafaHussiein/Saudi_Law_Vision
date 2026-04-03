"""
Database Configuration
File: app/core/database.py

CONNECTION STRING IS HERE → DATABASE_URL in config.py (or .env file)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# ─── Engine ───────────────────────────────────────────────────────────────────
# SQLite (default - no setup needed, creates a file)
# DATABASE_URL = "sqlite:///./legal_tech.db"
#
# PostgreSQL (production recommended)
# DATABASE_URL = "postgresql://user:password@localhost:5432/legal_tech"
#
# MySQL
# DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/legal_tech"

engine = create_engine(
    settings.DATABASE_URL,
    # SQLite-specific: allow multiple threads
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    # Connection pool settings (for PostgreSQL/MySQL)
    pool_pre_ping=True,      # Test connections before using them
    echo=settings.DEBUG,     # Log all SQL queries when DEBUG=True
)

# ─── Session Factory ──────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ─── Base Class ───────────────────────────────────────────────────────────────
# ALL models must inherit from Base so SQLAlchemy knows about them
Base = declarative_base()


# ─── Dependency ───────────────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that provides a database session.
    Use with: db: Session = Depends(get_db)

    Automatically closes session after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
