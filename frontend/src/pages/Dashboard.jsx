import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import ChartCard from "../components/ChartCard.jsx";
import MetricCard from "../components/MetricCard.jsx";
import {
  checkHealth,
  getAnalyticsSummary,
  getCategoryAnalytics,
  getPriorityAnalytics,
  getSLAAnalytics,
  getStatusAnalytics,
  getTrends,
} from "../services/api.js";

const trendRangeOptions = [
  { label: "7 Days", value: 7 },
  { label: "30 Days", value: 30 },
  { label: "90 Days", value: 90 },
];

const chartColors = {
  created: "#176457",
  resolved: "#85580e",
  category: "#2f9e8f",
  status: ["#2d528f", "#8a5d12", "#624192", "#176457", "#46535d"],
  priority: {
    Critical: "#9b2f24",
    High: "#85580e",
    Medium: "#2d528f",
    Low: "#176457",
  },
  sla: {
    Met: "#176457",
    Breached: "#9b2f24",
    Pending: "#8a5d12",
  },
};

function hasCountData(items, key = "count") {
  return items.some((item) => Number(item[key]) > 0);
}

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }

  return new Intl.NumberFormat().format(value);
}

function formatDecimal(value, suffix) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }

  return `${Number(value).toFixed(1)}${suffix}`;
}

function formatMinutes(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }

  if (Number(value) < 60) {
    return `${Number(value).toFixed(1)} min`;
  }

  const hours = Math.floor(Number(value) / 60);
  const minutes = Math.round(Number(value) % 60);

  return minutes ? `${hours} hr ${minutes} min` : `${hours} hr`;
}

function formatHours(value) {
  return formatDecimal(value, " hr");
}

function formatPercentage(value) {
  return formatDecimal(value, "%");
}

function formatSlaTarget(minutes) {
  if (minutes === null || minutes === undefined || Number.isNaN(Number(minutes))) {
    return "--";
  }

  const targetMinutes = Number(minutes);

  if (targetMinutes < 60) {
    return `${targetMinutes} min`;
  }

  const hours = targetMinutes / 60;
  return Number.isInteger(hours) ? `${hours} hr` : `${hours.toFixed(1)} hr`;
}

function getLocalDate(dateString) {
  const [year, month, day] = dateString.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function formatShortDate(dateString) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
  }).format(getLocalDate(dateString));
}

function formatLongDate(dateString) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(getLocalDate(dateString));
}

function AnalyticsTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  const displayLabel = payload[0]?.payload?.fullDate || label;

  return (
    <div className="chart-tooltip">
      <p>{displayLabel}</p>
      {payload.map((item) => (
        <div key={item.name} className="chart-tooltip-row">
          <span
            className="chart-tooltip-dot"
            style={{ background: item.color }}
          />
          <span>
            {item.name}: {formatNumber(item.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

function Dashboard() {
  const [dashboardData, setDashboardData] = useState({
    summary: null,
    categories: [],
    statuses: [],
    priorities: [],
    sla: null,
  });
  const [trends, setTrends] = useState([]);
  const [trendDays, setTrendDays] = useState(30);
  const [connectionStatus, setConnectionStatus] = useState("checking");
  const [isDashboardLoading, setIsDashboardLoading] = useState(true);
  const [isTrendLoading, setIsTrendLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");
  const [trendError, setTrendError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let isCurrent = true;

    async function loadDashboardData() {
      setIsDashboardLoading(true);
      setDashboardError("");
      setConnectionStatus("checking");

      try {
        await checkHealth();
        const [summary, categories, statuses, priorities, sla] =
          await Promise.all([
            getAnalyticsSummary(),
            getCategoryAnalytics(),
            getStatusAnalytics(),
            getPriorityAnalytics(),
            getSLAAnalytics(),
          ]);

        if (isCurrent) {
          setDashboardData({
            summary,
            categories,
            statuses,
            priorities,
            sla,
          });
          setConnectionStatus("connected");
        }
      } catch (error) {
        if (isCurrent) {
          setDashboardError(error.message || "Unable to load dashboard analytics.");
          setConnectionStatus("unavailable");
        }
      } finally {
        if (isCurrent) {
          setIsDashboardLoading(false);
        }
      }
    }

    loadDashboardData();

    return () => {
      isCurrent = false;
    };
  }, [reloadKey]);

  useEffect(() => {
    let isCurrent = true;

    async function loadTrendData() {
      setIsTrendLoading(true);
      setTrendError("");

      try {
        const trendData = await getTrends(trendDays);

        if (isCurrent) {
          setTrends(trendData);
        }
      } catch (error) {
        if (isCurrent) {
          setTrendError(error.message || "Unable to load ticket trends.");
          setTrends([]);
        }
      } finally {
        if (isCurrent) {
          setIsTrendLoading(false);
        }
      }
    }

    loadTrendData();

    return () => {
      isCurrent = false;
    };
  }, [trendDays, reloadKey]);

  const trendChartData = useMemo(
    () =>
      trends.map((point) => ({
        ...point,
        label: formatShortDate(point.date),
        fullDate: formatLongDate(point.date),
      })),
    [trends],
  );

  const categoryChartData = dashboardData.categories.map((item) => ({
    name: item.category,
    count: item.count,
  }));

  const statusChartData = dashboardData.statuses.map((item) => ({
    name: item.status,
    count: item.count,
  }));

  const priorityChartData = dashboardData.priorities.map((item) => ({
    name: item.priority,
    count: item.count,
  }));

  const slaChartData = dashboardData.sla
    ? [
        { name: "Met", value: dashboardData.sla.met },
        { name: "Breached", value: dashboardData.sla.breached },
        { name: "Pending", value: dashboardData.sla.pending },
      ]
    : [];

  const hasTrendData = trendChartData.some(
    (point) => Number(point.created) > 0 || Number(point.resolved) > 0,
  );
  const hasSlaData = hasCountData(slaChartData, "value");

  function retryDashboard() {
    setReloadKey((currentKey) => currentKey + 1);
  }

  if (isDashboardLoading && !dashboardData.summary) {
    return <section className="panel state-message">Loading dashboard...</section>;
  }

  if (dashboardError) {
    return (
      <section className="panel state-message error-state">
        <p>Unable to load dashboard analytics.</p>
        <p>{dashboardError}</p>
        <button className="primary-button" onClick={retryDashboard}>
          Retry
        </button>
      </section>
    );
  }

  const { summary, sla } = dashboardData;

  return (
    <section className="page-stack dashboard-stack">
      <div className="dashboard-heading">
        <div className="section-heading">
          <p className="eyebrow">Operations Overview</p>
          <h2>Cybersecurity Service Desk Dashboard</h2>
          <p className="supporting-text">
            Overview of cybersecurity requests, service performance, and SLA
            compliance.
          </p>
        </div>

        <div className={`connection-pill connection-${connectionStatus}`}>
          <span className="status-dot" />
          <span>
            Backend API:{" "}
            {connectionStatus === "connected" ? "Connected" : "Unavailable"}
          </span>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Total Tickets" value={formatNumber(summary.total_tickets)} />
        <MetricCard label="Open Tickets" value={formatNumber(summary.open_tickets)} />
        <MetricCard
          label="Completed Tickets"
          value={formatNumber(summary.completed_tickets)}
        />
        <MetricCard
          label="Created Today"
          value={formatNumber(summary.tickets_created_today)}
        />
        <MetricCard
          label="Resolved This Week"
          value={formatNumber(summary.tickets_resolved_this_week)}
        />
        <MetricCard
          label="Avg First Response"
          value={formatMinutes(summary.average_response_time_minutes)}
        />
        <MetricCard
          label="Avg Resolution Time"
          value={formatHours(summary.average_resolution_time_hours)}
        />
        <MetricCard
          label="SLA Compliance"
          value={formatPercentage(summary.sla_compliance_percentage)}
        />
      </div>

      <ChartCard
        title="Ticket Creation and Resolution Trends"
        action={
          <label className="range-control" htmlFor="trend-range">
            <span>Range</span>
            <select
              id="trend-range"
              value={trendDays}
              onChange={(event) => setTrendDays(Number(event.target.value))}
            >
              {trendRangeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        }
        isEmpty={!isTrendLoading && !trendError && !hasTrendData}
        emptyMessage="No ticket trend data available."
      >
        {isTrendLoading ? (
          <div className="empty-chart-message">Loading trend data...</div>
        ) : trendError ? (
          <div className="empty-chart-message error-state">{trendError}</div>
        ) : (
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendChartData} margin={{ top: 8, right: 18, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="#e5ebef" strokeDasharray="3 3" />
                <XAxis dataKey="label" tickLine={false} />
                <YAxis allowDecimals={false} tickLine={false} width={36} />
                <Tooltip content={<AnalyticsTooltip />} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="created"
                  name="Created"
                  stroke={chartColors.created}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 5 }}
                />
                <Line
                  type="monotone"
                  dataKey="resolved"
                  name="Resolved"
                  stroke={chartColors.resolved}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </ChartCard>

      <div className="dashboard-grid">
        <ChartCard
          title="Tickets by Category"
          isEmpty={!hasCountData(categoryChartData)}
        >
          <div className="chart-area tall-chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={categoryChartData}
                layout="vertical"
                margin={{ top: 8, right: 18, left: 12, bottom: 0 }}
              >
                <CartesianGrid stroke="#e5ebef" strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} tickLine={false} />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={150}
                  tickLine={false}
                />
                <Tooltip content={<AnalyticsTooltip />} />
                <Bar dataKey="count" name="Tickets" fill={chartColors.category} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Tickets by Status" isEmpty={!hasCountData(statusChartData)}>
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusChartData}
                  dataKey="count"
                  nameKey="name"
                  innerRadius={58}
                  outerRadius={92}
                  paddingAngle={2}
                >
                  {statusChartData.map((entry, index) => (
                    <Cell
                      key={entry.name}
                      fill={chartColors.status[index % chartColors.status.length]}
                    />
                  ))}
                </Pie>
                <Tooltip content={<AnalyticsTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      <div className="dashboard-grid">
        <ChartCard
          title="Tickets by Priority"
          isEmpty={!hasCountData(priorityChartData)}
        >
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priorityChartData} margin={{ top: 8, right: 18, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="#e5ebef" strokeDasharray="3 3" />
                <XAxis dataKey="name" tickLine={false} />
                <YAxis allowDecimals={false} tickLine={false} width={36} />
                <Tooltip content={<AnalyticsTooltip />} />
                <Bar dataKey="count" name="Tickets">
                  {priorityChartData.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={chartColors.priority[entry.name] || chartColors.category}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="SLA Outcome">
          <div className="sla-overview">
            {hasSlaData ? (
              <div className="chart-area compact-chart-area">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={slaChartData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={56}
                      outerRadius={88}
                      paddingAngle={2}
                    >
                      {slaChartData.map((entry) => (
                        <Cell
                          key={entry.name}
                          fill={chartColors.sla[entry.name] || chartColors.category}
                        />
                      ))}
                    </Pie>
                    <Tooltip content={<AnalyticsTooltip />} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="empty-chart-message compact-empty-message">
                No SLA data available.
              </div>
            )}

            <dl className="sla-counts">
              <div>
                <dt>Met</dt>
                <dd>{formatNumber(sla.met)}</dd>
              </div>
              <div>
                <dt>Breached</dt>
                <dd>{formatNumber(sla.breached)}</dd>
              </div>
              <div>
                <dt>Pending</dt>
                <dd>{formatNumber(sla.pending)}</dd>
              </div>
              <div>
                <dt>Compliance</dt>
                <dd>{formatPercentage(sla.compliance_percentage)}</dd>
              </div>
            </dl>
          </div>
        </ChartCard>
      </div>

      <section className="panel sla-priority-panel">
        <div className="chart-card-header">
          <h3>SLA Performance by Priority</h3>
        </div>

        <div className="sla-priority-table-wrap">
          <table className="sla-priority-table">
            <thead>
              <tr>
                <th>Priority</th>
                <th>SLA Target</th>
                <th>Met</th>
                <th>Breached</th>
                <th>Pending</th>
                <th>Compliance</th>
              </tr>
            </thead>
            <tbody>
              {sla.by_priority.map((item) => (
                <tr key={item.priority}>
                  <td>{item.priority}</td>
                  <td>{formatSlaTarget(item.target_minutes)}</td>
                  <td>{formatNumber(item.met)}</td>
                  <td>{formatNumber(item.breached)}</td>
                  <td>{formatNumber(item.pending)}</td>
                  <td>{formatPercentage(item.compliance_percentage)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

export default Dashboard;
