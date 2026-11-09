import { mondayOfForgeWeek, todayKey } from "../dates";
import { PLAN_WEEKS, MAX_PLANNED_WEEK } from "./catalog";
import type { PlanDay, PlanItem, PlanLane, PlanWeek } from "./types";

export function getMaxPlannedWeek() {
  return MAX_PLANNED_WEEK;
}

export function getWeek(weekNumber: number): PlanWeek | null {
  if (weekNumber < 1 || weekNumber > MAX_PLANNED_WEEK) return null;
  return PLAN_WEEKS.find((w) => w.weekNumber === weekNumber) ?? null;
}

export function getPlanDay(weekNumber: number, dow: number): PlanDay | null {
  const week = getWeek(weekNumber);
  if (!week) return null;
  return week.days.find((d) => d.dow === dow) ?? null;
}

export function itemsByLane(day: PlanDay, lane: PlanLane): PlanItem[] {
  return day.items.filter((i) => i.lane === lane);
}

export function dateKeyForPlanDay(weekNumber: number, dow: number): string {
  const monday = mondayOfForgeWeek(weekNumber);
  const offset = dow === 0 ? 6 : dow - 1;
  const d = new Date(monday);
  d.setDate(monday.getDate() + offset);
  return todayKey(d);
}

export function planItemCheckKey(dateKey: string, itemId: string) {
  return `${dateKey}::${itemId}`;
}
