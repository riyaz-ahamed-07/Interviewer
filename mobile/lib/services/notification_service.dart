import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/data/latest.dart' as tzdata;
import 'package:timezone/timezone.dart' as tz;

class NotificationService {
  NotificationService._();
  static final instance = NotificationService._();

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();
  bool _ready = false;

  static const _morningId = 1001;
  static const _taskAheadId = 1002;
  static const _taskNowId = 1003;
  static const _streakSaverId = 1004;
  static const _streakCriticalId = 1005;
  static const _comebackId = 1006;

  Future<void> init() async {
    if (_ready) return;
    tzdata.initializeTimeZones();
    try {
      final name = await FlutterTimezone.getLocalTimezone();
      tz.setLocalLocation(tz.getLocation(name));
    } catch (_) {
      tz.setLocalLocation(tz.getLocation('UTC'));
    }

    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    await _plugin.initialize(
      const InitializationSettings(android: android, iOS: ios),
    );

    if (Platform.isAndroid) {
      final androidPlugin = _plugin.resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin>();
      await androidPlugin?.requestNotificationsPermission();
      await androidPlugin?.createNotificationChannel(
        const AndroidNotificationChannel(
          'kaizen_momentum',
          'Momentum',
          description: 'Streak savers, morning kickoffs, and task nudges',
          importance: Importance.high,
        ),
      );
      await androidPlugin?.createNotificationChannel(
        const AndroidNotificationChannel(
          'kaizen_streak_critical',
          'Streak on the line',
          description: 'Urgent countdown when your streak is about to break',
          importance: Importance.max,
        ),
      );
    }
    _ready = true;
  }

  NotificationDetails _rich({
    required String channel,
    required String titleBig,
    String? summary,
    bool critical = false,
  }) {
    return NotificationDetails(
      android: AndroidNotificationDetails(
        channel,
        critical ? 'Streak on the line' : 'Momentum',
        channelDescription: critical
            ? 'Urgent countdown when your streak is about to break'
            : 'Streak savers, morning kickoffs, and task nudges',
        importance: critical ? Importance.max : Importance.high,
        priority: critical ? Priority.max : Priority.high,
        styleInformation: BigTextStyleInformation(
          titleBig,
          contentTitle: summary,
          summaryText: 'Kaizen',
        ),
        largeIcon: const DrawableResourceAndroidBitmap('@mipmap/ic_launcher'),
        category: AndroidNotificationCategory.reminder,
        actions: critical
            ? const [
                AndroidNotificationAction(
                  'open_home',
                  'Save streak',
                  showsUserInterface: true,
                ),
                AndroidNotificationAction(
                  'snooze_30',
                  'Remind in 30m',
                ),
              ]
            : const [
                AndroidNotificationAction(
                  'open_home',
                  'Open Kaizen',
                  showsUserInterface: true,
                ),
              ],
      ),
      iOS: DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
        interruptionLevel: critical
            ? InterruptionLevel.timeSensitive
            : InterruptionLevel.active,
      ),
    );
  }

  Future<void> syncSchedule({
    required int streak,
    required String? lastActiveDate,
    required List<({String title, DateTime? deadline})> openTodos,
    String? nextTaskTitle,
    DateTime? nextTaskAt,
  }) async {
    if (!_ready) await init();
    await _plugin.cancelAll();

    final now = tz.TZDateTime.now(tz.local);
    final practicedToday = lastActiveDate == _dayKey(now);

    await _scheduleDaily(
      id: _morningId,
      hour: 8,
      minute: 0,
      title: streak > 0
          ? '🔥 Day ${streak + (practicedToday ? 0 : 1)} is waiting'
          : '☕ Morning kickoff',
      body: nextTaskTitle == null || nextTaskTitle.isEmpty
          ? 'Open Atlas, check one box, keep the rhythm.'
          : 'First up: $nextTaskTitle — 12 quiet minutes is enough.',
      channel: 'kaizen_momentum',
    );

    if (!practicedToday) {
      await _scheduleOnceOrDaily(
        id: _streakSaverId,
        hour: 20,
        minute: 0,
        title: streak > 0 ? '⏳ $streak-day streak · evening window' : '🌙 Soft restart',
        body: streak > 0
            ? 'Your streak resets at midnight. One leaf now keeps the fire.'
            : 'No guilt. Open Kaizen and mark one tiny win.',
        channel: 'kaizen_momentum',
      );

      final criticalAt = tz.TZDateTime(
        tz.local,
        now.year,
        now.month,
        now.day,
        22,
        30,
      );
      if (criticalAt.isAfter(now) && streak > 0) {
        await _plugin.zonedSchedule(
          _streakCriticalId,
          '🚨 Streak on the line · ~90 min left',
          'Tap Save streak. Raeez is ready for a 5-minute soft mock.',
          criticalAt,
          _rich(
            channel: 'kaizen_streak_critical',
            titleBig:
                'Your $streak-day streak breaks at midnight. One checkbox saves it.',
            summary: 'Streak countdown',
            critical: true,
          ),
          androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        );
      }
    }

    if (lastActiveDate != null && !practicedToday) {
      final last = DateTime.tryParse(lastActiveDate);
      if (last != null) {
        final hours = now.difference(last).inHours;
        if (hours >= 23) {
          final when = now.add(const Duration(minutes: 5));
          await _plugin.zonedSchedule(
            _comebackId,
            '🦉 We saved your seat',
            'Comeback > perfect. Open Atlas and reclaim momentum.',
            when,
            _rich(
              channel: 'kaizen_momentum',
              titleBig:
                  'It has been ~${hours}h since your last practice. Duolingo-style nudge: return before the habit cools.',
              summary: 'Comeback nudge',
            ),
            androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
          );
        }
      }
    }

    final task = nextTaskAt;
    final taskTitle = nextTaskTitle;
    if (task != null && taskTitle != null && taskTitle.isNotEmpty) {
      final localTask = tz.TZDateTime.from(task, tz.local);
      final ahead = localTask.subtract(const Duration(minutes: 20));
      if (ahead.isAfter(now)) {
        await _plugin.zonedSchedule(
          _taskAheadId,
          '⏰ $taskTitle in 20 min',
          'Prep the tab. When the clock hits, you are already mid-flow.',
          ahead,
          _rich(
            channel: 'kaizen_momentum',
            titleBig: 'Upcoming: $taskTitle. Set a timer for deep work.',
            summary: 'Beforehand nudge',
          ),
          androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        );
      }
      if (localTask.isAfter(now)) {
        await _plugin.zonedSchedule(
          _taskNowId,
          '▶ $taskTitle · now',
          'Start the block. Mark it done when you land the win.',
          localTask,
          _rich(
            channel: 'kaizen_momentum',
            titleBig: 'It is time for $taskTitle. Open Kaizen and execute.',
            summary: 'On-time cue',
          ),
          androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        );
      }
    }

    var id = 1100;
    for (final todo in openTodos.take(3)) {
      final deadline = todo.deadline;
      if (deadline == null) continue;
      final local = tz.TZDateTime.from(deadline, tz.local);
      final ahead = local.subtract(const Duration(minutes: 30));
      if (ahead.isAfter(now)) {
        await _plugin.zonedSchedule(
          id++,
          '📌 ${todo.title} soon',
          'Deadline in 30 minutes. Chip away now.',
          ahead,
          _rich(
            channel: 'kaizen_momentum',
            titleBig: todo.title,
            summary: 'Todo reminder',
          ),
          androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        );
      }
    }

    if (kDebugMode) {
      debugPrint('Kaizen notifications rescheduled (streak=$streak)');
    }
  }

  Future<void> _scheduleDaily({
    required int id,
    required int hour,
    required int minute,
    required String title,
    required String body,
    required String channel,
  }) async {
    final now = tz.TZDateTime.now(tz.local);
    var when = tz.TZDateTime(tz.local, now.year, now.month, now.day, hour, minute);
    if (!when.isAfter(now)) {
      when = when.add(const Duration(days: 1));
    }
    await _plugin.zonedSchedule(
      id,
      title,
      body,
      when,
      _rich(channel: channel, titleBig: body, summary: title),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      matchDateTimeComponents: DateTimeComponents.time,
    );
  }

  Future<void> _scheduleOnceOrDaily({
    required int id,
    required int hour,
    required int minute,
    required String title,
    required String body,
    required String channel,
  }) async {
    final now = tz.TZDateTime.now(tz.local);
    var when = tz.TZDateTime(tz.local, now.year, now.month, now.day, hour, minute);
    if (!when.isAfter(now)) return;
    await _plugin.zonedSchedule(
      id,
      title,
      body,
      when,
      _rich(channel: channel, titleBig: body, summary: title),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
    );
  }

  String _dayKey(DateTime dt) {
    final m = dt.month.toString().padLeft(2, '0');
    final d = dt.day.toString().padLeft(2, '0');
    return '${dt.year}-$m-$d';
  }
}
