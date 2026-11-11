import '../forge/progress.dart';
import '../forge/todo_store.dart';
import 'home_widget_service.dart';
import 'notification_service.dart';

Future<void> syncMomentum({
  required ForgeProgressStore store,
  required CustomTodoStore todos,
  String? nextTaskTitle,
  DateTime? nextTaskAt,
}) async {
  final open = todos.openItems;
  final nextTodo = open.where((t) => t.deadline != null).firstOrNull ??
      open.firstOrNull;
  final title = nextTaskTitle ?? nextTodo?.title;
  final at = nextTaskAt ?? nextTodo?.deadline;
  final level = store.level;

  await NotificationService.instance.syncSchedule(
    streak: store.streak,
    lastActiveDate: store.lastActiveDate,
    openTodos: open
        .map((t) => (title: t.title, deadline: t.deadline))
        .toList(growable: false),
    nextTaskTitle: title,
    nextTaskAt: at,
  );

  await HomeWidgetService.sync(
    streak: store.streak,
    level: level.level,
    xpIntoLevel: (level.xp - level.floorXp).clamp(0, 1 << 30),
    xpForLevel: (level.nextXp - level.floorXp).clamp(1, 1 << 30),
    openTodos: open.length,
    nextTask: title ?? '',
  );
}
