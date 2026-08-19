# Cybersecurity Awareness Service Desk

Cybersecurity Awareness Service Desk is project intended to simulate a enterprise cybersecurity request management system.

## Backend Setup

The backend is a FastAPI application using SQLAlchemy with a local SQLite database.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

## Ticket Data

The ticket system currently supports information such as:

- Ticket number
- Title and description
- Requester information
- Department
- Security category
- Priority
- Status
- Assigned security team
- Creation and update timestamps
- First response time
- Resolution time
- Resolution notes

## Running the API

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

## API Documentation

After starting the server, open:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc
