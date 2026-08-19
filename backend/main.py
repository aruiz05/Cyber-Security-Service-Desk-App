from fastapi import Depends, FastAPI, HTTPException, status

# SQLAlchemy is used for a lightweight database
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# import reusable database session from module
from .database import get_db


# create FastAPI app and set titlr
app = FastAPI(title="Cybersecurity Awareness Service Desk API")


# root endpoint
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Cybersecurity Awareness Service Desk API"}


# health endpoint 
@app.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        # run a simple SQL statement to verify SQLite is reachable
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # return a service unavailable response if the database check fails
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc

    # if the query succeeds report that the service is healthy.
    return {"status": "healthy"}
