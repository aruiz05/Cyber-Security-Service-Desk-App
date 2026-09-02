from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import knowledge_crud, models, schemas
from ..database import get_db
from ..enums import KnowledgeCategory


# Router groups all knowledge-base endpoints under /knowledge in Swagger.
router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


# Create a knowledge-base article and return the saved database record.
@router.post(
    "",
    response_model=schemas.KnowledgeArticleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_article(
    article: schemas.KnowledgeArticleCreate,
    db: Session = Depends(get_db),
) -> models.KnowledgeArticle:
    try:
        return knowledge_crud.create_article(db, article)
    except IntegrityError as exc:
        # Keep database failures from becoming generic 500 errors.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error",
        ) from exc


# Return articles with optional search and category filters.
@router.get("", response_model=list[schemas.KnowledgeArticleResponse])
def get_articles(
    # Enum type gives Swagger valid category values and FastAPI validation.
    category: KnowledgeCategory | None = None,
    # Optional text search across title, summary, and article content.
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[models.KnowledgeArticle]:
    return knowledge_crud.get_articles(db=db, search=search, category=category)


# Return one knowledge-base article by id, or 404 if it does not exist.
@router.get("/{article_id}", response_model=schemas.KnowledgeArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
) -> models.KnowledgeArticle:
    db_article = knowledge_crud.get_article(db, article_id)
    if db_article is None:
        # Missing articles use a consistent 404 message.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge article not found",
        )

    return db_article


# Partially update an existing knowledge-base article.
@router.patch("/{article_id}", response_model=schemas.KnowledgeArticleResponse)
def update_article(
    article_id: int,
    article_update: schemas.KnowledgeArticleUpdate,
    db: Session = Depends(get_db),
) -> models.KnowledgeArticle:
    db_article = knowledge_crud.get_article(db, article_id)
    if db_article is None:
        # Missing articles cannot be updated.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge article not found",
        )

    try:
        return knowledge_crud.update_article(db, db_article, article_update)
    except IntegrityError as exc:
        # Keep database failures from becoming generic 500 errors.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error",
        ) from exc


# Delete a knowledge-base article by id and return 204 when successful.
@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, db: Session = Depends(get_db)) -> Response:
    db_article = knowledge_crud.get_article(db, article_id)
    if db_article is None:
        # Missing articles cannot be deleted.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge article not found",
        )

    knowledge_crud.delete_article(db, db_article)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
