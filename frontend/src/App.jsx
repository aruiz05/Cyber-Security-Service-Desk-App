import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import KnowledgeArticle from "./pages/KnowledgeArticle.jsx";
import KnowledgeBase from "./pages/KnowledgeBase.jsx";
import Reports from "./pages/Reports.jsx";
import SubmitRequest from "./pages/SubmitRequest.jsx";
import TicketDetail from "./pages/TicketDetail.jsx";
import Tickets from "./pages/Tickets.jsx";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/tickets" element={<Tickets />} />
        <Route path="/tickets/:ticketId" element={<TicketDetail />} />
        <Route path="/submit" element={<SubmitRequest />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/knowledge/:articleId" element={<KnowledgeArticle />} />
        <Route path="/reports" element={<Reports />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
