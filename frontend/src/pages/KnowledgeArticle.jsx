import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { KNOWLEDGE_CATEGORIES } from "../constants/knowledge.js";
import {
  deleteKnowledgeArticle,
  getKnowledgeArticle,
  updateKnowledgeArticle,
} from "../services/api.js";
import { formatDateTime } from "../utils/format.js";

function KnowledgeArticle() {
  const { articleId } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [formData, setFormData] = useState({
    title: "",
    summary: "",
    category: KNOWLEDGE_CATEGORIES[0],
    content: "",
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [saveError, setSaveError] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let isCurrent = true;

    async function loadArticle() {
      setIsLoading(true);
      setError("");

      try {
        const articleData = await getKnowledgeArticle(articleId);

        if (isCurrent) {
          setArticle(articleData);
          setFormData({
            title: articleData.title,
            summary: articleData.summary,
            category: articleData.category,
            content: articleData.content,
          });
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || "Unable to load article.");
          setArticle(null);
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadArticle();

    return () => {
      isCurrent = false;
    };
  }, [articleId, reloadKey]);

  const patchPayload = useMemo(() => {
    if (!article) {
      return {};
    }

    const payload = {};

    if (formData.title !== article.title) {
      payload.title = formData.title;
    }

    if (formData.summary !== article.summary) {
      payload.summary = formData.summary;
    }

    if (formData.category !== article.category) {
      payload.category = formData.category;
    }

    if (formData.content !== article.content) {
      payload.content = formData.content;
    }

    return payload;
  }, [article, formData]);

  const hasChanges = Object.keys(patchPayload).length > 0;

  function updateField(event) {
    const { name, value } = event.target;
    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
    setSaveMessage("");
    setSaveError("");
    setDeleteError("");
  }

  function cancelEdit() {
    setFormData({
      title: article.title,
      summary: article.summary,
      category: article.category,
      content: article.content,
    });
    setIsEditing(false);
    setSaveError("");
    setSaveMessage("");
  }

  async function saveChanges(event) {
    event.preventDefault();

    if (!hasChanges) {
      setIsEditing(false);
      return;
    }

    setIsSaving(true);
    setSaveMessage("");
    setSaveError("");

    try {
      const updatedArticle = await updateKnowledgeArticle(articleId, patchPayload);
      setArticle(updatedArticle);
      setFormData({
        title: updatedArticle.title,
        summary: updatedArticle.summary,
        category: updatedArticle.category,
        content: updatedArticle.content,
      });
      setIsEditing(false);
      setSaveMessage("Article updated successfully.");
    } catch (requestError) {
      setSaveError(requestError.message || "Unable to update article.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeleteArticle() {
    if (isDeleting) {
      return;
    }

    const confirmed = window.confirm(
      `Delete article "${article.title}"?\n\nThis action cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    setIsDeleting(true);
    setDeleteError("");

    try {
      await deleteKnowledgeArticle(articleId);
      navigate("/knowledge");
    } catch (requestError) {
      setDeleteError(requestError.message || "Unable to delete article.");
    } finally {
      setIsDeleting(false);
    }
  }

  if (isLoading) {
    return <section className="panel state-message">Loading article...</section>;
  }

  if (error) {
    return (
      <section className="panel state-message error-state">
        <p>{error}</p>
        <div className="button-row">
          <button
            className="primary-button"
            type="button"
            onClick={() => setReloadKey((key) => key + 1)}
          >
            Retry
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={() => navigate("/knowledge")}
          >
            Back to Knowledge Base
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <div className="detail-heading knowledge-detail-heading">
        <button className="text-button" onClick={() => navigate("/knowledge")}>
          Back to Knowledge Base
        </button>
        <div>
          <p className="eyebrow">{article.category}</p>
          <h2>{article.title}</h2>
          <p className="supporting-text">{article.summary}</p>
        </div>
        <div className="button-row detail-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              if (isEditing) {
                cancelEdit();
              } else {
                setIsEditing(true);
              }
            }}
          >
            {isEditing ? "Close Editor" : "Edit Article"}
          </button>
        </div>
      </div>

      {saveMessage ? <div className="form-success">{saveMessage}</div> : null}

      {isEditing ? (
        <form className="panel form-panel" onSubmit={saveChanges}>
          <div className="form-grid">
            <label className="form-field" htmlFor="detail-article-title">
              <span>Title</span>
              <input
                id="detail-article-title"
                name="title"
                maxLength="200"
                required
                value={formData.title}
                onChange={updateField}
              />
            </label>

            <label className="form-field" htmlFor="detail-article-category">
              <span>Category</span>
              <select
                id="detail-article-category"
                name="category"
                value={formData.category}
                onChange={updateField}
              >
                {KNOWLEDGE_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </label>

            <label
              className="form-field form-field-full"
              htmlFor="detail-article-summary"
            >
              <span>Summary</span>
              <input
                id="detail-article-summary"
                name="summary"
                maxLength="500"
                required
                value={formData.summary}
                onChange={updateField}
              />
            </label>

            <label
              className="form-field form-field-full"
              htmlFor="detail-article-content"
            >
              <span>Content</span>
              <textarea
                id="detail-article-content"
                name="content"
                rows="10"
                required
                value={formData.content}
                onChange={updateField}
              />
            </label>
          </div>

          {saveError ? <div className="form-error">{saveError}</div> : null}

          <div className="button-row">
            <button
              className="primary-button"
              type="submit"
              disabled={!hasChanges || isSaving}
            >
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
            <button
              className="secondary-button"
              type="button"
              disabled={isSaving}
              onClick={cancelEdit}
            >
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <article className="panel detail-panel knowledge-article-panel">
          <dl className="detail-list compact-detail-list">
            <div>
              <dt>Updated</dt>
              <dd>{formatDateTime(article.updated_at)}</dd>
            </div>
            <div>
              <dt>Created</dt>
              <dd>{formatDateTime(article.created_at)}</dd>
            </div>
          </dl>
          <div className="article-content">
            {article.content.split(/\n{2,}/).map((paragraph, index) => (
              <p key={`${article.id}-${index}`}>{paragraph}</p>
            ))}
          </div>
        </article>
      )}

      <div className="panel detail-panel destructive-panel">
        <div>
          <p className="panel-label">Destructive Action</p>
          <h3>Delete Article</h3>
          <p className="supporting-text">
            Permanently remove this article from the knowledge base.
          </p>
        </div>

        {deleteError ? (
          <div className="form-error delete-error">{deleteError}</div>
        ) : null}

        <div className="button-row destructive-actions">
          <button
            className="danger-button"
            type="button"
            disabled={isDeleting}
            onClick={handleDeleteArticle}
          >
            {isDeleting ? "Deleting..." : "Delete Article"}
          </button>
        </div>
      </div>
    </section>
  );
}

export default KnowledgeArticle;
