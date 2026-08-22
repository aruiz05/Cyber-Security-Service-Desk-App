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

## Current Ticket Workflow

- Automatic sequential ticket numbering
- Automatic category-based ticket routing
- Automatic default priority assignment
- First-response timestamp tracking
- Resolution timestamp tracking

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

## API Endpoints

<!-- Current API routes exposed by the FastAPI backend. -->

- `GET /`
- `GET /health`
- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}`
- `DELETE /tickets/{ticket_id}`
