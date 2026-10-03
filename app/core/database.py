"""
Database Layer — JSON FILE persistence (demo mode, no database server, free)
File: app/core/database.py

How it works
------------
* All your endpoints keep using SQLAlchemy (Session, models, filters...) unchanged.
* The live working copy is a throw-away SQLite file in the OS temp folder,
  rebuilt from the JSON file every time the app starts.
* After EVERY successful commit the whole database is written to a JSON file
  (default: json_db/db.json).  That JSON file is the real storage.

Settings (environment variables, all optional)
----------------------------------------------
JSON_DB_PATH    where the JSON file lives            (default: json_db/db.json)
ADMIN_EMAIL     admin created if there are no users  (default: admin@legaltech.com)
ADMIN_PASSWORD  its password                         (default: admin123)

Note: run with ONE worker (uvicorn default).  Several workers would each hold
their own copy and overwrite each other's JSON file.
"""

import atexit
import json
import logging
import os
import tempfile
import threading
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
JSON_DB_PATH = Path(os.getenv("JSON_DB_PATH", "json_db/db.json"))
_RUNTIME_DB = Path(tempfile.gettempdir()) / f"legaltech_runtime_{os.getpid()}.db"

if _RUNTIME_DB.exists():
    _RUNTIME_DB.unlink()

# ─── Engine (temporary working copy) ──────────────────────────────────────────
engine = create_engine(
    f"sqlite:///{_RUNTIME_DB.as_posix()}",
    connect_args={"check_same_thread": False, "timeout": 30},
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# ─── Base class ───────────────────────────────────────────────────────────────
# ALL models must inherit from Base so SQLAlchemy knows about them
Base = declarative_base()

_lock = threading.RLock()
_initialized = False


def _cleanup():
    try:
        engine.dispose()
        _RUNTIME_DB.unlink(missing_ok=True)
    except Exception:
        pass


atexit.register(_cleanup)


# ─── Save: database → JSON ────────────────────────────────────────────────────
def save_to_json() -> None:
    """Write every table to the JSON file (atomic: temp file, then replace)."""
    with _lock:
        data = {}
        with engine.connect() as conn:
            for table in Base.metadata.sorted_tables:
                rows = conn.exec_driver_sql(f'SELECT * FROM "{table.name}"').fetchall()
                data[table.name] = [dict(r._mapping) for r in rows]

        JSON_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = JSON_DB_PATH.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=1, default=str),
            encoding="utf-8",
        )
        os.replace(tmp, JSON_DB_PATH)


@event.listens_for(Session, "after_commit")
def _persist_after_commit(session):
    if not _initialized:
        return
    try:
        save_to_json()
    except Exception as e:  # never break a request because of the backup
        logger.error("❌ Could not write JSON database: %s", e)


# ─── Load: JSON → database ────────────────────────────────────────────────────
def _load_from_json() -> None:
    if not JSON_DB_PATH.exists():
        logger.info("ℹ️  No JSON database yet (%s) — starting empty", JSON_DB_PATH)
        return

    data = json.loads(JSON_DB_PATH.read_text(encoding="utf-8"))
    total = 0
    with engine.begin() as conn:
        for name, rows in data.items():
            table = Base.metadata.tables.get(name)
            if table is None or not rows:
                continue
            cols = [c.name for c in table.columns if c.name in rows[0]]
            col_sql = ", ".join(f'"{c}"' for c in cols)
            ph_sql = ", ".join(["?"] * len(cols))
            conn.exec_driver_sql(
                f'INSERT OR REPLACE INTO "{name}" ({col_sql}) VALUES ({ph_sql})',
                [tuple(r.get(c) for c in cols) for r in rows],
            )
            total += len(rows)
    logger.info("✅ Loaded %d rows from %s", total, JSON_DB_PATH)


def _ensure_admin() -> None:
    """If there are no users at all, create the admin so you can always log in."""
    try:
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash
    except Exception as e:
        logger.warning("Could not import User model for admin seeding: %s", e)
        return

    db = Session(bind=engine)
    try:
        if db.query(User).count() == 0:
            email = os.getenv("ADMIN_EMAIL", "admin@legaltech.com")
            db.add(User(
                email=email,
                full_name="System Administrator",
                full_name_ar="مدير النظام",
                hashed_password=get_password_hash(os.getenv("ADMIN_PASSWORD", "admin123")),
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True,
                created_at=datetime.utcnow(),
            ))
            db.commit()
            logger.warning("👤 Admin created: %s (change the password!)", email)
    except Exception as e:
        db.rollback()
        logger.error("Admin seeding failed: %s", e)
    finally:
        db.close()


def init_json_db() -> None:
    """Create tables, load the JSON file, seed admin. Safe to call many times."""
    global _initialized
    if _initialized:
        return
    with _lock:
        if _initialized:
            return
        try:
            import app.models  # noqa: F401  (registers every model on Base)
        except Exception as e:
            logger.warning("Could not import app.models: %s", e)

        Base.metadata.create_all(bind=engine)
        _load_from_json()
        _initialized = True
        _ensure_admin()


# ─── Session Factory ──────────────────────────────────────────────────────────
class _InitSession(Session):
    """Makes sure the JSON data is loaded before the first session is used."""

    def __init__(self, *args, **kwargs):
        init_json_db()
        super().__init__(*args, **kwargs)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=_InitSession,
)


# ─── Dependency ───────────────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that provides a database session.
    Use with: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
