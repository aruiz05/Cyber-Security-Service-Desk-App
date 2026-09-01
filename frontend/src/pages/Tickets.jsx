import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import TicketBadge from "../components/TicketBadge.jsx";
import {
  ASSIGNED_TEAMS,
  DEPARTMENTS,
  SORT_OPTIONS,
  TICKET_CATEGORIES,
  TICKET_PRIORITIES,
  TICKET_STATUSES,
  getSortOption,
} from "../constants/tickets.js";
import { getTickets } from "../services/api.js";
import { formatDateTime } from "../utils/format.js";

const initialFilters = {
  status: "",
  category: "",
  priority: "",
  assigned_team: "",
  department: "",
};

function Tickets() {
  const navigate = useNavigate();
  const [ticketsData, setTicketsData] = useState(null);
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [filters, setFilters] = useState(initialFilters);
  const [sortValue, setSortValue] = useState(SORT_OPTIONS[0].value);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  const selectedSort = getSortOption(sortValue);

  const hasActiveFilters = useMemo(
    () =>
      Boolean(
        debouncedSearch ||
          filters.status ||
          filters.category ||
          filters.priority ||
          filters.assigned_team ||
          filters.department,
      ),
    [debouncedSearch, filters],
  );

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
    }, 400);

    return () => window.clearTimeout(timeoutId);
  }, [searchInput]);

  useEffect(() => {
    let isCurrent = true;

    async function loadTickets() {
      setIsLoading(true);
      setError("");

      try {
        const data = await getTickets({
          search: debouncedSearch,
          status: filters.status,
          category: filters.category,
          priority: filters.priority,
          assigned_team: filters.assigned_team,
          department: filters.department,
          sort_by: selectedSort.sort_by,
          sort_order: selectedSort.sort_order,
          page,
          page_size: pageSize,
        });

        if (isCurrent) {
          setTicketsData(data);
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || "Unable to load tickets.");
          setTicketsData(null);
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadTickets();

    return () => {
      isCurrent = false;
    };
  }, [debouncedSearch, filters, page, pageSize, reloadKey, selectedSort]);

  function updateFilter(name, value) {
    setFilters((currentFilters) => ({
      ...currentFilters,
      [name]: value,
    }));
    setPage(1);
  }

  function handleSearchChange(event) {
    setSearchInput(event.target.value);
    setPage(1);
  }

  function handleSortChange(event) {
    setSortValue(event.target.value);
    setPage(1);
  }

  function handlePageSizeChange(event) {
    setPageSize(Number(event.target.value));
    setPage(1);
  }

  function clearFilters() {
    setSearchInput("");
    setDebouncedSearch("");
    setFilters(initialFilters);
    setSortValue(SORT_OPTIONS[0].value);
    setPage(1);
  }

  function retryLoad() {
    setReloadKey((currentKey) => currentKey + 1);
  }

  function openTicket(ticketId) {
    navigate(`/tickets/${ticketId}`);
  }

  const tickets = ticketsData?.items || [];
  const total = ticketsData?.total || 0;
  const totalPages = ticketsData?.total_pages || 0;
  const rangeStart = total === 0 ? 0 : (ticketsData.page - 1) * pageSize + 1;
  const rangeEnd = Math.min(ticketsData?.page * pageSize || 0, total);

  return (
    <section className="page-stack">
      <div className="section-heading">
        <p className="eyebrow">Ticket Queue</p>
        <h2>Cybersecurity Requests</h2>
      </div>

      <div className="panel ticket-controls">
        <div className="control-field control-field-wide">
          <label htmlFor="ticket-search">Search</label>
          <input
            id="ticket-search"
            type="search"
            placeholder="Search tickets..."
            value={searchInput}
            onChange={handleSearchChange}
          />
        </div>

        <div className="control-field">
          <label htmlFor="status-filter">Status</label>
          <select
            id="status-filter"
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
          <label htmlFor="category-filter">Category</label>
          <select
            id="category-filter"
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
          <label htmlFor="priority-filter">Priority</label>
          <select
            id="priority-filter"
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
          <label htmlFor="team-filter">Assigned Team</label>
          <select
            id="team-filter"
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
          <label htmlFor="department-filter">Department</label>
          <select
            id="department-filter"
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
          <label htmlFor="sort-control">Sort</label>
          <select id="sort-control" value={sortValue} onChange={handleSortChange}>
            {SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <button className="secondary-button control-action" onClick={clearFilters}>
          Clear Filters
        </button>
      </div>

      <div className="panel table-panel">
        {isLoading ? (
          <div className="state-message">Loading tickets...</div>
        ) : error ? (
          <div className="state-message error-state">
            <p>{error || "Unable to load tickets."}</p>
            <button className="primary-button" onClick={retryLoad}>
              Retry
            </button>
          </div>
        ) : tickets.length === 0 ? (
          <div className="state-message">
            {hasActiveFilters
              ? "No tickets match the current filters."
              : "No tickets found."}
          </div>
        ) : (
          <>
            <div className="table-summary">
              Showing {rangeStart}-{rangeEnd} of {total} tickets
            </div>
            <div className="table-scroll">
              <table className="tickets-table">
                <thead>
                  <tr>
                    <th>Ticket</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Assigned Team</th>
                    <th>Requester</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((ticket) => (
                    <tr
                      key={ticket.id}
                      className="clickable-row"
                      tabIndex={0}
                      onClick={() => openTicket(ticket.id)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter") {
                          openTicket(ticket.id);
                        }
                      }}
                    >
                      <td>
                        <button
                          className="ticket-number-button"
                          onClick={(event) => {
                            event.stopPropagation();
                            openTicket(ticket.id);
                          }}
                        >
                          {ticket.ticket_number}
                        </button>
                      </td>
                      <td className="ticket-title-cell">{ticket.title}</td>
                      <td>{ticket.category}</td>
                      <td>
                        <TicketBadge type="priority" value={ticket.priority} />
                      </td>
                      <td>
                        <TicketBadge type="status" value={ticket.status} />
                      </td>
                      <td>{ticket.assigned_team}</td>
                      <td>{ticket.requester_name}</td>
                      <td>{formatDateTime(ticket.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      <div className="pagination-bar">
        <div className="control-field page-size-control">
          <label htmlFor="page-size">Page Size</label>
          <select
            id="page-size"
            value={pageSize}
            onChange={handlePageSizeChange}
          >
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
        </div>

        <div className="pagination-controls">
          <button
            className="secondary-button"
            disabled={page <= 1 || isLoading}
            onClick={() =>
              setPage((currentPage) => Math.max(currentPage - 1, 1))
            }
          >
            Previous
          </button>
          <span>
            Page {ticketsData?.page || page} of {totalPages || 1}
          </span>
          <button
            className="secondary-button"
            disabled={page >= totalPages || totalPages === 0 || isLoading}
            onClick={() => setPage((currentPage) => currentPage + 1)}
          >
            Next
          </button>
        </div>
      </div>
    </section>
  );
}

export default Tickets;
