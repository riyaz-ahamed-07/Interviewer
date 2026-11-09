export type PlanLane = "practice" | "concept";

export type PlanKind =
  | "leetcode"
  | "sql"
  | "aptitude"
  | "ml"
  | "paper"
  | "module"
  | "concept"
  | "sysdesign"
  | "agents";

export type PlanItem = {
  id: string;
  lane: PlanLane;
  kind: PlanKind;
  title: string;
  estMin: number;
  conceptId?: string;
  optional?: boolean;
};

export type PlanDay = {
  week: number;
  dow: number;
  budgetMin: number;
  label: string;
  practiceLabel: string;
  items: PlanItem[];
};

export type PlanWeek = {
  weekNumber: number;
  theme: string;
  days: PlanDay[];
};
