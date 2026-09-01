import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import KnowledgeBase from "./pages/KnowledgeBase.jsx";
import Reports from "./pages/Reports.jsx";
import SubmitRequest from "./pages/SubmitRequest.jsx";
import Tickets from "./pages/Tickets.jsx";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/tickets" element={<Tickets />} />
        <Route path="/submit" element={<SubmitRequest />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/reports" element={<Reports />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
