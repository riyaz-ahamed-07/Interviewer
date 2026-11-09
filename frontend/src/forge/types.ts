export type NodeState = "todo" | "learning" | "done" | "mastered";

export type ForgeNode = {
  id: string;
  title: string;
  xp?: number;
  phase?: 1 | 2 | 3 | 4 | 5;
  children?: ForgeNode[];
};

export type Pillar = {
  id: string;
  title: string;
  blurb: string;
  accent: string;
  roots: ForgeNode[];
};

export type ProgressMap = Record<string, NodeState>;

export type DayLog = {
  date: string;
  xp: number;
  checked: string[];
  questIds: string[];
};

export type ForgeStore = {
  version: 1 | 2;
  startedAt: string;
  progress: ProgressMap;
  xp: number;
  streak: number;
  bestStreak: number;
  lastActiveDate: string | null;
  freezeLeft: number;
  days: Record<string, DayLog>;
  weekChecks: Record<string, boolean>;
  paperWeek: {
    weekKey: string;
    title: string;
    arxiv?: string;
    notes: string;
  } | null;
  focusPillarId: string | null;
  levelCelebrated: number;
};

export type DailyQuest = {
  id: string;
  title: string;
  pillarId: string;
  path: string[];
  xp: number;
  kind: "concept" | "paper" | "build" | "review";
};

export type WeekSlot = {
  day: string;
  label: string;
  hours: number;
  theme: string;
  questIds: string[];
  catchUp: boolean;
};
