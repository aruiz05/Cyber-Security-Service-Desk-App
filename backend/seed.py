from collections import Counter
from datetime import timedelta

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas, ticket_logic
from .database import Base, SessionLocal, engine
from .enums import Department, TicketCategory, TicketStatus


# Fixed fictional dataset used to populate the local development database.
SEED_TICKETS = [
    {
        "title": "Suspicious Microsoft 365 Password Reset Email",
        "description": "Employee received an unexpected email claiming their Microsoft 365 password would expire unless they signed in through an external link.",
        "requester_name": "Jordan Lee",
        "requester_email": "jordan.lee@example.com",
        "department": Department.FINANCE,
        "category": TicketCategory.PHISHING,
        "status": TicketStatus.NEW,
        "days_ago": 1,
    },
    {
        "title": "QR Code Login Verification Email",
        "description": "Sales employee reported a message containing a QR code that claimed to verify access to a customer portal.",
        "requester_name": "Taylor Morgan",
        "requester_email": "taylor.morgan@example.com",
        "department": Department.SALES,
        "category": TicketCategory.PHISHING,
        "status": TicketStatus.IN_PROGRESS,
        "days_ago": 3,
        "response_minutes": 28,
    },
    {
        "title": "Suspicious Attachment from Unknown Sender",
        "description": "A customer service representative received an unexpected attachment from an unfamiliar sender and requested review.",
        "requester_name": "Casey Brooks",
        "requester_email": "casey.brooks@example.com",
        "department": Department.CUSTOMER_SERVICE,
        "category": TicketCategory.PHISHING,
        "status": TicketStatus.WAITING_FOR_USER,
        "days_ago": 5,
        "response_minutes": 52,
    },
    {
        "title": "Fake Invoice Approval Request",
        "description": "Finance received an invoice approval request that appeared to impersonate a known vendor contact.",
        "requester_name": "Morgan Patel",
        "requester_email": "morgan.patel@example.com",
        "department": Department.FINANCE,
        "category": TicketCategory.PHISHING,
        "status": TicketStatus.RESOLVED,
        "days_ago": 8,
        "response_minutes": 18,
        "resolution_hours": 5,
        "resolution_notes": "Employee reported the phishing email and the message was removed from the mailbox.",
    },
    {
        "title": "Phishing Report Button Question",
        "description": "Marketing asked whether a suspicious newsletter link should be reported with the phishing-reporting button.",
        "requester_name": "Jamie Carter",
        "requester_email": "jamie.carter@example.com",
        "department": Department.MARKETING,
        "category": TicketCategory.PHISHING,
        "status": TicketStatus.IN_PROGRESS,
        "days_ago": 2,
        "response_minutes": 12,
    },
    {
        "title": "Possible Executive Impersonation Email",
        "description": "An employee received an urgent message appearing to come from an executive requesting a confidential financial action.",
        "requester_name": "Alex Rivera",
        "requester_email": "alex.rivera@example.com",
        "department": Department.LEGAL,
        "category": TicketCategory.PHISHING,
        "status": TicketStatus.RESOLVED,
        "days_ago": 12,
        "response_minutes": 34,
        "resolution_hours": 7,
        "resolution_notes": "The message was confirmed as impersonation and reported through the approved process.",
    },
    {
        "title": "Payroll Direct Deposit Change Email",
        "description": "Human Resources received a payroll-change email that used unusual wording and requested urgent processing.",
        "requester_name": "Riley Chen",
        "requester_email": "riley.chen@example.com",
        "department": Department.HUMAN_RESOURCES,
        "category": TicketCategory.PHISHING,
        "status": TicketStatus.CLOSED,
        "days_ago": 20,
        "response_minutes": 41,
        "resolution_hours": 10,
        "resolution_notes": "The request was confirmed fraudulent, blocked, and closed after user follow-up.",
    },
    {
        "title": "Phone Call Requesting Badge Information",
        "description": "Operations reported a caller asking for employee badge details while claiming to be from building security.",
        "requester_name": "Cameron Davis",
        "requester_email": "cameron.davis@example.com",
        "department": Department.OPERATIONS,
        "category": TicketCategory.SOCIAL_ENGINEERING,
        "status": TicketStatus.RESOLVED,
        "days_ago": 10,
        "response_minutes": 67,
        "resolution_hours": 8,
        "resolution_notes": "The team reviewed the report and reminded staff of visitor verification procedures.",
    },
    {
        "title": "Vendor Impersonation Chat Message",
        "description": "Engineering received a chat message from someone claiming to be a vendor and requesting internal project details.",
        "requester_name": "Avery Thompson",
        "requester_email": "avery.thompson@example.com",
        "department": Department.ENGINEERING,
        "category": TicketCategory.SOCIAL_ENGINEERING,
        "status": TicketStatus.IN_PROGRESS,
        "days_ago": 4,
        "response_minutes": 120,
    },
    {
        "title": "Unusual Text Message About Company Account",
        "description": "Sales received a text message claiming their company account would be disabled unless they confirmed their identity.",
        "requester_name": "Drew Wilson",
        "requester_email": "drew.wilson@example.com",
        "department": Department.SALES,
        "category": TicketCategory.SOCIAL_ENGINEERING,
        "status": TicketStatus.NEW,
        "days_ago": 1,
    },
    {
        "title": "Reception Desk Visitor Verification Concern",
        "description": "Operations requested guidance after a visitor attempted to access a restricted floor without a verified appointment.",
        "requester_name": "Samira Khan",
        "requester_email": "samira.khan@example.com",
        "department": Department.OPERATIONS,
        "category": TicketCategory.SOCIAL_ENGINEERING,
        "status": TicketStatus.CLOSED,
        "days_ago": 26,
        "response_minutes": 95,
        "resolution_hours": 16,
        "resolution_notes": "The visitor process was reviewed and the reception team received updated guidance.",
    },
    {
        "title": "Possible Password Sharing Concern",
        "description": "Customer Service asked for guidance after a team member mentioned sharing a password for temporary coverage.",
        "requester_name": "Priya Shah",
        "requester_email": "priya.shah@example.com",
        "department": Department.CUSTOMER_SERVICE,
        "category": TicketCategory.PASSWORD_SECURITY,
        "status": TicketStatus.WAITING_FOR_USER,
        "days_ago": 6,
        "response_minutes": 180,
    },
    {
        "title": "Password Reset After Public WiFi Login",
        "description": "A marketing employee requested a password reset after signing in from public WiFi while traveling.",
        "requester_name": "Devon Green",
        "requester_email": "devon.green@example.com",
        "department": Department.MARKETING,
        "category": TicketCategory.PASSWORD_SECURITY,
        "status": TicketStatus.IN_PROGRESS,
        "days_ago": 7,
        "response_minutes": 36,
    },
    {
        "title": "Password Manager Setup Assistance",
        "description": "Human Resources requested assistance setting up the approved password manager for a shared HR workflow.",
        "requester_name": "Elena Garcia",
        "requester_email": "elena.garcia@example.com",
        "department": Department.HUMAN_RESOURCES,
        "category": TicketCategory.PASSWORD_SECURITY,
        "status": TicketStatus.CLOSED,
        "days_ago": 18,
        "response_minutes": 240,
        "resolution_hours": 20,
        "resolution_notes": "Password manager access was configured and the requester confirmed the workflow was updated.",
    },
    {
        "title": "Customer Spreadsheet Shared with External Recipient",
        "description": "A Finance employee accidentally sent a spreadsheet containing customer information to an external email address.",
        "requester_name": "Noah Bennett",
        "requester_email": "noah.bennett@example.com",
        "department": Department.FINANCE,
        "category": TicketCategory.DATA_LOSS_PREVENTION,
        "status": TicketStatus.RESOLVED,
        "days_ago": 14,
        "response_minutes": 22,
        "resolution_hours": 30,
        "resolution_notes": "Data Protection reviewed the incident and completed the required follow-up.",
    },
    {
        "title": "Sensitive File Shared to Personal Email",
        "description": "Legal reported that a sensitive document may have been forwarded to a personal email address by mistake.",
        "requester_name": "Harper Collins",
        "requester_email": "harper.collins@example.com",
        "department": Department.LEGAL,
        "category": TicketCategory.DATA_LOSS_PREVENTION,
        "status": TicketStatus.NEW,
        "days_ago": 2,
    },
    {
        "title": "Removable Media Use Question",
        "description": "Engineering asked whether a removable drive from a conference could be used on a company workstation.",
        "requester_name": "Quinn Foster",
        "requester_email": "quinn.foster@example.com",
        "department": Department.ENGINEERING,
        "category": TicketCategory.DATA_LOSS_PREVENTION,
        "status": TicketStatus.WAITING_FOR_USER,
        "days_ago": 9,
        "response_minutes": 73,
    },
    {
        "title": "Confidential Contract Uploaded to Public Folder",
        "description": "Sales reported that a confidential customer contract was accidentally placed in a broadly accessible folder.",
        "requester_name": "Reese Parker",
        "requester_email": "reese.parker@example.com",
        "department": Department.SALES,
        "category": TicketCategory.DATA_LOSS_PREVENTION,
        "status": TicketStatus.CLOSED,
        "days_ago": 22,
        "response_minutes": 19,
        "resolution_hours": 24,
        "resolution_notes": "The file permissions were corrected and the exposure review was completed.",
    },
    {
        "title": "Unpatched Browser Version Report",
        "description": "IT reported that several workstations are running a browser version affected by a recently identified security vulnerability.",
        "requester_name": "Parker Young",
        "requester_email": "parker.young@example.com",
        "department": Department.IT,
        "category": TicketCategory.VULNERABILITY,
        "status": TicketStatus.IN_PROGRESS,
        "days_ago": 5,
        "response_minutes": 44,
    },
    {
        "title": "Outdated VPN Client on Workstations",
        "description": "Operations reported several laptops using an outdated VPN client that requires review and remediation.",
        "requester_name": "Skyler Reed",
        "requester_email": "skyler.reed@example.com",
        "department": Department.OPERATIONS,
        "category": TicketCategory.VULNERABILITY,
        "status": TicketStatus.RESOLVED,
        "days_ago": 16,
        "response_minutes": 160,
        "resolution_hours": 38,
        "resolution_notes": "The affected VPN clients were updated and the workstation list was confirmed complete.",
    },
    {
        "title": "Vulnerable Collaboration Plugin Report",
        "description": "Engineering requested review of a collaboration plugin after a security bulletin identified a vulnerable version.",
        "requester_name": "Rowan Price",
        "requester_email": "rowan.price@example.com",
        "department": Department.ENGINEERING,
        "category": TicketCategory.VULNERABILITY,
        "status": TicketStatus.RESOLVED,
        "days_ago": 24,
        "response_minutes": 310,
        "resolution_hours": 48,
        "resolution_notes": "The vulnerable plugin was removed from affected systems and the team confirmed remediation.",
    },
    {
        "title": "Quarterly Phishing Awareness Training Request",
        "description": "Human Resources requested phishing-awareness training materials for newly hired employees.",
        "requester_name": "Emerson Ward",
        "requester_email": "emerson.ward@example.com",
        "department": Department.HUMAN_RESOURCES,
        "category": TicketCategory.SECURITY_TRAINING,
        "status": TicketStatus.NEW,
        "days_ago": 3,
    },
    {
        "title": "Manager Security Briefing Request",
        "description": "Finance asked for a short briefing to help managers recognize and report suspicious payment requests.",
        "requester_name": "Finley Ross",
        "requester_email": "finley.ross@example.com",
        "department": Department.FINANCE,
        "category": TicketCategory.SECURITY_TRAINING,
        "status": TicketStatus.IN_PROGRESS,
        "days_ago": 11,
        "response_minutes": 360,
    },
    {
        "title": "New Hire Security Training Access",
        "description": "Human Resources requested training-platform access for a group of new employees starting this week.",
        "requester_name": "Hayden Scott",
        "requester_email": "hayden.scott@example.com",
        "department": Department.HUMAN_RESOURCES,
        "category": TicketCategory.SECURITY_TRAINING,
        "status": TicketStatus.RESOLVED,
        "days_ago": 13,
        "response_minutes": 88,
        "resolution_hours": 12,
        "resolution_notes": "Security-awareness materials were delivered to the requesting department.",
    },
    {
        "title": "Security Awareness Poster Request",
        "description": "Marketing requested approved cybersecurity-awareness messaging for digital signage in shared office spaces.",
        "requester_name": "Kendall Turner",
        "requester_email": "kendall.turner@example.com",
        "department": Department.MARKETING,
        "category": TicketCategory.SECURITY_AWARENESS,
        "status": TicketStatus.NEW,
        "days_ago": 4,
    },
    {
        "title": "Department Cyber Safety Presentation",
        "description": "Customer Service requested a short cyber safety presentation for an upcoming department meeting.",
        "requester_name": "Logan Murphy",
        "requester_email": "logan.murphy@example.com",
        "department": Department.CUSTOMER_SERVICE,
        "category": TicketCategory.SECURITY_AWARENESS,
        "status": TicketStatus.CLOSED,
        "days_ago": 29,
        "response_minutes": 140,
        "resolution_hours": 36,
        "resolution_notes": "The awareness presentation was delivered and the department confirmed completion.",
    },
    {
        "title": "Repeated MFA Approval Requests",
        "description": "Employee received multiple unexpected MFA approval notifications while not attempting to sign in.",
        "requester_name": "Monroe Ellis",
        "requester_email": "monroe.ellis@example.com",
        "department": Department.IT,
        "category": TicketCategory.ACCOUNT_SECURITY,
        "status": TicketStatus.IN_PROGRESS,
        "days_ago": 1,
        "response_minutes": 14,
    },
    {
        "title": "Suspicious Login Notification While Traveling",
        "description": "Sales employee received a suspicious login notification from a location they did not recognize.",
        "requester_name": "Nico Ramirez",
        "requester_email": "nico.ramirez@example.com",
        "department": Department.SALES,
        "category": TicketCategory.ACCOUNT_SECURITY,
        "status": TicketStatus.WAITING_FOR_USER,
        "days_ago": 6,
        "response_minutes": 64,
    },
    {
        "title": "Account Lockout After Credential Exposure Concern",
        "description": "Engineering requested review after an employee reported possible credential exposure and a related account lockout.",
        "requester_name": "Peyton Hughes",
        "requester_email": "peyton.hughes@example.com",
        "department": Department.ENGINEERING,
        "category": TicketCategory.ACCOUNT_SECURITY,
        "status": TicketStatus.RESOLVED,
        "days_ago": 17,
        "response_minutes": 26,
        "resolution_hours": 18,
        "resolution_notes": "Affected account credentials were reset and the user confirmed access was restored.",
    },
    {
        "title": "Security Mailbox Triage Question",
        "description": "IT requested guidance on how to route a message sent to the shared security mailbox.",
        "requester_name": "Robin Simmons",
        "requester_email": "robin.simmons@example.com",
        "department": Department.IT,
        "category": TicketCategory.OTHER,
        "status": TicketStatus.NEW,
        "days_ago": 2,
    },
]


# Check whether this specific seed dataset has already been inserted.
def seed_already_exists(db: Session) -> bool:
    # Titles and fictional emails are stable identifiers for this seed data.
    seed_titles = [ticket["title"] for ticket in SEED_TICKETS]
    seed_emails = [ticket["requester_email"] for ticket in SEED_TICKETS]

    # Count matching tickets without deleting or changing existing records.
    existing_seed_count = db.scalar(
        select(func.count())
        .select_from(models.Ticket)
        .where(
            models.Ticket.title.in_(seed_titles),
            models.Ticket.requester_email.in_(seed_emails),
        )
    )

    return bool(existing_seed_count)


# Build realistic timestamps for each seed ticket.
def build_timestamps(seed_ticket: dict, index: int) -> dict:
    now = ticket_logic.utc_now()

    # Spread created dates across the previous month.
    created_at = now - timedelta(
        days=seed_ticket["days_ago"],
        hours=index % 7,
        minutes=(index * 11) % 60,
    )
    status = seed_ticket["status"]

    first_response_at = None
    if status != TicketStatus.NEW:
        # Non-new tickets should have a first response after creation.
        first_response_at = created_at + timedelta(
            minutes=seed_ticket["response_minutes"]
        )

    resolved_at = None
    if status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
        # Resolved and closed tickets should have a completion timestamp.
        resolved_at = first_response_at + timedelta(
            hours=seed_ticket["resolution_hours"]
        )

    # Updated time reflects the latest workflow activity.
    if resolved_at is not None:
        updated_at = resolved_at + timedelta(hours=2 + (index % 5))
    elif first_response_at is not None:
        updated_at = first_response_at + timedelta(hours=1 + (index % 8))
    else:
        updated_at = created_at + timedelta(minutes=5 + index)

    return {
        "created_at": created_at,
        "updated_at": min(updated_at, now),
        "first_response_at": first_response_at,
        "resolved_at": resolved_at,
    }


# Convert one seed record into a SQLAlchemy Ticket object.
def create_seed_ticket(db: Session, seed_ticket: dict, index: int) -> models.Ticket:
    # Validate employee-provided fields with the normal create schema.
    ticket_create = schemas.TicketCreate(
        title=seed_ticket["title"],
        description=seed_ticket["description"],
        requester_name=seed_ticket["requester_name"],
        requester_email=seed_ticket["requester_email"],
        department=seed_ticket["department"],
        category=seed_ticket["category"],
    )

    # Reuse application workflow logic for numbering, routing, and priority.
    ticket_data = ticket_logic.build_new_ticket_data(db, ticket_create.model_dump())

    # Apply seed-specific status, notes, and historical timestamps.
    ticket_data.update(
        {
            "status": seed_ticket["status"],
            "resolution_notes": seed_ticket.get("resolution_notes"),
            **build_timestamps(seed_ticket, index),
        }
    )

    db_ticket = models.Ticket(**ticket_data)
    db.add(db_ticket)
    return db_ticket


# Validate the generated seed tickets before committing them.
def validate_seeded_tickets(tickets: list[models.Ticket]) -> None:
    ticket_numbers = [ticket.ticket_number for ticket in tickets]
    if len(ticket_numbers) != len(set(ticket_numbers)):
        raise ValueError("Seed data generated duplicate ticket numbers.")

    for ticket in tickets:
        # Seed records should match the same routing logic used by the API.
        if ticket.assigned_team != ticket_logic.get_assigned_team(ticket.category):
            raise ValueError(f"Routing mismatch for {ticket.ticket_number}.")

        # Seed records should match the same priority logic used by the API.
        if ticket.priority != ticket_logic.get_default_priority(ticket.category):
            raise ValueError(f"Priority mismatch for {ticket.ticket_number}.")

        # Updated timestamps should never be earlier than creation.
        if ticket.updated_at < ticket.created_at:
            raise ValueError(f"Invalid updated_at for {ticket.ticket_number}.")

        if ticket.first_response_at is not None:
            # First response must happen after the ticket was created.
            if ticket.first_response_at < ticket.created_at:
                raise ValueError(
                    f"Invalid first_response_at for {ticket.ticket_number}."
                )

        if ticket.status == TicketStatus.NEW:
            # New tickets should not already have workflow timestamps.
            if ticket.first_response_at is not None or ticket.resolved_at is not None:
                raise ValueError(f"New ticket has workflow timestamps: {ticket.ticket_number}.")

        if ticket.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
            # Completed tickets need response, resolution, and notes.
            if ticket.resolved_at is None:
                raise ValueError(f"Resolved ticket is missing resolved_at: {ticket.ticket_number}.")
            if ticket.first_response_at is None:
                raise ValueError(
                    f"Resolved ticket is missing first_response_at: {ticket.ticket_number}."
                )
            if ticket.resolved_at < ticket.first_response_at:
                raise ValueError(f"Invalid resolved_at for {ticket.ticket_number}.")
            if not ticket.resolution_notes:
                raise ValueError(
                    f"Resolved ticket is missing resolution notes: {ticket.ticket_number}."
                )
        elif ticket.resolved_at is not None:
            raise ValueError(f"Open ticket has resolved_at: {ticket.ticket_number}.")


# Print a concise summary after successful seeding.
def print_summary(tickets: list[models.Ticket]) -> None:
    status_counts = Counter(ticket.status.value for ticket in tickets)

    print("Seed complete.")
    print()
    print(f"Tickets created: {len(tickets)}")
    print()
    for status in TicketStatus:
        print(f"{status.value}: {status_counts[status.value]}")


# Main seed operation for local development data.
def seed_database() -> None:
    # Ensure tables exist when the script runs outside the FastAPI server.
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Skip instead of duplicating the fixed development dataset.
        if seed_already_exists(db):
            print("Database already contains the development seed dataset.")
            print("Seed operation skipped.")
            return

        created_tickets = []

        try:
            # Build all seed tickets before committing any of them.
            for index, seed_ticket in enumerate(SEED_TICKETS):
                created_tickets.append(create_seed_ticket(db, seed_ticket, index))

            # Flush assigns generated values so validation can inspect them.
            db.flush()
            validate_seeded_tickets(created_tickets)
            db.commit()
        except (IntegrityError, ValidationError, ValueError) as exc:
            # Roll back so a failed seed run does not leave partial data.
            db.rollback()
            raise RuntimeError("Seed operation failed. No seed tickets were saved.") from exc

        print_summary(created_tickets)


# Allows the script to run with: python -m backend.seed
if __name__ == "__main__":
    seed_database()
