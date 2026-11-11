import 'package:shared_preferences/shared_preferences.dart';

class HomeWidgetService {
  HomeWidgetService._();
  static const androidName = 'KaizenStreakWidgetProvider';
  static const iOSName = 'KaizenStreakWidget';
  static const _prefix = 'flutter.';

  static Future<void> sync({
    required int streak,
    required int level,
    required int xpIntoLevel,
    required int xpForLevel,
    required int openTodos,
    required String nextTask,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('${_prefix}streak', streak);
    await prefs.setInt('${_prefix}level', level);
    await prefs.setInt('${_prefix}xp_into', xpIntoLevel);
    await prefs.setInt('${_prefix}xp_need', xpForLevel);
    await prefs.setInt('${_prefix}open_todos', openTodos);
    await prefs.setString(
      '${_prefix}next_task',
      nextTask.isEmpty ? 'Open Atlas' : nextTask,
    );
    await prefs.setString(
      '${_prefix}headline',
      streak > 0 ? '$streak-day streak' : 'Start today',
    );
  }
}
