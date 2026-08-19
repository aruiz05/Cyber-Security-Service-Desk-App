
from collections.abc import Generator

# SQLAlchemy creates the database engine and manages database sessions
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# local SQLite database file 
SQLALCHEMY_DATABASE_URL = "sqlite:///./cybersecurity_service_desk.db"

# create the SQLAlchemy engine 
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # required for SQLite when FastAPI handles requests across threads
    connect_args={"check_same_thread": False},
)

# factory for creating database session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# base class future SQLAlchemy models will inherit from
class Base(DeclarativeBase):
    pass


# FastAPI dependency that gives each request a database session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        # provide the active session to the endpoint using this dependency
        yield db
    finally:
        # always close the session after the request finishes
        db.close()
