class ForgeNode {
  const ForgeNode({
    required this.id,
    required this.title,
    this.xp,
    this.phase,
    this.children = const [],
  });

  final String id;
  final String title;
  final int? xp;
  final int? phase;
  final List<ForgeNode> children;

  bool get hasChildren => children.isNotEmpty;

  factory ForgeNode.fromJson(Map<String, dynamic> json) {
    final kids = json['children'];
    return ForgeNode(
      id: json['id'] as String,
      title: json['title'] as String,
      xp: json['xp'] as int?,
      phase: json['phase'] as int?,
      children: kids is List
          ? kids
                .whereType<Map<String, dynamic>>()
                .map(ForgeNode.fromJson)
                .toList()
          : const [],
    );
  }
}

class Pillar {
  const Pillar({
    required this.id,
    required this.title,
    required this.blurb,
    required this.accent,
    required this.roots,
  });

  final String id;
  final String title;
  final String blurb;
  final String accent;
  final List<ForgeNode> roots;

  factory Pillar.fromJson(Map<String, dynamic> json) {
    final roots = json['roots'];
    return Pillar(
      id: json['id'] as String,
      title: json['title'] as String,
      blurb: json['blurb'] as String,
      accent: json['accent'] as String,
      roots: roots is List
          ? roots
                .whereType<Map<String, dynamic>>()
                .map(ForgeNode.fromJson)
                .toList()
          : const [],
    );
  }
}

class CurriculumTrack {
  const CurriculumTrack({
    required this.id,
    required this.title,
    required this.pillarIds,
  });

  final String id;
  final String title;
  final List<String> pillarIds;
}

const kCurriculumTracks = <CurriculumTrack>[
  CurriculumTrack(
    id: 'foundations',
    title: 'Foundations',
    pillarIds: ['math', 'ml', 'aptitude'],
  ),
  CurriculumTrack(
    id: 'deep',
    title: 'Deep learning',
    pillarIds: ['dl'],
  ),
  CurriculumTrack(
    id: 'modern',
    title: 'Modern AI · Agents',
    pillarIds: ['llm', 'agents', 'papers', 'mlops'],
  ),
  CurriculumTrack(
    id: 'practice',
    title: 'TrenTorch practice',
    pillarIds: ['trentorch'],
  ),
  CurriculumTrack(
    id: 'systems',
    title: 'Systems · Core CS',
    pillarIds: ['systems', 'corecs'],
  ),
  CurriculumTrack(
    id: 'interview',
    title: 'Interview armor',
    pillarIds: ['dsa', 'sql', 'sysdesign', 'comms', 'career'],
  ),
];

enum NodeState { todo, learning, done, mastered }

extension NodeStateX on NodeState {
  String get mark {
    switch (this) {
      case NodeState.todo:
        return '○';
      case NodeState.learning:
        return '◐';
      case NodeState.done:
        return '●';
      case NodeState.mastered:
        return '◆';
    }
  }

  NodeState get next {
    switch (this) {
      case NodeState.todo:
        return NodeState.learning;
      case NodeState.learning:
        return NodeState.done;
      case NodeState.done:
        return NodeState.mastered;
      case NodeState.mastered:
        return NodeState.todo;
    }
  }

  String get storage => name;
}

class PlanItemSummary {
  const PlanItemSummary({
    required this.id,
    required this.lane,
    required this.kind,
    required this.title,
    required this.estMin,
    this.conceptId,
    this.optional = false,
  });

  final String id;
  final String lane;
  final String kind;
  final String title;
  final int estMin;
  final String? conceptId;
  final bool optional;

  factory PlanItemSummary.fromJson(Map<String, dynamic> json) {
    return PlanItemSummary(
      id: json['id'] as String,
      lane: json['lane'] as String? ?? 'practice',
      kind: json['kind'] as String? ?? 'module',
      title: json['title'] as String,
      estMin: json['estMin'] as int? ?? 45,
      conceptId: json['conceptId'] as String?,
      optional: json['optional'] as bool? ?? false,
    );
  }
}

class PlanDaySummary {
  const PlanDaySummary({
    required this.dow,
    required this.label,
    required this.practiceLabel,
    required this.budgetMin,
    required this.items,
    this.conceptTitle = '',
    this.conceptId,
  });

  final int dow;
  final String label;
  final String practiceLabel;
  final int budgetMin;
  final List<PlanItemSummary> items;
  final String conceptTitle;
  final String? conceptId;

  List<PlanItemSummary> get practiceItems =>
      items.where((i) => i.lane == 'practice').toList(growable: false);

  List<PlanItemSummary> get conceptItems =>
      items.where((i) => i.lane == 'concept').toList(growable: false);

  factory PlanDaySummary.fromJson(Map<String, dynamic> json) {
    final items = json['items'];
    final parsedItems = items is List
        ? items
              .whereType<Map<String, dynamic>>()
              .map(PlanItemSummary.fromJson)
              .toList()
        : <PlanItemSummary>[];
    final concept = parsedItems.where((i) => i.lane == 'concept').firstOrNull;
    return PlanDaySummary(
      dow: json['dow'] as int,
      label: json['label'] as String? ?? '',
      practiceLabel: json['practiceLabel'] as String? ?? '',
      budgetMin: json['budgetMin'] as int? ?? 180,
      items: parsedItems,
      conceptTitle:
          json['conceptTitle'] as String? ?? concept?.title ?? '',
      conceptId: json['conceptId'] as String? ?? concept?.conceptId,
    );
  }
}

class PlanWeekSummary {
  const PlanWeekSummary({
    required this.weekNumber,
    required this.theme,
    required this.days,
  });

  final int weekNumber;
  final String theme;
  final List<PlanDaySummary> days;

  factory PlanWeekSummary.fromJson(Map<String, dynamic> json) {
    final days = json['days'];
    return PlanWeekSummary(
      weekNumber: json['weekNumber'] as int,
      theme: json['theme'] as String,
      days: days is List
          ? days
                .whereType<Map<String, dynamic>>()
                .map(PlanDaySummary.fromJson)
                .toList()
          : const [],
    );
  }
}

class PlanCatalog {
  const PlanCatalog({
    required this.maxPlannedWeek,
    required this.week1Monday,
    required this.weeks,
  });

  final int maxPlannedWeek;
  final DateTime week1Monday;
  final List<PlanWeekSummary> weeks;

  factory PlanCatalog.fromJson(Map<String, dynamic> json) {
    final weeks = json['weeks'];
    final raw = json['week1Monday'] as String;
    final parts = raw.split('-').map(int.parse).toList();
    return PlanCatalog(
      maxPlannedWeek: json['maxPlannedWeek'] as int? ?? 12,
      week1Monday: DateTime(parts[0], parts[1], parts[2]),
      weeks: weeks is List
          ? weeks
                .whereType<Map<String, dynamic>>()
                .map(PlanWeekSummary.fromJson)
                .toList()
          : const [],
    );
  }

  PlanWeekSummary? week(int n) {
    for (final w in weeks) {
      if (w.weekNumber == n) return w;
    }
    return null;
  }
}
