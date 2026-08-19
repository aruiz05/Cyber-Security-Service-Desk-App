# Generator is used for the FastAPI database dependency return type.
from collections.abc import Generator

# SQLAlchemy creates the database engine and manages database sessions.
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# Local SQLite database file used by the backend.
SQLALCHEMY_DATABASE_URL = "sqlite:///./cybersecurity_service_desk.db"

# Create the SQLAlchemy engine that connects to SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Required for SQLite when FastAPI handles requests across threads.
    connect_args={"check_same_thread": False},
)

# Factory for creating database session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class future SQLAlchemy models will inherit from.
class Base(DeclarativeBase):
    pass


# FastAPI dependency that gives each request a database session.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        # Provide the active session to the endpoint using this dependency.
        yield db
    finally:
        # Always close the session after the request finishes.
        db.close()
