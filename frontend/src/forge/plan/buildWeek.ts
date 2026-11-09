import type { PlanDay, PlanItem, PlanKind, PlanWeek } from "./types";

const BUDGET: Record<number, number> = {
  1: 180,
  2: 180,
  3: 180,
  4: 180,
  5: 180,
  6: 120,
  0: 300,
};

const DAY_LABEL: Record<number, string> = {
  1: "Mon",
  2: "Tue",
  3: "Wed",
  4: "Thu",
  5: "Fri",
  6: "Sat",
  0: "Sun",
};

const PRACTICE_KIND: Record<number, PlanKind> = {
  1: "sql",
  2: "aptitude",
  3: "ml",
  4: "sysdesign",
  5: "ml",
  6: "paper",
  0: "agents",
};

const PRACTICE_TITLE: Record<number, string> = {
  1: "SQL questions practice (2–3)",
  2: "Aptitude questions practice",
  3: "TrenTorch ML practice (2–3 Qs)",
  4: "System design practice (1 prompt)",
  5: "TrenTorch ML practice (2–3 Qs)",
  6: "Research paper (read / map / notes)",
  0: "Agentic AI practice (optional)",
};

const PRACTICE_LABEL: Record<number, string> = {
  1: "SQL",
  2: "Aptitude",
  3: "TrenTorch",
  4: "SysDesign",
  5: "TrenTorch",
  6: "Paper",
  0: "Agents",
};

const PRACTICE_MIN: Record<number, number> = {
  1: 50,
  2: 45,
  3: 55,
  4: 55,
  5: 55,
  6: 60,
  0: 60,
};

export type DaySeed = {
  dow: number;
  topic: string;
  conceptTitle: string;
  conceptId?: string;
  conceptMin?: number;
  practiceTitle?: string;
  practiceExtra?: PlanItem;
  deepExtra?: PlanItem[];
};

export function buildPlanWeek(
  weekNumber: number,
  theme: string,
  seeds: DaySeed[],
): PlanWeek {
  const byDow = new Map(seeds.map((s) => [s.dow, s]));
  const days: PlanDay[] = [1, 2, 3, 4, 5, 6, 0].map((dow) => {
    const seed = byDow.get(dow)!;
    const items: PlanItem[] = [
      {
        id: `w${weekNumber}-d${dow}-lc`,
        lane: "practice",
        kind: "leetcode",
        title: dow === 6 || dow === 0 ? "LeetCode (1 problem)" : "LeetCode (1–2 problems)",
        estMin: dow === 6 || dow === 0 ? 30 : 45,
      },
      {
        id: `w${weekNumber}-d${dow}-prac`,
        lane: "practice",
        kind: PRACTICE_KIND[dow],
        title: seed.practiceTitle ?? PRACTICE_TITLE[dow],
        estMin: PRACTICE_MIN[dow],
        optional: dow === 0,
      },
    ];

    if (seed.practiceExtra) items.push(seed.practiceExtra);

    items.push({
      id: `w${weekNumber}-d${dow}-concept`,
      lane: "concept",
      kind: "concept",
      title: seed.conceptTitle,
      estMin: seed.conceptMin ?? (dow === 0 ? 120 : 80),
      conceptId: seed.conceptId,
    });

    if (seed.deepExtra) items.push(...seed.deepExtra);

    if (dow === 6 || dow === 0) {
      items.push({
        id: `w${weekNumber}-d${dow}-module`,
        lane: "practice",
        kind: "module",
        title: "Module / college slot",
        estMin: 30,
        optional: true,
      });
    }

    return {
      week: weekNumber,
      dow,
      budgetMin: BUDGET[dow],
      label: `${DAY_LABEL[dow]} · ${seed.topic}`,
      practiceLabel: PRACTICE_LABEL[dow],
      items,
    };
  });

  return { weekNumber, theme, days };
}
