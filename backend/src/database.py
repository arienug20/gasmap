"""Database setup and initialization."""

import sqlite3
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.config import get_settings

settings = get_settings()

# Ensure data directory exists
data_dir = Path(settings.database_path).parent
data_dir.mkdir(parents=True, exist_ok=True)

# Create engine with SQLite
engine = create_engine(
    f"sqlite:///{settings.database_path}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Enable foreign keys
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with tables and seed data."""
    from src.models.chemical import Base

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Seed chemicals if empty
    from src.services.chemical_service import ChemicalService

    db = SessionLocal()
    try:
        service = ChemicalService(db)
        if service.get_count() == 0:
            print("Seeding chemical database...")
            service.seed_from_json("src/data/seed_chemicals.json")
            print(f"Seeded {service.get_count()} chemicals")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")