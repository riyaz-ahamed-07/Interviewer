import type { ReactNode } from "react";

export default function CapsuleTodo({
  checked,
  onChange,
  lane = "practice",
  optional,
  children,
}: {
  checked: boolean;
  onChange: () => void;
  lane?: "practice" | "concept";
  optional?: boolean;
  children: ReactNode;
}) {
  return (
    <label
      className={`day-todo-capsule lane-${lane}${checked ? " done" : ""}${optional ? " optional" : ""}`}
    >
      <input type="checkbox" checked={checked} onChange={onChange} />
      <span className="day-todo-radio" aria-hidden>
        {checked ? (
          <svg viewBox="0 0 12 9" width="11" height="8">
            <path
              d="M1 4.2L4 7L11 1"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        ) : null}
      </span>
      <span className="day-todo-text">{children}</span>
    </label>
  );
}
