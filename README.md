# Cybersecurity Awareness Service Desk

Cybersecurity Awareness Service Desk is a portfolio project intended to simulate an enterprise cybersecurity awareness request-management system.

## Backend Setup

The backend is a FastAPI application using SQLAlchemy with a local SQLite database.

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
