import { PILLARS, allLeaves, findNode, countLeaves } from "./curriculum";
import type {
  DailyQuest,
  DayLog,
  ForgeStore,
  NodeState,
  ProgressMap,
  WeekSlot,
} from "./types";

const KEY = "interviewer.forge.v1";

export const LEVELS = [
  { level: 1, xp: 0, title: "Spark" },
  { level: 2, xp: 120, title: "Builder" },
  { level: 3, xp: 350, title: "Engineer" },
  { level: 4, xp: 700, title: "Systems mind" },
  { level: 5, xp: 1200, title: "Inference craft" },
  { level: 6, xp: 1900, title: "Paper blooded" },
  { level: 7, xp: 2800, title: "Off-campus weapon" },
  { level: 8, xp: 4000, title: "NVIDIA-ready" },
  { level: 9, xp: 5500, title: "Invincible" },
];

export function todayKey(d = new Date()): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function weekKey(d = new Date()): string {
  const tmp = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const dayNum = tmp.getUTCDay() || 7;
  tmp.setUTCDate(tmp.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil(
    ((tmp.getTime() - yearStart.getTime()) / 86400000 + 1) / 7,
  );
  return `${tmp.getUTCFullYear()}-W${String(weekNo).padStart(2, "0")}`;
}

function emptyStore(): ForgeStore {
  return {
    version: 1,
    startedAt: new Date().toISOString(),
    progress: {},
    xp: 0,
    streak: 0,
    bestStreak: 0,
    lastActiveDate: null,
    freezeLeft: 2,
    days: {},
    paperWeek: null,
    focusPillarId: "math",
    levelCelebrated: 1,
  };
}

export function loadStore(): ForgeStore {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return emptyStore();
    const parsed = JSON.parse(raw) as ForgeStore;
    if (parsed.version !== 1) return emptyStore();
    return { ...emptyStore(), ...parsed };
  } catch {
    return emptyStore();
  }
}

export function saveStore(store: ForgeStore) {
  localStorage.setItem(KEY, JSON.stringify(store));
  window.dispatchEvent(new Event("forge-progress"));
}

export function levelForXp(xp: number) {
  let cur = LEVELS[0];
  for (const L of LEVELS) {
    if (xp >= L.xp) cur = L;
  }
  const next = LEVELS.find((L) => L.level === cur.level + 1);
  return {
    ...cur,
    nextXp: next?.xp ?? cur.xp,
    progress: next && next.xp > cur.xp ? (xp - cur.xp) / (next.xp - cur.xp) : 1,
  };
}

function dayBefore(key: string): string {
  const [y, m, d] = key.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() - 1);
  return todayKey(dt);
}

export function touchStreak(store: ForgeStore, date = todayKey()): ForgeStore {
  if (store.lastActiveDate === date) return store;
  const prev = store.lastActiveDate;
  let streak = store.streak;
  let freezeLeft = store.freezeLeft;
  if (!prev) {
    streak = 1;
  } else if (prev === dayBefore(date)) {
    streak += 1;
  } else if (freezeLeft > 0 && prev === dayBefore(dayBefore(date))) {
    freezeLeft -= 1;
    streak += 1;
  } else {
    streak = 1;
  }
  return {
    ...store,
    streak,
    bestStreak: Math.max(store.bestStreak, streak),
    lastActiveDate: date,
    freezeLeft,
  };
}

export function setNodeState(
  store: ForgeStore,
  id: string,
  state: NodeState,
): ForgeStore {
  const prev = store.progress[id] ?? "todo";
  if (prev === state) return store;
  const node = findNode(id)?.node;
  const leafXp = node?.xp ?? 12;
  let xpDelta = 0;
  if (state === "learning" && prev === "todo")
    xpDelta = Math.floor(leafXp * 0.25);
  if (state === "done" && prev !== "done" && prev !== "mastered")
    xpDelta = leafXp;
  if (state === "mastered" && prev !== "mastered")
    xpDelta =
      prev === "done" ? Math.floor(leafXp * 0.5) : Math.floor(leafXp * 1.5);
  if (
    (prev === "done" || prev === "mastered") &&
    (state === "todo" || state === "learning")
  )
    xpDelta = -Math.floor(leafXp * (prev === "mastered" ? 1.5 : 1));

  const date = todayKey();
  const day: DayLog = store.days[date] ?? {
    date,
    xp: 0,
    checked: [],
    questIds: [],
  };
  const checked =
    state === "done" || state === "mastered"
      ? Array.from(new Set([...day.checked, id]))
      : day.checked.filter((x) => x !== id);

  let next = touchStreak(
    {
      ...store,
      progress: { ...store.progress, [id]: state },
      xp: Math.max(0, store.xp + xpDelta),
      days: {
        ...store.days,
        [date]: { ...day, xp: day.xp + Math.max(0, xpDelta), checked },
      },
    },
    date,
  );
  return next;
}

export function pillarStats(progress: ProgressMap, pillarId: string) {
  const pillar = PILLARS.find((p) => p.id === pillarId);
  if (!pillar) return { total: 0, done: 0, mastered: 0, learning: 0 };
  const total = countLeaves(pillar.roots);
  let done = 0;
  let mastered = 0;
  let learning = 0;
  const walk = (nodes: typeof pillar.roots) => {
    for (const n of nodes) {
      if (!n.children?.length) {
        const s = progress[n.id] ?? "todo";
        if (s === "done") done += 1;
        if (s === "mastered") {
          mastered += 1;
          done += 1;
        }
        if (s === "learning") learning += 1;
      } else walk(n.children);
    }
  };
  walk(pillar.roots);
  return { total, done, mastered, learning };
}

export function overallStats(progress: ProgressMap) {
  const leaves = allLeaves();
  let done = 0;
  let mastered = 0;
  for (const leaf of leaves) {
    const s = progress[leaf.id] ?? "todo";
    if (s === "done" || s === "mastered") done += 1;
    if (s === "mastered") mastered += 1;
  }
  return { total: leaves.length, done, mastered };
}

const WEEKDAY_THEMES: Record<
  number,
  { theme: string; pillarIds: string[]; hours: number }
> = {
  1: { theme: "Math · Classical ML", pillarIds: ["math", "ml"], hours: 3 },
  2: { theme: "Deep Learning · PyTorch", pillarIds: ["dl"], hours: 3 },
  3: { theme: "Systems · Inference", pillarIds: ["systems", "llm"], hours: 3 },
  4: {
    theme: "Paper · Concept extract",
    pillarIds: ["papers", "llm"],
    hours: 3,
  },
  5: {
    theme: "Build · Implement",
    pillarIds: ["dl", "papers", "mlops"],
    hours: 3,
  },
  6: {
    theme: "Catch-up · Light DSA/SQL",
    pillarIds: ["dsa", "sql", "corecs"],
    hours: 2,
  },
  0: {
    theme: "Deep work · Review",
    pillarIds: ["math", "dl", "llm", "systems", "career"],
    hours: 5,
  },
};

function unfinishedLeaves(
  progress: ProgressMap,
  pillarIds: string[],
): string[] {
  const ids: string[] = [];
  for (const pid of pillarIds) {
    const pillar = PILLARS.find((p) => p.id === pid);
    if (!pillar) continue;
    const walk = (nodes: typeof pillar.roots) => {
      for (const n of nodes) {
        if (!n.children?.length) {
          const s = progress[n.id] ?? "todo";
          if (s === "todo" || s === "learning") ids.push(n.id);
        } else walk(n.children);
      }
    };
    walk(pillar.roots);
  }
  return ids;
}

export function buildDailyQuests(
  store: ForgeStore,
  date = new Date(),
): DailyQuest[] {
  const key = todayKey(date);
  const dow = date.getDay();
  const theme = WEEKDAY_THEMES[dow];
  const focus = store.focusPillarId
    ? [store.focusPillarId, ...theme.pillarIds]
    : theme.pillarIds;
  const pool = unfinishedLeaves(store.progress, focus);
  const learningFirst = pool.sort((a, b) => {
    const sa = store.progress[a] === "learning" ? 0 : 1;
    const sb = store.progress[b] === "learning" ? 0 : 1;
    return sa - sb;
  });

  const budget = dow === 0 ? 4 : dow === 6 ? 2 : 3;
  const picked = learningFirst.slice(0, budget);
  const quests: DailyQuest[] = picked.map((id) => {
    const hit = findNode(id)!;
    return {
      id,
      title: hit.node.title,
      pillarId: hit.pillar.id,
      path: hit.path,
      xp: hit.node.xp ?? 12,
      kind: hit.pillar.id === "papers" ? "paper" : "concept",
    };
  });

  if (dow === 4 || dow === 0) {
    quests.unshift({
      id: `__paper__${weekKey(date)}`,
      title: store.paperWeek?.title
        ? `Paper: ${store.paperWeek.title}`
        : "Pick this week's research paper",
      pillarId: "papers",
      path: ["Research Papers", "This week"],
      xp: 20,
      kind: "paper",
    });
  }

  const day = store.days[key];
  if (day?.questIds?.length) {
    return quests;
  }
  return quests;
}

export function buildWeekPlan(
  store: ForgeStore,
  from = new Date(),
): WeekSlot[] {
  const start = new Date(from);
  start.setHours(0, 0, 0, 0);
  const slots: WeekSlot[] = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() - ((start.getDay() + 6) % 7) + i);
    const dow = d.getDay();
    const theme = WEEKDAY_THEMES[dow];
    const label = d.toLocaleDateString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
    const key = todayKey(d);
    const dayLog = store.days[key];
    const missed =
      d < new Date(todayKey()) &&
      (!dayLog || dayLog.checked.length === 0) &&
      dow !== 6;
    const quests = buildDailyQuests(store, d);
    slots.push({
      day: key,
      label,
      hours: theme.hours,
      theme: theme.theme,
      questIds: quests.map((q) => q.id),
      catchUp: Boolean(missed),
    });
  }
  return slots;
}

export function scheduleBlurb(): string[] {
  return [
    "Weekdays: 7–8pm + 10pm–12am (~3h career). College block ignored on purpose.",
    "Gatherly 8–10pm stays sacred — Forge never steals it.",
    "Sunday: deep work (~5h). Saturday: light catch-up or college-day mode.",
    "Miss a day? No pile-on. One catch-up chip folds into the next theme.",
    "Weekly paper → Dr. Delta. Concept names only — no tutorial hell.",
  ];
}
