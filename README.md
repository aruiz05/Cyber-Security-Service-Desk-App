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
- JavaScript
- React
- Vite
- React Router
- Recharts

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
- Ticket filtering, search, sorting, and pagination
- SLA tracking and compliance metrics
- Backend ticket analytics by category, status, and priority
- Ticket creation and resolution trends

## Running the API

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

## Frontend Setup

The frontend is a Vite React application. It currently provides the application layout, navigation, placeholder pages, and backend health connectivity.

The frontend currently supports the ticket queue, search, filtering, sorting, pagination, request submission, ticket detail views, analyst ticket workflow updates, ticket deletion with confirmation, and an analytics dashboard with KPI summary cards, ticket volume charts, created/resolved trends, SLA compliance visualization, and SLA performance by priority.

Reporting features and the knowledge base are not complete yet.

From the project root:

```bash
cd frontend
npm install
npm run dev
```

## Development Seed Data

Populate the local SQLite database with fictional cybersecurity service-desk tickets for development and testing:

```bash
python -m backend.seed
```

The sample tickets use fictional names and example.com email addresses only.

## API Documentation

After starting the server, open:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## API Endpoints

- `GET /`
- `GET /health`
- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}`
- `DELETE /tickets/{ticket_id}`
- `GET /analytics/summary`
- `GET /analytics/categories`
- `GET /analytics/status`
- `GET /analytics/priorities`
- `GET /analytics/trends`
- `GET /analytics/sla`

## Ticket Queue Examples

- `GET /tickets?status=New`
- `GET /tickets?category=Phishing`
- `GET /tickets?priority=Critical`
- `GET /tickets?department=Finance`
- `GET /tickets?assigned_team=Human Risk Management`
- `GET /tickets?search=Microsoft`
- `GET /tickets?sort_by=ticket_number&sort_order=asc`
- `GET /tickets?page=2&page_size=10`
