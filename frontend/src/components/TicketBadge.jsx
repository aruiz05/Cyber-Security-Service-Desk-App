function getBadgeClass(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function TicketBadge({ type, value }) {
  return (
    <span className={`ticket-badge badge-${type} badge-${getBadgeClass(value)}`}>
      {value}
    </span>
  );
}

export default TicketBadge;
