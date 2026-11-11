import 'dart:convert';

import 'package:flutter/services.dart';

import 'models.dart';

class ForgeCurriculum {
  ForgeCurriculum._(this.pillars, this.plan);

  final List<Pillar> pillars;
  final PlanCatalog plan;

  static ForgeCurriculum? _cache;

  static Future<ForgeCurriculum> load() async {
    final hit = _cache;
    if (hit != null) return hit;

    final pillarsRaw = await rootBundle.loadString('assets/data/pillars.json');
    final planRaw = await rootBundle.loadString('assets/data/plan_weeks.json');
    final pillarsJson = jsonDecode(pillarsRaw) as List<dynamic>;
    final planJson = jsonDecode(planRaw) as Map<String, dynamic>;

    final loaded = ForgeCurriculum._(
      pillarsJson
          .whereType<Map<String, dynamic>>()
          .map(Pillar.fromJson)
          .toList(),
      PlanCatalog.fromJson(planJson),
    );
    _cache = loaded;
    return loaded;
  }

  Pillar? pillarById(String id) {
    for (final p in pillars) {
      if (p.id == id) return p;
    }
    return null;
  }

  List<Pillar> pillarsForTrack(CurriculumTrack track) {
    return track.pillarIds
        .map(pillarById)
        .whereType<Pillar>()
        .toList(growable: false);
  }

  int countLeaves(List<ForgeNode> nodes) {
    var c = 0;
    walk(nodes, (node) {
      if (!node.hasChildren) c += 1;
    });
    return c;
  }

  void walk(
    List<ForgeNode> nodes,
    void Function(ForgeNode node) fn,
  ) {
    for (final node in nodes) {
      fn(node);
      if (node.hasChildren) walk(node.children, fn);
    }
  }

  ({int total, int done}) pillarStats(
    Map<String, NodeState> progress,
    String pillarId,
  ) {
    final pillar = pillarById(pillarId);
    if (pillar == null) return (total: 0, done: 0);
    var total = 0;
    var done = 0;
    walk(pillar.roots, (node) {
      if (node.hasChildren) return;
      total += 1;
      final s = progress[node.id] ?? NodeState.todo;
      if (s == NodeState.done || s == NodeState.mastered) done += 1;
    });
    return (total: total, done: done);
  }

  ({int total, int done}) trackProgress(
    Map<String, NodeState> progress,
    List<String> pillarIds,
  ) {
    var total = 0;
    var done = 0;
    for (final id in pillarIds) {
      final s = pillarStats(progress, id);
      total += s.total;
      done += s.done;
    }
    return (total: total, done: done);
  }

  int forgeWeekNumber([DateTime? from]) {
    final now = from ?? DateTime.now();
    final monday = _startOfWeek(now);
    final epoch = _startOfWeek(plan.week1Monday);
    final week = (monday.difference(epoch).inDays ~/ 7) + 1;
    return week < 1 ? 1 : week;
  }

  int currentPlannedWeek() {
    final n = forgeWeekNumber();
    if (n > plan.maxPlannedWeek) return plan.maxPlannedWeek;
    return n < 1 ? 1 : n;
  }

  int planDow([DateTime? from]) {
    final d = from ?? DateTime.now();
    return d.weekday % 7;
  }

  PlanDaySummary? todayPlanDay([DateTime? from]) {
    return planDayForDate(from ?? DateTime.now());
  }

  PlanDaySummary? planDayForDate(DateTime from) {
    final weekNum = forgeWeekNumber(from);
    final clamped = weekNum > plan.maxPlannedWeek
        ? plan.maxPlannedWeek
        : (weekNum < 1 ? 1 : weekNum);
    final week = plan.week(clamped);
    if (week == null) return null;
    final dow = planDow(from);
    for (final day in week.days) {
      if (day.dow == dow) return day;
    }
    return null;
  }

  String todayDateKey([DateTime? from]) {
    final d = from ?? DateTime.now();
    final m = d.month.toString().padLeft(2, '0');
    final day = d.day.toString().padLeft(2, '0');
    return '${d.year}-$m-$day';
  }

  DateTime mondayOfCurrentWeek([DateTime? from]) {
    return _startOfWeek(from ?? DateTime.now());
  }

  DateTime _startOfWeek(DateTime from) {
    final d = DateTime(from.year, from.month, from.day);
    final mondayIndex = (d.weekday + 6) % 7;
    return d.subtract(Duration(days: mondayIndex));
  }
}
