"""
Database Configuration — SQLite via SQLAlchemy.

Uses a local SQLite file for zero-dependency persistence.
DATABASE_URL can be overridden via environment variable.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/capital_engine.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, auto-closes on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    import app.db.db_models  # noqa: F401 — ensure models are registered
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
