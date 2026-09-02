import { useEffect, useMemo, useState } from "react";

import MetricCard from "../components/MetricCard.jsx";
import {
  ASSIGNED_TEAMS,
  DEPARTMENTS,
  TICKET_CATEGORIES,
  TICKET_PRIORITIES,
  TICKET_STATUSES,
} from "../constants/tickets.js";
import { downloadTicketReport, getAnalyticsSummary } from "../services/api.js";

const initialReportFilters = {
  status: "",
  category: "",
  priority: "",
  assigned_team: "",
  department: "",
  start_date: "",
  end_date: "",
};

const filterLabels = {
  status: "Status",
  category: "Category",
  priority: "Priority",
  assigned_team: "Assigned Team",
  department: "Department",
  start_date: "Start Date",
  end_date: "End Date",
};

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }

  return new Intl.NumberFormat().format(value);
}

function formatPercentage(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }

  return `${Number(value).toFixed(1)}%`;
}

function Reports() {
  const [summary, setSummary] = useState(null);
  const [filters, setFilters] = useState(initialReportFilters);
  const [isSummaryLoading, setIsSummaryLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [summaryError, setSummaryError] = useState("");
  const [downloadError, setDownloadError] = useState("");
  const [downloadMessage, setDownloadMessage] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  const activeFilters = useMemo(
    () =>
      Object.entries(filters)
        .filter(([, value]) => Boolean(value))
        .map(([key, value]) => `${filterLabels[key]}: ${value}`),
    [filters],
  );

  useEffect(() => {
    let isCurrent = true;

    async function loadSummary() {
      setIsSummaryLoading(true);
      setSummaryError("");

      try {
        const summaryData = await getAnalyticsSummary();

        if (isCurrent) {
          setSummary(summaryData);
        }
      } catch (requestError) {
        if (isCurrent) {
          setSummaryError(requestError.message || "Unable to load report summary.");
          setSummary(null);
        }
      } finally {
        if (isCurrent) {
          setIsSummaryLoading(false);
        }
      }
    }

    loadSummary();

    return () => {
      isCurrent = false;
    };
  }, [reloadKey]);

  function updateFilter(name, value) {
    setFilters((currentFilters) => ({
      ...currentFilters,
      [name]: value,
    }));
    setDownloadError("");
    setDownloadMessage("");
  }

  function clearFilters() {
    setFilters(initialReportFilters);
    setDownloadError("");
    setDownloadMessage("");
  }

  async function handleDownloadReport() {
    if (isDownloading) {
      return;
    }

    setIsDownloading(true);
    setDownloadError("");
    setDownloadMessage("");

    try {
      const result = await downloadTicketReport(filters);
      setDownloadMessage(`Downloaded ${result.filename}.`);
    } catch (requestError) {
      setDownloadError(requestError.message || "Unable to download report.");
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <section className="page-stack">
      <div className="section-heading">
        <p className="eyebrow">Reporting</p>
        <h2>Ticket Reports</h2>
        <p className="supporting-text">
          Export service-desk tickets to CSV using the current report filters.
        </p>
      </div>

      {summaryError ? (
        <section className="panel state-message error-state">
          <p>{summaryError}</p>
          <button
            className="primary-button"
            type="button"
            onClick={() => setReloadKey((key) => key + 1)}
          >
            Retry
          </button>
        </section>
      ) : (
        <div className="metrics-grid">
          <MetricCard
            label="Total Tickets"
            value={isSummaryLoading ? "--" : formatNumber(summary?.total_tickets)}
            helper="All service-desk records"
          />
          <MetricCard
            label="Open Tickets"
            value={isSummaryLoading ? "--" : formatNumber(summary?.open_tickets)}
            helper="New, in progress, or waiting"
          />
          <MetricCard
            label="Completed"
            value={
              isSummaryLoading ? "--" : formatNumber(summary?.completed_tickets)
            }
            helper="Resolved or closed tickets"
          />
          <MetricCard
            label="SLA Compliance"
            value={
              isSummaryLoading
                ? "--"
                : formatPercentage(summary?.sla_compliance_percentage)
            }
            helper="First-response performance"
          />
        </div>
      )}

      <div className="panel report-controls">
        <div className="control-field">
          <label htmlFor="report-status">Status</label>
          <select
            id="report-status"
            value={filters.status}
            onChange={(event) => updateFilter("status", event.target.value)}
          >
            <option value="">All Statuses</option>
            {TICKET_STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div className="control-field">
          <label htmlFor="report-category">Category</label>
          <select
            id="report-category"
            value={filters.category}
            onChange={(event) => updateFilter("category", event.target.value)}
          >
            <option value="">All Categories</option>
            {TICKET_CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <div className="control-field">
          <label htmlFor="report-priority">Priority</label>
          <select
            id="report-priority"
            value={filters.priority}
            onChange={(event) => updateFilter("priority", event.target.value)}
          >
            <option value="">All Priorities</option>
            {TICKET_PRIORITIES.map((priority) => (
              <option key={priority} value={priority}>
                {priority}
              </option>
            ))}
          </select>
        </div>

        <div className="control-field">
          <label htmlFor="report-team">Assigned Team</label>
          <select
            id="report-team"
            value={filters.assigned_team}
            onChange={(event) =>
              updateFilter("assigned_team", event.target.value)
            }
          >
            <option value="">All Teams</option>
            {ASSIGNED_TEAMS.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>
        </div>

        <div className="control-field">
          <label htmlFor="report-department">Department</label>
          <select
            id="report-department"
            value={filters.department}
            onChange={(event) => updateFilter("department", event.target.value)}
          >
            <option value="">All Departments</option>
            {DEPARTMENTS.map((department) => (
              <option key={department} value={department}>
                {department}
              </option>
            ))}
          </select>
        </div>

        <div className="control-field">
          <label htmlFor="report-start-date">Start Date</label>
          <input
            id="report-start-date"
            type="date"
            value={filters.start_date}
            onChange={(event) => updateFilter("start_date", event.target.value)}
          />
        </div>

        <div className="control-field">
          <label htmlFor="report-end-date">End Date</label>
          <input
            id="report-end-date"
            type="date"
            value={filters.end_date}
            onChange={(event) => updateFilter("end_date", event.target.value)}
          />
        </div>

        <div className="report-actions">
          <button
            className="primary-button"
            type="button"
            disabled={isDownloading}
            onClick={handleDownloadReport}
          >
            {isDownloading ? "Downloading..." : "Download CSV"}
          </button>
          <button className="secondary-button" type="button" onClick={clearFilters}>
            Clear Filters
          </button>
        </div>
      </div>

      <section className="panel report-export-panel">
        <p className="panel-label">Export Scope</p>
        <p>
          {activeFilters.length
            ? activeFilters.join(" | ")
            : "All tickets will be included."}
        </p>

        {downloadMessage ? (
          <div className="form-success">{downloadMessage}</div>
        ) : null}
        {downloadError ? <div className="form-error">{downloadError}</div> : null}
      </section>
    </section>
  );
}

export default Reports;
