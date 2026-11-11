import 'models.dart';

class TaskWindow {
  const TaskWindow({
    required this.item,
    required this.startHour,
    required this.startMinute,
    required this.endHour,
    required this.endMinute,
    this.carriedFromDateKey,
  });

  final PlanItemSummary item;
  final int startHour;
  final int startMinute;
  final int endHour;
  final int endMinute;
  final String? carriedFromDateKey;

  String get rangeLabel {
    return '${_fmt(startHour, startMinute)} – ${_fmt(endHour, endMinute)}';
  }

  static String _fmt(int h, int m) {
    final period = h >= 12 ? 'PM' : 'AM';
    final hour12 = h % 12 == 0 ? 12 : h % 12;
    final mm = m.toString().padLeft(2, '0');
    return '$hour12:$mm $period';
  }
}

class FocusSlot {
  const FocusSlot({
    required this.startMinutes,
    required this.endMinutes,
  });

  final int startMinutes;
  final int endMinutes;

  int get capacity => endMinutes - startMinutes;
}

const kEveningSlots = <FocusSlot>[
  FocusSlot(startMinutes: 19 * 60, endMinutes: 20 * 60),
  FocusSlot(startMinutes: 22 * 60, endMinutes: 24 * 60),
];

List<TaskWindow> scheduleTasksForEvening(
  List<PlanItemSummary> items, {
  Map<String, String> carriedFrom = const {},
}) {
  final required = items.where((i) => !i.optional).toList();
  final windows = <TaskWindow>[];
  var slotIndex = 0;
  var cursor = kEveningSlots.first.startMinutes;

  for (final item in required) {
    while (slotIndex < kEveningSlots.length) {
      final slot = kEveningSlots[slotIndex];
      if (cursor < slot.startMinutes) cursor = slot.startMinutes;
      final remaining = slot.endMinutes - cursor;
      if (remaining >= item.estMin || slotIndex == kEveningSlots.length - 1) {
        final start = cursor;
        final end = (cursor + item.estMin).clamp(start + 5, slot.endMinutes);
        windows.add(
          TaskWindow(
            item: item,
            startHour: start ~/ 60,
            startMinute: start % 60,
            endHour: end ~/ 60 == 24 ? 0 : end ~/ 60,
            endMinute: end % 60,
            carriedFromDateKey: carriedFrom[item.id],
          ),
        );
        cursor = end;
        if (cursor >= slot.endMinutes) {
          slotIndex += 1;
          if (slotIndex < kEveningSlots.length) {
            cursor = kEveningSlots[slotIndex].startMinutes;
          }
        }
        break;
      }
      slotIndex += 1;
      if (slotIndex < kEveningSlots.length) {
        cursor = kEveningSlots[slotIndex].startMinutes;
      }
    }
  }

  return windows;
}

String taskBrief(PlanItemSummary item) {
  final lane = item.lane == 'concept' ? 'Concept' : 'Practice';
  final idLine = item.conceptId == null ? '' : '\nLinked node: ${item.conceptId}';
  return '$lane · ${item.kind}\n'
      '${item.title}\n'
      'Estimate: ~${item.estMin} minutes$idLine\n\n'
      'Do this inside the shown window. Protect Gatherly 8–10 PM. '
      'If unfinished, it carries forward to the next open evening slot.';
}
