from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .enums import KnowledgeCategory


# Build SQLAlchemy WHERE conditions from optional knowledge-base filters.
def build_knowledge_filters(
    search: str | None = None,
    category: KnowledgeCategory | None = None,
) -> list:
    filters = []

    if category is not None:
        # Category filtering is an exact enum match.
        filters.append(models.KnowledgeArticle.category == category)

    if search is not None and search.strip():
        # Search article text fields with case-insensitive partial matching.
        search_pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                models.KnowledgeArticle.title.ilike(search_pattern),
                models.KnowledgeArticle.summary.ilike(search_pattern),
                models.KnowledgeArticle.content.ilike(search_pattern),
            )
        )

    return filters


# Create and persist a new knowledge-base article.
def create_article(
    db: Session,
    article: schemas.KnowledgeArticleCreate,
) -> models.KnowledgeArticle:
    db_article = models.KnowledgeArticle(**article.model_dump())
    db.add(db_article)

    try:
        # Commit the article so SQLite stores it permanently.
        db.commit()
    except IntegrityError:
        # Roll back failed writes so the session can continue safely.
        db.rollback()
        raise

    # Refresh loads database-generated fields such as id and timestamps.
    db.refresh(db_article)
    return db_article


# Retrieve knowledge-base articles with optional search and category filters.
def get_articles(
    db: Session,
    search: str | None = None,
    category: KnowledgeCategory | None = None,
) -> list[models.KnowledgeArticle]:
    filters = build_knowledge_filters(search=search, category=category)

    query = (
        select(models.KnowledgeArticle)
        # Filtering and search happen in SQLite.
        .where(*filters)
        .order_by(models.KnowledgeArticle.updated_at.desc(), models.KnowledgeArticle.id.desc())
    )

    return list(db.scalars(query).all())


# Retrieve one article by database id.
def get_article(db: Session, article_id: int) -> models.KnowledgeArticle | None:
    return db.get(models.KnowledgeArticle, article_id)


# Apply a partial update to an existing knowledge-base article.
def update_article(
    db: Session,
    db_article: models.KnowledgeArticle,
    article_update: schemas.KnowledgeArticleUpdate,
) -> models.KnowledgeArticle:
    # Only update fields the request actually sent.
    update_data = article_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_article, field, value)

    try:
        # Commit the changed article to SQLite.
        db.commit()
    except IntegrityError:
        # Roll back failed writes so the session is not left in a bad state.
        db.rollback()
        raise

    # Refresh returns the latest database state, including updated_at.
    db.refresh(db_article)
    return db_article


# Delete an existing knowledge-base article.
def delete_article(db: Session, db_article: models.KnowledgeArticle) -> None:
    db.delete(db_article)
    db.commit()
