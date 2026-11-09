import { useEffect } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import NavBar from "./components/NavBar";
import BottomNav from "./components/ui/BottomNav";
import History from "./pages/History";
import InterviewRoom from "./pages/InterviewRoom";
import Landing from "./pages/Landing";
import MasterList from "./pages/MasterList";
import PaperBuddy from "./pages/PaperBuddy";
import PaperLibrary from "./pages/PaperLibrary";
import Report from "./pages/Report";
import Setup from "./pages/Setup";
import ForgeDay from "./pages/ForgeDay";
import ForgeStats from "./pages/ForgeStats";
import ForgeCalendar from "./pages/ForgeCalendar";
import Onboarding, { needsOnboarding } from "./pages/Onboarding";
import Settings from "./pages/Settings";

function OnboardGate() {
  const nav = useNavigate();
  const loc = useLocation();
  useEffect(() => {
    if (needsOnboarding() && loc.pathname !== "/onboarding") {
      nav("/onboarding", { replace: true });
    }
  }, [loc.pathname, nav]);
  return null;
}

function AppShell() {
  return (
    <div className="app-shell">
      <OnboardGate />
      <NavBar />
      <Outlet />
      <BottomNav />
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
          <Route path="/forge/list" element={<MasterList />} />
          <Route path="/forge/day/:dateKey" element={<ForgeDay />} />
          <Route path="/forge/stats" element={<ForgeStats />} />
          <Route path="/forge/calendar" element={<ForgeCalendar />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/settings" element={<Settings />} />
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
