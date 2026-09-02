import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { KNOWLEDGE_CATEGORIES } from "../constants/knowledge.js";
import {
  createKnowledgeArticle,
  getKnowledgeArticles,
} from "../services/api.js";
import { formatDateTime } from "../utils/format.js";

const blankArticle = {
  title: "",
  summary: "",
  category: KNOWLEDGE_CATEGORIES[0],
  content: "",
};

function KnowledgeBase() {
  const navigate = useNavigate();
  const [articles, setArticles] = useState([]);
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState(blankArticle);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  const hasActiveFilters = useMemo(
    () => Boolean(debouncedSearch || selectedCategory),
    [debouncedSearch, selectedCategory],
  );

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
    }, 400);

    return () => window.clearTimeout(timeoutId);
  }, [searchInput]);

  useEffect(() => {
    let isCurrent = true;

    async function loadArticles() {
      setIsLoading(true);
      setError("");

      try {
        const articleData = await getKnowledgeArticles({
          search: debouncedSearch,
          category: selectedCategory,
        });

        if (isCurrent) {
          setArticles(articleData);
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || "Unable to load knowledge articles.");
          setArticles([]);
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadArticles();

    return () => {
      isCurrent = false;
    };
  }, [debouncedSearch, selectedCategory, reloadKey]);

  function updateFormField(event) {
    const { name, value } = event.target;
    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
    setFormError("");
  }

  function clearFilters() {
    setSearchInput("");
    setDebouncedSearch("");
    setSelectedCategory("");
  }

  function retryLoad() {
    setReloadKey((currentKey) => currentKey + 1);
  }

  async function handleCreateArticle(event) {
    event.preventDefault();

    setIsCreating(true);
    setFormError("");

    try {
      const createdArticle = await createKnowledgeArticle(formData);
      setFormData(blankArticle);
      setShowCreateForm(false);
      navigate(`/knowledge/${createdArticle.id}`);
    } catch (requestError) {
      setFormError(requestError.message || "Unable to create article.");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <section className="page-stack">
      <div className="section-heading knowledge-heading">
        <div>
          <p className="eyebrow">Security Guidance</p>
          <h2>Knowledge Base</h2>
          <p className="supporting-text">
            Search internal guidance for cybersecurity awareness requests.
          </p>
        </div>
        <button
          className="secondary-button"
          type="button"
          onClick={() => setShowCreateForm((isVisible) => !isVisible)}
        >
          {showCreateForm ? "Close Form" : "New Article"}
        </button>
      </div>

      {showCreateForm ? (
        <form className="panel form-panel" onSubmit={handleCreateArticle}>
          <div className="form-grid">
            <label className="form-field" htmlFor="article-title">
              <span>Title</span>
              <input
                id="article-title"
                name="title"
                maxLength="200"
                required
                value={formData.title}
                onChange={updateFormField}
              />
            </label>

            <label className="form-field" htmlFor="article-category">
              <span>Category</span>
              <select
                id="article-category"
                name="category"
                value={formData.category}
                onChange={updateFormField}
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
              htmlFor="article-summary"
            >
              <span>Summary</span>
              <input
                id="article-summary"
                name="summary"
                maxLength="500"
                required
                value={formData.summary}
                onChange={updateFormField}
              />
            </label>

            <label
              className="form-field form-field-full"
              htmlFor="article-content"
            >
              <span>Content</span>
              <textarea
                id="article-content"
                name="content"
                rows="8"
                required
                value={formData.content}
                onChange={updateFormField}
              />
            </label>
          </div>

          {formError ? <div className="form-error">{formError}</div> : null}

          <div className="button-row">
            <button
              className="primary-button"
              type="submit"
              disabled={isCreating}
            >
              {isCreating ? "Creating..." : "Create Article"}
            </button>
          </div>
        </form>
      ) : null}

      <div className="panel knowledge-controls">
        <div className="control-field control-field-wide">
          <label htmlFor="knowledge-search">Search</label>
          <input
            id="knowledge-search"
            type="search"
            placeholder="Search articles..."
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
          />
        </div>

        <div className="control-field">
          <label htmlFor="knowledge-category">Category</label>
          <select
            id="knowledge-category"
            value={selectedCategory}
            onChange={(event) => setSelectedCategory(event.target.value)}
          >
            <option value="">All Categories</option>
            {KNOWLEDGE_CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <button
          className="secondary-button control-action"
          type="button"
          onClick={clearFilters}
        >
          Clear Filters
        </button>
      </div>

      {isLoading ? (
        <section className="panel state-message">Loading articles...</section>
      ) : error ? (
        <section className="panel state-message error-state">
          <p>{error}</p>
          <button className="primary-button" type="button" onClick={retryLoad}>
            Retry
          </button>
        </section>
      ) : articles.length === 0 ? (
        <section className="panel state-message">
          {hasActiveFilters
            ? "No articles match the current filters."
            : "No knowledge articles found."}
        </section>
      ) : (
        <div className="knowledge-grid">
          {articles.map((article) => (
            <button
              key={article.id}
              className="panel knowledge-card"
              type="button"
              onClick={() => navigate(`/knowledge/${article.id}`)}
            >
              <div>
                <p className="panel-label">{article.category}</p>
                <h3>{article.title}</h3>
              </div>
              <p>{article.summary}</p>
              <span>Updated {formatDateTime(article.updated_at)}</span>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

export default KnowledgeBase;
