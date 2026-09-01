import { useEffect, useState } from "react";

import { API_BASE_URL, checkHealth } from "../services/api.js";

const statusLabels = {
  checking: "Checking API connection...",
  connected: "Connected",
  unavailable: "Unavailable",
};

function Dashboard() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    let isCurrent = true;

    async function loadHealthStatus() {
      setApiStatus("checking");

      try {
        await checkHealth();
        if (isCurrent) {
          setApiStatus("connected");
        }
      } catch (error) {
        console.error("Backend health check failed:", error);
        if (isCurrent) {
          setApiStatus("unavailable");
        }
      }
    }

    loadHealthStatus();

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <section className="page-stack">
      <div className="section-heading">
        <p className="eyebrow">Operations Overview</p>
        <h2>Cybersecurity Awareness Service Desk</h2>
      </div>

      <div className="panel status-panel">
        <div>
          <p className="panel-label">System Status</p>
          <h3>Backend API</h3>
          <p className="supporting-text">{API_BASE_URL}</p>
        </div>

        <div className={`status-badge status-${apiStatus}`}>
          <span className="status-dot" />
          <span>
            {apiStatus === "checking"
              ? statusLabels.checking
              : `Backend API: ${statusLabels[apiStatus]}`}
          </span>
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
