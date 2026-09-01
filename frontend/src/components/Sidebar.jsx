import { NavLink } from "react-router-dom";

const navigationItems = [
  { to: "/", label: "Dashboard" },
  { to: "/tickets", label: "Tickets" },
  { to: "/submit", label: "Submit Request" },
  { to: "/knowledge", label: "Knowledge Base" },
  { to: "/reports", label: "Reports" },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-kicker">Cybersecurity Awareness</span>
        <span className="brand-name">Service Desk</span>
      </div>

      <nav className="sidebar-nav" aria-label="Main navigation">
        {navigationItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
