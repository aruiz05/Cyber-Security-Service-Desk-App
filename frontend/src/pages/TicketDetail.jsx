import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import TicketBadge from "../components/TicketBadge.jsx";
import {
  ASSIGNED_TEAMS,
  TICKET_PRIORITIES,
  TICKET_STATUSES,
} from "../constants/tickets.js";
import { deleteTicket, getTicket, updateTicket } from "../services/api.js";
import { formatDateTime } from "../utils/format.js";

function TicketDetail() {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [formData, setFormData] = useState({
    priority: "",
    status: "",
    assigned_team: "",
    resolution_notes: "",
  });
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

    async function loadTicket() {
      setIsLoading(true);
      setError("");

      try {
        const ticketData = await getTicket(ticketId);

        if (isCurrent) {
          setTicket(ticketData);
          setFormData({
            priority: ticketData.priority,
            status: ticketData.status,
            assigned_team: ticketData.assigned_team,
            resolution_notes: ticketData.resolution_notes || "",
          });
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || "Unable to load ticket.");
          setTicket(null);
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadTicket();

    return () => {
      isCurrent = false;
    };
  }, [ticketId, reloadKey]);

  const patchPayload = useMemo(() => {
    if (!ticket) {
      return {};
    }

    const payload = {};

    if (formData.priority !== ticket.priority) {
      payload.priority = formData.priority;
    }

    if (formData.status !== ticket.status) {
      payload.status = formData.status;
    }

    if (formData.assigned_team !== ticket.assigned_team) {
      payload.assigned_team = formData.assigned_team;
    }

    if (formData.resolution_notes !== (ticket.resolution_notes || "")) {
      payload.resolution_notes = formData.resolution_notes;
    }

    return payload;
  }, [formData, ticket]);

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

  async function saveChanges(event) {
    event.preventDefault();

    if (!hasChanges) {
      return;
    }

    setIsSaving(true);
    setSaveMessage("");
    setSaveError("");

    try {
      const updatedTicket = await updateTicket(ticketId, patchPayload);
      setTicket(updatedTicket);
      setFormData({
        priority: updatedTicket.priority,
        status: updatedTicket.status,
        assigned_team: updatedTicket.assigned_team,
        resolution_notes: updatedTicket.resolution_notes || "",
      });
      setSaveMessage("Ticket updated successfully.");
    } catch (requestError) {
      setSaveError(requestError.message || "Unable to update ticket.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeleteTicket() {
    if (isDeleting) {
      return;
    }

    const confirmed = window.confirm(
      `Delete ticket ${ticket.ticket_number}?\n\nThis action cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    setIsDeleting(true);
    setDeleteError("");

    try {
      await deleteTicket(ticketId);
      navigate("/tickets");
    } catch (requestError) {
      setDeleteError(requestError.message || "Unable to delete ticket.");
    } finally {
      setIsDeleting(false);
    }
  }

  if (isLoading) {
    return <section className="panel state-message">Loading ticket...</section>;
  }

  if (error) {
    return (
      <section className="panel state-message error-state">
        <p>{error}</p>
        <div className="button-row">
          <button
            className="primary-button"
            onClick={() => setReloadKey((key) => key + 1)}
          >
            Retry
          </button>
          <button
            className="secondary-button"
            onClick={() => navigate("/tickets")}
          >
            Back to Tickets
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <div className="detail-heading">
        <button className="text-button" onClick={() => navigate("/tickets")}>
          Back to Tickets
        </button>
        <div>
          <p className="eyebrow">{ticket.ticket_number}</p>
          <h2>{ticket.title}</h2>
        </div>
      </div>

      <div className="detail-grid">
        <div className="panel detail-panel">
          <p className="panel-label">Request Information</p>
          <dl className="detail-list">
            <div>
              <dt>Description</dt>
              <dd>{ticket.description}</dd>
            </div>
            <div>
              <dt>Requester</dt>
              <dd>{ticket.requester_name}</dd>
            </div>
            <div>
              <dt>Requester Email</dt>
              <dd>{ticket.requester_email}</dd>
            </div>
            <div>
              <dt>Department</dt>
              <dd>{ticket.department}</dd>
            </div>
            <div>
              <dt>Category</dt>
              <dd>{ticket.category}</dd>
            </div>
          </dl>
        </div>

        <div className="panel detail-panel">
          <p className="panel-label">Workflow Information</p>
          <dl className="detail-list compact-detail-list">
            <div>
              <dt>Priority</dt>
              <dd>
                <TicketBadge type="priority" value={ticket.priority} />
              </dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>
                <TicketBadge type="status" value={ticket.status} />
              </dd>
            </div>
            <div>
              <dt>Assigned Team</dt>
              <dd>{ticket.assigned_team}</dd>
            </div>
            <div>
              <dt>Created</dt>
              <dd>{formatDateTime(ticket.created_at)}</dd>
            </div>
            <div>
              <dt>Updated</dt>
              <dd>{formatDateTime(ticket.updated_at)}</dd>
            </div>
            <div>
              <dt>First Response</dt>
              <dd>
                {formatDateTime(ticket.first_response_at, "Not yet responded")}
              </dd>
            </div>
            <div>
              <dt>Resolved</dt>
              <dd>{formatDateTime(ticket.resolved_at, "Not resolved")}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="panel detail-panel">
        <p className="panel-label">Resolution</p>
        <p className="resolution-text">
          {ticket.resolution_notes || "No resolution notes"}
        </p>
      </div>

      <form className="panel form-panel" onSubmit={saveChanges}>
        <div className="form-grid">
          <label className="form-field" htmlFor="detail-priority">
            <span>Priority</span>
            <select
              id="detail-priority"
              name="priority"
              value={formData.priority}
              onChange={updateField}
            >
              {TICKET_PRIORITIES.map((priority) => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field" htmlFor="detail-status">
            <span>Status</span>
            <select
              id="detail-status"
              name="status"
              value={formData.status}
              onChange={updateField}
            >
              {TICKET_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field" htmlFor="detail-assigned-team">
            <span>Assigned Team</span>
            <select
              id="detail-assigned-team"
              name="assigned_team"
              value={formData.assigned_team}
              onChange={updateField}
            >
              {ASSIGNED_TEAMS.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>

          <label
            className="form-field form-field-full"
            htmlFor="detail-resolution-notes"
          >
            <span>Resolution Notes</span>
            <textarea
              id="detail-resolution-notes"
              name="resolution_notes"
              rows="5"
              value={formData.resolution_notes}
              onChange={updateField}
            />
          </label>
        </div>

        {saveMessage ? <div className="form-success">{saveMessage}</div> : null}
        {saveError ? <div className="form-error">{saveError}</div> : null}

        <div className="button-row">
          <button
            className="primary-button"
            type="submit"
            disabled={!hasChanges || isSaving}
          >
            {isSaving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>

      <div className="panel detail-panel destructive-panel">
        <div>
          <p className="panel-label">Destructive Action</p>
          <h3>Delete Ticket</h3>
          <p className="supporting-text">
            Permanently remove {ticket.ticket_number} from the ticket queue.
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
            onClick={handleDeleteTicket}
          >
            {isDeleting ? "Deleting..." : "Delete Ticket"}
          </button>
        </div>
      </div>
    </section>
  );
}

export default TicketDetail;
