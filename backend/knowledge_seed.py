from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import Base, SessionLocal, engine
from .enums import KnowledgeCategory


# Fixed fictional articles used to populate the local knowledge base.
KNOWLEDGE_ARTICLES = [
    {
        "title": "How to Report a Suspicious Email",
        "summary": "Steps employees should follow when they receive a message that may be phishing.",
        "category": KnowledgeCategory.PHISHING,
        "content": (
            "Do not click links, open attachments, or reply to a suspicious message. "
            "Use the approved reporting button or forward the message to the security "
            "team according to company procedure.\n\n"
            "Include any context that helps the analyst review the report, such as "
            "whether the message was expected, whether similar messages were received, "
            "and whether any interaction already happened."
        ),
    },
    {
        "title": "Recognizing Social Engineering Requests",
        "summary": "Common warning signs that a phone call, chat message, or email may be impersonation.",
        "category": KnowledgeCategory.SOCIAL_ENGINEERING,
        "content": (
            "Social engineering often relies on urgency, secrecy, authority, or fear. "
            "Employees should be careful with requests for credentials, payment changes, "
            "badge information, confidential files, or unusual approvals.\n\n"
            "Verify the requester through a trusted channel before taking action. If "
            "the request still feels unusual, pause the workflow and open a service-desk "
            "ticket for review."
        ),
    },
    {
        "title": "Password Manager Basics",
        "summary": "Guidance for creating unique passwords and storing them in the approved password manager.",
        "category": KnowledgeCategory.PASSWORD_SECURITY,
        "content": (
            "Use a unique password for every work account and store it in the approved "
            "password manager. Do not reuse personal passwords for company systems or "
            "share passwords through email, chat, screenshots, or documents.\n\n"
            "If a password may have been exposed, change it immediately and report the "
            "concern so the security team can check for related account activity."
        ),
    },
    {
        "title": "Handling Sensitive Files",
        "summary": "Basic data protection steps for storing, sharing, and reporting sensitive information.",
        "category": KnowledgeCategory.DATA_PROTECTION,
        "content": (
            "Sensitive files should only be stored in approved company systems with the "
            "least access needed for the business task. Review recipients before sharing "
            "and avoid sending sensitive content to personal email accounts.\n\n"
            "If a file is shared with the wrong person or placed in a public location, "
            "remove access if you can and submit a ticket with the file location, time, "
            "and intended recipient."
        ),
    },
    {
        "title": "Responding to Unexpected MFA Prompts",
        "summary": "What to do when multi-factor authentication prompts appear unexpectedly.",
        "category": KnowledgeCategory.ACCOUNT_SECURITY,
        "content": (
            "Unexpected MFA prompts may mean someone else has a password and is trying "
            "to sign in. Deny the prompt if the authenticator gives that option, then "
            "change the account password from a trusted device.\n\n"
            "Report repeated or unexplained prompts to the service desk. Include the "
            "time of the prompt, the account involved, and whether any prompt was approved."
        ),
    },
    {
        "title": "Security Training Request Checklist",
        "summary": "Information to include when requesting cybersecurity awareness training.",
        "category": KnowledgeCategory.SECURITY_TRAINING,
        "content": (
            "Training requests should include the audience, department, preferred date, "
            "topic, and whether the session is for new hires, managers, or a specific "
            "business workflow.\n\n"
            "Useful topics include phishing recognition, safe data handling, password "
            "manager setup, social engineering awareness, and reporting procedures."
        ),
    },
    {
        "title": "Office Security Awareness Reminders",
        "summary": "Short reminders for everyday security habits in shared workspaces.",
        "category": KnowledgeCategory.SECURITY_AWARENESS,
        "content": (
            "Lock your screen when leaving a workstation, keep visitor badges visible, "
            "and avoid discussing confidential information in public areas. Challenge "
            "tailgating politely by directing unknown visitors to reception.\n\n"
            "Report lost badges, unattended devices, suspicious visitors, and unusual "
            "requests through the service desk so the security team can follow up."
        ),
    },
    {
        "title": "When to Open a General Security Ticket",
        "summary": "Examples of security concerns that do not fit another request category.",
        "category": KnowledgeCategory.GENERAL_SECURITY,
        "content": (
            "Open a general security ticket when a concern does not fit a specific "
            "category but still needs review. Examples include unclear mailbox routing, "
            "questions about approved tools, or requests for basic security guidance.\n\n"
            "Include the business context, system names, dates, screenshots if allowed, "
            "and the outcome you need from the security team."
        ),
    },
]


# Insert any missing knowledge articles without changing existing records.
def seed_knowledge_articles(db: Session) -> int:
    existing_titles = set(db.scalars(select(models.KnowledgeArticle.title)).all())
    created_count = 0

    for article_data in KNOWLEDGE_ARTICLES:
        if article_data["title"] in existing_titles:
            # Skip articles that were already inserted in a previous seed run.
            continue

        db.add(models.KnowledgeArticle(**article_data))
        created_count += 1

    if created_count:
        # Commit once after all missing articles have been added.
        db.commit()

    return created_count


# Main seed operation for local knowledge-base data.
def seed_database() -> None:
    # Ensure tables exist when the script runs outside the FastAPI server.
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        created_count = seed_knowledge_articles(db)

    print(f"Knowledge articles created: {created_count}")


# Allows the script to run with: python -m backend.knowledge_seed
if __name__ == "__main__":
    seed_database()
