function MetricCard({ label, value, helper }) {
  return (
    <div className="metric-card">
      <p className="metric-label">{label}</p>
      <p className="metric-value">{value}</p>
      {helper ? <p className="metric-helper">{helper}</p> : null}
    </div>
  );
}

export default MetricCard;
