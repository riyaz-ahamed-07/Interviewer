import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar";
import History from "./pages/History";
import InterviewRoom from "./pages/InterviewRoom";
import Landing from "./pages/Landing";
import PaperBuddy from "./pages/PaperBuddy";
import PaperLibrary from "./pages/PaperLibrary";
import Report from "./pages/Report";
import Setup from "./pages/Setup";
import "./App.css";

function AppShell() {
  return (
    <div className="app-shell">
      <NavBar />
      <Outlet />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Landing />} />
          <Route path="/setup" element={<Setup />} />
          <Route path="/report/:sessionId" element={<Report />} />
          <Route path="/history" element={<History />} />
          <Route
            path="/forge"
            element={<Navigate to={{ pathname: "/", hash: "forge" }} replace />}
          />
          <Route path="/buddies/paper" element={<PaperLibrary />} />
          <Route
            path="/buddies/friend"
            element={<Navigate to="/setup" replace />}
          />
          <Route
            path="/buddies/design-teacher"
            element={<Navigate to="/" replace />}
          />
        </Route>
        <Route path="/interview/:sessionId" element={<InterviewRoom />} />
        <Route path="/buddies/paper/:paperId" element={<PaperBuddy />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
