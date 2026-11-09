export default function Mascot({
  mood = "idle",
  size = 72,
}: {
  mood?: "idle" | "celebrate" | "nudge";
  size?: number;
}) {
  const cheek = mood === "celebrate" ? "#fb7185" : "#f9a8d4";
  const eyeY = mood === "nudge" ? 38 : 36;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 96 96"
      className={`mascot mascot-${mood}`}
      aria-hidden
    >
      <defs>
        <linearGradient id="mascotBody" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#c4b5fd" />
          <stop offset="100%" stopColor="#8b5cf6" />
        </linearGradient>
      </defs>
      <ellipse cx="48" cy="84" rx="26" ry="6" fill="rgba(109,40,217,0.12)" />
      <circle cx="48" cy="48" r="34" fill="url(#mascotBody)" />
      <circle cx="34" cy="42" r="5" fill="#2e1065" />
      <circle cx="62" cy="42" r="5" fill="#2e1065" />
      <circle cx="35.5" cy={eyeY} r="1.6" fill="#fff" />
      <circle cx="63.5" cy={eyeY} r="1.6" fill="#fff" />
      <circle cx="30" cy="52" r="5" fill={cheek} opacity="0.85" />
      <circle cx="66" cy="52" r="5" fill={cheek} opacity="0.85" />
      {mood === "celebrate" ? (
        <path
          d="M36 58c4 7 20 7 24 0"
          fill="none"
          stroke="#2e1065"
          strokeWidth="3"
          strokeLinecap="round"
        />
      ) : mood === "nudge" ? (
        <path
          d="M38 60c3 3 17 3 20 0"
          fill="none"
          stroke="#2e1065"
          strokeWidth="3"
          strokeLinecap="round"
        />
      ) : (
        <path
          d="M38 58c4 5 16 5 20 0"
          fill="none"
          stroke="#2e1065"
          strokeWidth="3"
          strokeLinecap="round"
        />
      )}
      <circle cx="22" cy="28" r="7" fill="#ddd6fe" />
      <circle cx="74" cy="28" r="7" fill="#ddd6fe" />
    </svg>
  );
}
