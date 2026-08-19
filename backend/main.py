# FastAPI provides the web app, dependency injection, and HTTP error helpers.
from fastapi import Depends, FastAPI, HTTPException, status

# SQLAlchemy is used here for a lightweight database connection check.
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Import the reusable database session dependency from the database module.
from .database import get_db


# Create the FastAPI application and set the title shown in the API docs.
app = FastAPI(title="Cybersecurity Awareness Service Desk API")


# Root endpoint for confirming the API is running.
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Cybersecurity Awareness Service Desk API"}


# Health endpoint for confirming both the API and database connection are working.
@app.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        # Run a simple SQL statement to verify SQLite is reachable.
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # Return a service-unavailable response if the database check fails.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc

    # If the query succeeds, report that the service is healthy.
    return {"status": "healthy"}
