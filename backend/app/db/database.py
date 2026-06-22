from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Connection string for local Postgres from docker-compose
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://docusense:docusense@localhost:5434/docusense"
)

# Engine manages DB connections
engine = create_engine(DATABASE_URL)

# Session factory for DB sessions (one per request)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Provides a database session to API endpoints.
    Closes the session after request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()