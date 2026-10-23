/** Pull a short topic cue from an interviewer question (LLM phase card). */
export function extractTopicCue(text: string): string | null {
  const raw = text.replace(/\s+/g, " ").trim();
  if (!raw || raw.length < 8) return null;

  const patterns = [
    /next topic:\s*(.+?)(?:[.?!]|$)/i,
    /(?:please\s+)?define\s+(.+?)(?:[.?!]|$)/i,
    /what(?:'s|\s+is|\s+are)\s+(.+?)(?:[.?!]|$)/i,
    /explain\s+(.+?)(?:[.?!]|$)/i,
    /(?:describe|contrast|compare)\s+(.+?)(?:[.?!]|$)/i,
    /(?:how does|how do|when do you|when would you)\s+(.+?)(?:[.?!]|$)/i,
  ];

  for (const re of patterns) {
    const m = raw.match(re);
    if (m?.[1]) {
      const cue = cleanCue(m[1]);
      if (cue) return cue;
    }
  }
  return null;
}

function cleanCue(s: string): string {
  let out = s.trim();
  out = out.replace(
    /^(please\s+)?(define|explain|describe|contrast|compare)\s+/i,
    "",
  );
  out = out.replace(/^(the|a|an)\s+/i, "");
  out = out.replace(/\s+in one (?:line|sentence|word).*$/i, "");
  out = out.replace(/\s+briefly.*$/i, "");
  out = out.replace(/^["'“”]+|["'“”]+$/g, "");
  out = out.replace(/[.?!,:;]+$/g, "").trim();
  if (out.length < 3 || out.length > 120) return "";
  if (/^(you define it|i'?m asking you|your turn)/i.test(out)) return "";
  return out;
}

export function latestTopicCue(
  messages: { role: string; content: string }[],
  liveAssistantPartial = "",
): string | null {
  if (liveAssistantPartial.trim()) {
    const live = extractTopicCue(liveAssistantPartial);
    if (live) return live;
  }
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (m.role !== "assistant") continue;
    const cue = extractTopicCue(m.content);
    if (cue) return cue;
  }
  return null;
}
