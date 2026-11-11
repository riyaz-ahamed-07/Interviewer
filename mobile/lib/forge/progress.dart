import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'curriculum.dart';
import 'levels.dart';
import 'models.dart';

const _kStoreKey = 'interviewer.forge.v1';

NodeState parseNodeState(String? raw) {
  switch (raw) {
    case 'learning':
      return NodeState.learning;
    case 'done':
      return NodeState.done;
    case 'mastered':
      return NodeState.mastered;
    default:
      return NodeState.todo;
  }
}

String todayKey([DateTime? from]) {
  final d = from ?? DateTime.now();
  final m = d.month.toString().padLeft(2, '0');
  final day = d.day.toString().padLeft(2, '0');
  return '${d.year}-$m-$day';
}

String planItemCheckKey(String dateKey, String itemId) => '$dateKey::$itemId';

class CarriedPlanTask {
  const CarriedPlanTask({
    required this.id,
    required this.fromDateKey,
    required this.item,
  });

  final String id;
  final String fromDateKey;
  final PlanItemSummary item;

  Map<String, dynamic> toJson() => {
        'id': id,
        'fromDateKey': fromDateKey,
        'item': {
          'id': item.id,
          'lane': item.lane,
          'kind': item.kind,
          'title': item.title,
          'estMin': item.estMin,
          'conceptId': item.conceptId,
          'optional': item.optional,
        },
      };

  factory CarriedPlanTask.fromJson(Map<String, dynamic> json) {
    final itemJson = Map<String, dynamic>.from(json['item'] as Map);
    return CarriedPlanTask(
      id: json['id'] as String,
      fromDateKey: json['fromDateKey'] as String,
      item: PlanItemSummary.fromJson(itemJson),
    );
  }
}

class ForgeProgressStore extends ChangeNotifier {
  ForgeProgressStore._(this._prefs);

  final SharedPreferences _prefs;

  Map<String, NodeState> progress = {};
  Map<String, bool> weekChecks = {};
  List<CarriedPlanTask> carried = [];
  int xp = 0;
  int streak = 0;
  int bestStreak = 0;
  String? lastActiveDate;
  int freezeLeft = 2;

  LevelProgress get level => levelForXp(xp);

  static Future<ForgeProgressStore> open() async {
    final prefs = await SharedPreferences.getInstance();
    final store = ForgeProgressStore._(prefs);
    store._hydrate();
    return store;
  }

  void _hydrate() {
    final raw = _prefs.getString(_kStoreKey);
    if (raw == null || raw.isEmpty) {
      _migrateLegacyProgress();
      return;
    }
    try {
      final decoded = jsonDecode(raw);
      if (decoded is! Map) return;
      final map = Map<String, dynamic>.from(decoded);
      final progressRaw = map['progress'];
      if (progressRaw is Map) {
        progress = {
          for (final e in progressRaw.entries)
            e.key.toString(): parseNodeState(e.value?.toString()),
        };
      }
      final checksRaw = map['weekChecks'];
      if (checksRaw is Map) {
        weekChecks = {
          for (final e in checksRaw.entries)
            e.key.toString(): e.value == true,
        };
      }
      xp = (map['xp'] as num?)?.toInt() ?? 0;
      streak = (map['streak'] as num?)?.toInt() ?? 0;
      bestStreak = (map['bestStreak'] as num?)?.toInt() ?? 0;
      lastActiveDate = map['lastActiveDate'] as String?;
      freezeLeft = (map['freezeLeft'] as num?)?.toInt() ?? 2;
      final carriedRaw = map['carried'];
      if (carriedRaw is List) {
        carried = carriedRaw
            .whereType<Map>()
            .map((e) => CarriedPlanTask.fromJson(Map<String, dynamic>.from(e)))
            .toList();
      }
    } catch (_) {
      progress = {};
      weekChecks = {};
      carried = [];
    }
  }

  void _migrateLegacyProgress() {
    final legacy = _prefs.getString('interviewer.forge.v1.progress');
    if (legacy == null || legacy.isEmpty) return;
    try {
      final decoded = jsonDecode(legacy);
      if (decoded is! Map) return;
      progress = {
        for (final e in decoded.entries)
          e.key.toString(): parseNodeState(e.value?.toString()),
      };
      _persist();
    } catch (_) {}
  }

  Future<void> _persist() async {
    final payload = {
      'version': 2,
      'progress': {
        for (final e in progress.entries) e.key: e.value.storage,
      },
      'weekChecks': weekChecks,
      'carried': carried.map((e) => e.toJson()).toList(),
      'xp': xp,
      'streak': streak,
      'bestStreak': bestStreak,
      'lastActiveDate': lastActiveDate,
      'freezeLeft': freezeLeft,
    };
    await _prefs.setString(_kStoreKey, jsonEncode(payload));
  }

  String _dayBefore(String key) {
    final parts = key.split('-').map(int.parse).toList();
    final dt = DateTime(parts[0], parts[1], parts[2])
        .subtract(const Duration(days: 1));
    return todayKey(dt);
  }

  void _touchStreak([String? date]) {
    final key = date ?? todayKey();
    if (lastActiveDate == key) return;
    final prev = lastActiveDate;
    if (prev == null) {
      streak = 1;
    } else if (prev == _dayBefore(key)) {
      streak += 1;
    } else if (freezeLeft > 0 && prev == _dayBefore(_dayBefore(key))) {
      freezeLeft -= 1;
      streak += 1;
    } else {
      streak = 1;
    }
    bestStreak = streak > bestStreak ? streak : bestStreak;
    lastActiveDate = key;
  }

  int _leafXp(ForgeCurriculum? curriculum, String id) {
    if (curriculum == null) return 12;
    for (final pillar in curriculum.pillars) {
      ForgeNode? found;
      curriculum.walk(pillar.roots, (node) {
        if (node.id == id) found = node;
      });
      if (found != null) return found!.xp ?? 12;
    }
    return 12;
  }

  Future<void> setNodeState(
    String id,
    NodeState state, {
    ForgeCurriculum? curriculum,
  }) async {
    final prev = progress[id] ?? NodeState.todo;
    if (prev == state) return;
    final leafXp = _leafXp(curriculum, id);
    var xpDelta = 0;
    if (state == NodeState.learning && prev == NodeState.todo) {
      xpDelta = (leafXp * 0.25).floor();
    }
    if (state == NodeState.done &&
        prev != NodeState.done &&
        prev != NodeState.mastered) {
      xpDelta = leafXp;
    }
    if (state == NodeState.mastered && prev != NodeState.mastered) {
      xpDelta = prev == NodeState.done
          ? (leafXp * 0.5).floor()
          : (leafXp * 1.5).floor();
    }
    if ((prev == NodeState.done || prev == NodeState.mastered) &&
        (state == NodeState.todo || state == NodeState.learning)) {
      xpDelta = -((leafXp * (prev == NodeState.mastered ? 1.5 : 1)).floor());
    }

    progress = {...progress, id: state};
    xp = (xp + xpDelta).clamp(0, 1 << 30);
    _touchStreak();
    await _persist();
    notifyListeners();
  }

  Future<void> cycle(
    String id, {
    ForgeCurriculum? curriculum,
  }) async {
    final prev = progress[id] ?? NodeState.todo;
    await setNodeState(id, prev.next, curriculum: curriculum);
  }

  bool isWeekTaskDone(String dateKey, String itemId) {
    return weekChecks[planItemCheckKey(dateKey, itemId)] ?? false;
  }

  Future<void> toggleWeekTask(String dateKey, String itemId) async {
    final key = planItemCheckKey(dateKey, itemId);
    final next = !(weekChecks[key] ?? false);
    weekChecks = {...weekChecks, key: next};
    if (next) {
      xp += 8;
      _touchStreak(dateKey);
      carried = carried
          .where((c) => !(c.fromDateKey == dateKey && c.item.id == itemId))
          .where((c) => c.item.id != itemId)
          .toList();
    } else {
      xp = (xp - 8).clamp(0, 1 << 30);
    }
    await _persist();
    notifyListeners();
  }

  ({int done, int total}) todayTaskStats(
    List<PlanItemSummary> items,
    String dateKey,
  ) {
    final required = items.where((i) => !i.optional).toList();
    var done = 0;
    for (final item in required) {
      if (isWeekTaskDone(dateKey, item.id)) done += 1;
    }
    return (done: done, total: required.length);
  }

  ({int done, int total}) overallMastery(ForgeCurriculum curriculum) {
    return curriculum.trackProgress(
      progress,
      curriculum.pillars.map((p) => p.id).toList(),
    );
  }

  Future<void> reconcileCarryForward(ForgeCurriculum curriculum) async {
    final today = DateTime.now();
    final todayDate = DateTime(today.year, today.month, today.day);
    final todayKeyStr = curriculum.todayDateKey(todayDate);
    final weekStart = curriculum.mondayOfCurrentWeek(todayDate);
    final pending = <CarriedPlanTask>[];
    final seen = <String>{};

    for (var d = weekStart;
        d.isBefore(todayDate);
        d = d.add(const Duration(days: 1))) {
      final dateKey = curriculum.todayDateKey(d);
      final planDay = curriculum.planDayForDate(d);
      if (planDay == null) continue;
      for (final item in planDay.items.where((i) => !i.optional)) {
        if (isWeekTaskDone(dateKey, item.id)) continue;
        final key = '$dateKey::${item.id}';
        if (!seen.add(key)) continue;
        pending.add(
          CarriedPlanTask(
            id: 'carry-$dateKey-${item.id}',
            fromDateKey: dateKey,
            item: item,
          ),
        );
      }
    }

    pending.removeWhere((c) => isWeekTaskDone(todayKeyStr, c.item.id));
    pending.removeWhere((c) => isWeekTaskDone(c.fromDateKey, c.item.id));

    carried = pending;
    await _persist();
    notifyListeners();
  }

  List<PlanItemSummary> composedTodayItems(PlanDaySummary? day) {
    final todayItems = [
      ...(day?.items ?? const <PlanItemSummary>[]),
    ];
    final ids = todayItems.map((i) => i.id).toSet();
    var used = todayItems
        .where((i) => !i.optional)
        .fold<int>(0, (sum, i) => sum + i.estMin);
    const eveningBudget = 180;

    for (final c in carried) {
      if (ids.contains(c.item.id)) continue;
      if (used + c.item.estMin > eveningBudget) continue;
      todayItems.add(c.item);
      ids.add(c.item.id);
      used += c.item.estMin;
    }
    return todayItems;
  }

  Map<String, String> carriedFromMap() => {
        for (final c in carried) c.item.id: c.fromDateKey,
      };

  ({int practiceDone, int practiceTotal, int conceptDone, int conceptTotal})
      laneWeekStats(ForgeCurriculum curriculum) {
    var practiceDone = 0;
    var practiceTotal = 0;
    var conceptDone = 0;
    var conceptTotal = 0;
    final week = curriculum.plan.week(curriculum.currentPlannedWeek());
    if (week == null) {
      return (
        practiceDone: 0,
        practiceTotal: 0,
        conceptDone: 0,
        conceptTotal: 0,
      );
    }
    final monday = curriculum.mondayOfCurrentWeek();
    for (final day in week.days) {
      final offset = day.dow == 0 ? 6 : day.dow - 1;
      final date = monday.add(Duration(days: offset));
      final dateKey = curriculum.todayDateKey(date);
      for (final item in day.items.where((i) => !i.optional)) {
        final done = isWeekTaskDone(dateKey, item.id);
        if (item.lane == 'practice') {
          practiceTotal += 1;
          if (done) practiceDone += 1;
        } else {
          conceptTotal += 1;
          if (done) conceptDone += 1;
        }
      }
    }
    return (
      practiceDone: practiceDone,
      practiceTotal: practiceTotal,
      conceptDone: conceptDone,
      conceptTotal: conceptTotal,
    );
  }

  Map<String, int> heatmapCounts(ForgeCurriculum curriculum, {int days = 35}) {
    final out = <String, int>{};
    final today = DateTime.now();
    for (var i = 0; i < days; i++) {
      final day = today.subtract(Duration(days: i));
      final key = curriculum.todayDateKey(day);
      var count = 0;
      for (final e in weekChecks.entries) {
        if (e.value && e.key.startsWith('$key::')) count += 1;
      }
      out[key] = count;
    }
    return out;
  }
}
