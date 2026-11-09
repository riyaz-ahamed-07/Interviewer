import { todayKey } from "./progress";

/** Week 1 starts Monday 09-11-2026 */
export const FORGE_WEEK1_MONDAY = new Date(2026, 10, 9);

export function mondayIndex(d: Date): number {
  return (d.getDay() + 6) % 7;
}

export function startOfWeek(from: Date): Date {
  const d = new Date(from);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() - mondayIndex(d));
  return d;
}

function pad2(n: number) {
  return String(n).padStart(2, "0");
}

export function formatDateDMY(d: Date): string {
  return `${pad2(d.getDate())}-${pad2(d.getMonth() + 1)}-${d.getFullYear()}`;
}

export function mondayOfForgeWeek(weekNumber: number): Date {
  const epoch = startOfWeek(FORGE_WEEK1_MONDAY);
  const d = new Date(epoch);
  d.setDate(epoch.getDate() + (Math.max(1, weekNumber) - 1) * 7);
  return d;
}

export function forgeWeekNumber(from = new Date()): number {
  const monday = startOfWeek(from);
  const epoch = startOfWeek(FORGE_WEEK1_MONDAY);
  const diff = Math.round(
    (monday.getTime() - epoch.getTime()) / (24 * 60 * 60 * 1000),
  );
  return Math.max(1, Math.floor(diff / 7) + 1);
}

export function forgeWeekMeta(weekNumber: number) {
  const start = mondayOfForgeWeek(weekNumber);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  return {
    weekNumber: Math.max(1, weekNumber),
    start,
    end,
    rangeLabel: `${formatDateDMY(start)} – ${formatDateDMY(end)}`,
  };
}

export { todayKey };
