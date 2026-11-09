import { NavLink } from "react-router-dom";
import { BookOpen, CalendarDays, Home, Sparkles, UserRound } from "lucide-react";

export default function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Primary">
      <NavLink to="/" end>
        <Home size={18} />
        <span>Home</span>
      </NavLink>
      <NavLink to="/forge/calendar">
        <CalendarDays size={18} />
        <span>Plan</span>
      </NavLink>
      <NavLink to="/forge/list">
        <BookOpen size={18} />
        <span>List</span>
      </NavLink>
      <NavLink to="/buddies/paper">
        <Sparkles size={18} />
        <span>Buddy</span>
      </NavLink>
      <NavLink to="/settings">
        <UserRound size={18} />
        <span>You</span>
      </NavLink>
    </nav>
  );
}
