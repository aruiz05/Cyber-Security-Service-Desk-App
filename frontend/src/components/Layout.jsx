import { Outlet, useLocation } from "react-router-dom";

import Header from "./Header.jsx";
import Sidebar from "./Sidebar.jsx";

const pageTitles = {
  "/": "Dashboard",
  "/tickets": "Tickets",
  "/submit": "Submit Request",
  "/knowledge": "Knowledge Base",
  "/reports": "Reports",
};

function Layout() {
  const location = useLocation();
  let pageTitle = pageTitles[location.pathname] || "Dashboard";

  if (location.pathname.startsWith("/tickets/")) {
    pageTitle = "Ticket Detail";
  }

  if (location.pathname.startsWith("/knowledge/")) {
    pageTitle = "Knowledge Article";
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="content-shell">
        <Header pageTitle={pageTitle} />
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
