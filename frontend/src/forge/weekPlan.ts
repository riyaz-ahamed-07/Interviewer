import {
  forgeWeekMeta,
  forgeWeekNumber,
  mondayOfForgeWeek,
  todayKey,
} from "./dates";
import { getMaxPlannedWeek, getWeek } from "./plan/selectors";
import type { PlanItem, PlanKind } from "./plan/types";
import type { ForgeStore } from "./types";

export type DayTask = {
  id: string;
  text: string;
  kind: PlanKind;
  lane: "practice" | "concept";
  estMin?: number;
  conceptId?: string;
  optional?: boolean;
};

export type DayCardModel = {
  dateKey: string;
  date: Date;
  label: string;
  shortLabel: string;
  isToday: boolean;
  topic: string;
  practiceLabel: string;
  budgetMin: number;
  weekNumber: number;
  tasks: DayTask[];
};

export {
  forgeWeekMeta,
  forgeWeekNumber,
  mondayOfForgeWeek,
  todayKey,
  getMaxPlannedWeek,
};

function toTask(item: PlanItem): DayTask {
  return {
    id: item.id,
    text: item.title,
    kind: item.kind,
    lane: item.lane,
    estMin: item.estMin,
    conceptId: item.conceptId,
    optional: item.optional,
  };
}

export function buildWeekDayCards(
  _store: ForgeStore,
  weekNumber: number,
): DayCardModel[] {
  const plan = getWeek(weekNumber);
  if (!plan) return [];
  const monday = mondayOfForgeWeek(weekNumber);
  const today = todayKey(new Date());
  const cards: DayCardModel[] = [];

  for (const day of plan.days) {
    const offset = day.dow === 0 ? 6 : day.dow - 1;
    const d = new Date(monday);
    d.setDate(monday.getDate() + offset);
    const dateKey = todayKey(d);
    const topic = day.label.includes("·")
      ? day.label.split("·")[1].trim()
      : day.label;

    cards.push({
      dateKey,
      date: d,
      label: d.toLocaleDateString("en-US", {
        weekday: "short",
        day: "numeric",
        month: "short",
      }),
      shortLabel: d.toLocaleDateString("en-US", { weekday: "short" }),
      isToday: dateKey === today,
      topic,
      practiceLabel: day.practiceLabel,
      budgetMin: day.budgetMin,
      weekNumber,
      tasks: day.items.map(toTask),
    });
  }

  return cards;
}

export function taskKey(dateKey: string, taskId: string) {
  return `${dateKey}::${taskId}`;
}

export function streakIsAlive(store: ForgeStore, from = new Date()): boolean {
  if (store.streak <= 0 || !store.lastActiveDate) return false;
  const today = todayKey(from);
  if (store.lastActiveDate === today) return true;
  const [y, m, d] = today.split("-").map(Number);
  const yest = new Date(y, m - 1, d);
  yest.setDate(yest.getDate() - 1);
  return store.lastActiveDate === todayKey(yest);
}

export function getDayCard(
  store: ForgeStore,
  weekNumber: number,
  dateKey: string,
): DayCardModel | null {
  return (
    buildWeekDayCards(store, weekNumber).find((c) => c.dateKey === dateKey) ??
    null
  );
}
