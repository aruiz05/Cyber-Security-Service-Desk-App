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
  const pageTitle = location.pathname.startsWith("/tickets/")
    ? "Ticket Detail"
    : pageTitles[location.pathname] || "Dashboard";

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
