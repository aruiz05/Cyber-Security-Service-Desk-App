function ChartCard({ title, action, children, emptyMessage, isEmpty = false }) {
  return (
    <section className="panel chart-card">
      <div className="chart-card-header">
        <h3>{title}</h3>
        {action ? <div className="chart-card-action">{action}</div> : null}
      </div>

      {isEmpty ? (
        <div className="empty-chart-message">
          {emptyMessage || "No ticket data available."}
        </div>
      ) : (
        children
      )}
    </section>
  );
}

export default ChartCard;
