import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { DEPARTMENTS, TICKET_CATEGORIES } from "../constants/tickets.js";
import { createTicket } from "../services/api.js";

const initialFormData = {
  title: "",
  description: "",
  requester_name: "",
  requester_email: "",
  department: "",
  category: "",
};

function SubmitRequest() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(initialFormData);
  const [createdTicket, setCreatedTicket] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    const { name, value } = event.target;
    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
  }

  function validateForm() {
    return Object.values(formData).every((value) => value.trim());
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!validateForm()) {
      setError("Please complete all required fields.");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      const ticket = await createTicket(formData);
      setCreatedTicket(ticket);
    } catch (requestError) {
      setError(requestError.message || "Unable to submit request.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function submitAnotherRequest() {
    setFormData(initialFormData);
    setCreatedTicket(null);
    setError("");
  }

  if (createdTicket) {
    return (
      <section className="page-stack">
        <div className="section-heading">
          <p className="eyebrow">Request Intake</p>
          <h2>Request submitted successfully.</h2>
        </div>

        <div className="panel success-panel">
          <dl className="summary-list">
            <div>
              <dt>Ticket</dt>
              <dd>{createdTicket.ticket_number}</dd>
            </div>
            <div>
              <dt>Priority</dt>
              <dd>{createdTicket.priority}</dd>
            </div>
            <div>
              <dt>Assigned Team</dt>
              <dd>{createdTicket.assigned_team}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{createdTicket.status}</dd>
            </div>
          </dl>

          <div className="button-row">
            <button
              className="primary-button"
              onClick={() => navigate(`/tickets/${createdTicket.id}`)}
            >
              View Ticket
            </button>
            <button className="secondary-button" onClick={submitAnotherRequest}>
              Submit Another Request
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <div className="section-heading">
        <p className="eyebrow">Request Intake</p>
        <h2>Submit Cybersecurity Request</h2>
      </div>

      <form className="panel form-panel" onSubmit={handleSubmit}>
        {error ? <div className="form-error">{error}</div> : null}

        <div className="form-grid">
          <label className="form-field" htmlFor="title">
            <span>Title</span>
            <input
              id="title"
              name="title"
              type="text"
              maxLength="200"
              required
              value={formData.title}
              onChange={updateField}
            />
          </label>

          <label className="form-field" htmlFor="requester_name">
            <span>Requester Name</span>
            <input
              id="requester_name"
              name="requester_name"
              type="text"
              maxLength="100"
              required
              value={formData.requester_name}
              onChange={updateField}
            />
          </label>

          <label className="form-field" htmlFor="requester_email">
            <span>Requester Email</span>
            <input
              id="requester_email"
              name="requester_email"
              type="email"
              required
              value={formData.requester_email}
              onChange={updateField}
            />
          </label>

          <label className="form-field" htmlFor="department">
            <span>Department</span>
            <select
              id="department"
              name="department"
              required
              value={formData.department}
              onChange={updateField}
            >
              <option value="">Select department</option>
              {DEPARTMENTS.map((department) => (
                <option key={department} value={department}>
                  {department}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field" htmlFor="category">
            <span>Category</span>
            <select
              id="category"
              name="category"
              required
              value={formData.category}
              onChange={updateField}
            >
              <option value="">Select category</option>
              {TICKET_CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field form-field-full" htmlFor="description">
            <span>Description</span>
            <textarea
              id="description"
              name="description"
              rows="6"
              required
              value={formData.description}
              onChange={updateField}
            />
          </label>
        </div>

        <div className="button-row">
          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Submitting..." : "Submit Request"}
          </button>
        </div>
      </form>
    </section>
  );
}

export default SubmitRequest;
