import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../forge/curriculum.dart';
import '../../forge/forge_scope.dart';
import '../../forge/models.dart';
import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class MasterListScreen extends StatefulWidget {
  const MasterListScreen({super.key});

  @override
  State<MasterListScreen> createState() => _MasterListScreenState();
}

class _MasterListScreenState extends State<MasterListScreen> {
  String _trackId = 'all';
  final Set<String> _expandedPillars = {};
  final Set<String> _openNodes = {};
  String _query = '';
  String _flash = '';
  var _seeded = false;

  Future<void> _toggleLeaf(String id) async {
    final store = ForgeScope.storeOf(context);
    final curriculum = ForgeScope.curriculumOf(context);
    await store.cycle(id, curriculum: curriculum);
    if (!mounted) return;
    final next = store.progress[id] ?? NodeState.todo;
    setState(() {
      _flash = switch (next) {
        NodeState.mastered => 'Mastered',
        NodeState.done => 'Done',
        NodeState.learning => 'Learning',
        NodeState.todo => '',
      };
    });
    if (_flash.isNotEmpty) {
      Future<void>.delayed(const Duration(milliseconds: 1200), () {
        if (mounted) setState(() => _flash = '');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final curriculum = ForgeScope.curriculumOf(context);
    final store = ForgeScope.storeOf(context);
    if (!_seeded && curriculum.pillars.isNotEmpty) {
      _expandedPillars.add(curriculum.pillars.first.id);
      _seeded = true;
    }

    return Scaffold(
      appBar: const KaizenTopBar(subtitle: 'Atlas'),
      body: SoftPagePadding(
        child: _MasterListBody(
          curriculum: curriculum,
          progress: store.progress,
          trackId: _trackId,
          query: _query,
          expandedPillars: _expandedPillars,
          openNodes: _openNodes,
          flash: _flash,
          onQuery: (q) => setState(() => _query = q),
          onSelectTrack: (id) => setState(() => _trackId = id),
          onTogglePillar: (id) {
            setState(() {
              if (_expandedPillars.contains(id)) {
                _expandedPillars.remove(id);
              } else {
                _expandedPillars.add(id);
              }
            });
          },
          onToggleNode: (id) {
            setState(() {
              if (_openNodes.contains(id)) {
                _openNodes.remove(id);
              } else {
                _openNodes.add(id);
              }
            });
          },
          onToggleLeaf: _toggleLeaf,
        ),
      ),
    );
  }
}

class _MasterListBody extends StatelessWidget {
  const _MasterListBody({
    required this.curriculum,
    required this.progress,
    required this.trackId,
    required this.query,
    required this.expandedPillars,
    required this.openNodes,
    required this.flash,
    required this.onQuery,
    required this.onSelectTrack,
    required this.onTogglePillar,
    required this.onToggleNode,
    required this.onToggleLeaf,
  });

  final ForgeCurriculum curriculum;
  final Map<String, NodeState> progress;
  final String trackId;
  final String query;
  final Set<String> expandedPillars;
  final Set<String> openNodes;
  final String flash;
  final ValueChanged<String> onQuery;
  final ValueChanged<String> onSelectTrack;
  final ValueChanged<String> onTogglePillar;
  final ValueChanged<String> onToggleNode;
  final ValueChanged<String> onToggleLeaf;

  List<Pillar> get _visiblePillars {
    final q = query.trim().toLowerCase();
    Iterable<Pillar> base;
    if (trackId == 'all') {
      base = curriculum.pillars;
    } else {
      final track = kCurriculumTracks.firstWhere((t) => t.id == trackId);
      base = curriculum.pillarsForTrack(track);
    }
    if (q.isEmpty) return base.toList();
    return base
        .where(
          (p) =>
              p.title.toLowerCase().contains(q) ||
              p.blurb.toLowerCase().contains(q) ||
              p.id.toLowerCase().contains(q),
        )
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final overall = curriculum.trackProgress(
      progress,
      curriculum.pillars.map((p) => p.id).toList(),
    );
    final pct = overall.total == 0
        ? 0
        : ((overall.done / overall.total) * 100).round();
    final pillars = _visiblePillars;
    final activeCycle = pillars
        .where((p) {
          final s = curriculum.pillarStats(progress, p.id);
          return s.done > 0 && s.done < s.total;
        })
        .length;

    return ListView(
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'KNOWLEDGE ATLAS',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: KaizenColors.primaryDeep,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.8,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Atlas',
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.8,
                      height: 1.05,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  'Progress',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: KaizenColors.inkSoft,
                  ),
                ),
                Text(
                  '$pct%',
                  style: theme.textTheme.titleLarge?.copyWith(
                    color: KaizenColors.primaryDeep,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ],
        ),
        if (flash.isNotEmpty) ...[
          const SizedBox(height: 8),
          AnimatedOpacity(
            opacity: 1,
            duration: const Duration(milliseconds: 200),
            child: Text(
              flash,
              style: theme.textTheme.labelLarge?.copyWith(
                color: KaizenColors.secondary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
        const SizedBox(height: 14),
        _MasteryQuotientCard(
          done: overall.done,
          total: overall.total,
          pillarCount: curriculum.pillars.length,
          activeCycle: activeCycle,
        ),
        const SizedBox(height: 14),
        TextField(
          onChanged: onQuery,
          decoration: InputDecoration(
            hintText: 'Search pillars…',
            prefixIcon: const Icon(Icons.search_rounded, size: 22),
            isDense: true,
            filled: true,
            fillColor: KaizenColors.surface,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 12,
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 38,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _FilterChip(
                label: 'All Pillars (${curriculum.pillars.length})',
                selected: trackId == 'all',
                onTap: () => onSelectTrack('all'),
              ),
              const SizedBox(width: 8),
              for (final t in kCurriculumTracks) ...[
                _FilterChip(
                  label: t.title,
                  selected: trackId == t.id,
                  onTap: () => onSelectTrack(t.id),
                ),
                const SizedBox(width: 8),
              ],
            ],
          ),
        ),
        const SizedBox(height: 14),
        for (final pillar in pillars) ...[
          _PillarCard(
            pillar: pillar,
            curriculum: curriculum,
            progress: progress,
            expanded: expandedPillars.contains(pillar.id),
            openNodes: openNodes,
            onToggle: () => onTogglePillar(pillar.id),
            onToggleNode: onToggleNode,
            onToggleLeaf: onToggleLeaf,
          ),
          const SizedBox(height: 10),
        ],
        if (pillars.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 28),
            child: Text(
              'No pillars match that search.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: KaizenColors.inkSoft,
              ),
            ),
          ),
        const SizedBox(height: 12),
      ],
    );
  }
}

class _MasteryQuotientCard extends StatelessWidget {
  const _MasteryQuotientCard({
    required this.done,
    required this.total,
    required this.pillarCount,
    required this.activeCycle,
  });

  final int done;
  final int total;
  final int pillarCount;
  final int activeCycle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final ratio = total == 0 ? 0.0 : done / total;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFF3F0FF), Color(0xFFE8E4FF), Color(0xFFFAF8FF)],
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: KaizenColors.primary.withValues(alpha: 0.16)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Atlas Quotient',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const Spacer(),
              Text(
                '$done / $total concepts',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: KaizenColors.primaryDeep,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: ratio,
              minHeight: 8,
              backgroundColor: Colors.white.withValues(alpha: 0.7),
              color: KaizenColors.primary,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _MetaPill(
                label: '$pillarCount Knowledge Pillars',
                tone: PillTone.primary,
              ),
              const SizedBox(width: 8),
              _MetaPill(
                label: '$activeCycle Active this cycle',
                tone: PillTone.secondary,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetaPill extends StatelessWidget {
  const _MetaPill({required this.label, required this.tone});

  final String label;
  final PillTone tone;

  @override
  Widget build(BuildContext context) {
    return PillChip(label: label, tone: tone);
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? KaizenColors.primaryDeep : KaizenColors.surface,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: selected
                ? KaizenColors.primaryDeep
                : KaizenColors.outlineVariant.withValues(alpha: 0.55),
          ),
          boxShadow: selected
              ? [
                  BoxShadow(
                    color: KaizenColors.primary.withValues(alpha: 0.22),
                    blurRadius: 10,
                    offset: const Offset(0, 3),
                  ),
                ]
              : null,
        ),
        child: Text(
          label,
          style: theme.textTheme.labelMedium?.copyWith(
            color: selected ? Colors.white : KaizenColors.inkMuted,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class _PillarCard extends StatelessWidget {
  const _PillarCard({
    required this.pillar,
    required this.curriculum,
    required this.progress,
    required this.expanded,
    required this.openNodes,
    required this.onToggle,
    required this.onToggleNode,
    required this.onToggleLeaf,
  });

  final Pillar pillar;
  final ForgeCurriculum curriculum;
  final Map<String, NodeState> progress;
  final bool expanded;
  final Set<String> openNodes;
  final VoidCallback onToggle;
  final ValueChanged<String> onToggleNode;
  final ValueChanged<String> onToggleLeaf;

  Color get _accent {
    final raw = pillar.accent.replaceFirst('#', '');
    if (raw.length != 6) return KaizenColors.primaryDeep;
    return Color(int.parse('FF$raw', radix: 16));
  }

  IconData get _icon {
    switch (pillar.id) {
      case 'math':
        return Icons.functions_rounded;
      case 'ml':
        return Icons.psychology_alt_rounded;
      case 'dl':
        return Icons.memory_rounded;
      case 'llm':
      case 'agents':
        return Icons.auto_awesome_rounded;
      case 'papers':
        return Icons.menu_book_rounded;
      case 'mlops':
        return Icons.cloud_sync_rounded;
      case 'trentorch':
        return Icons.local_fire_department_rounded;
      case 'systems':
      case 'corecs':
        return Icons.dns_rounded;
      case 'dsa':
        return Icons.account_tree_rounded;
      case 'sql':
        return Icons.storage_rounded;
      case 'sysdesign':
        return Icons.architecture_rounded;
      case 'comms':
      case 'career':
        return Icons.forum_rounded;
      case 'aptitude':
        return Icons.calculate_rounded;
      default:
        return Icons.hub_rounded;
    }
  }

  String get _tag {
    switch (pillar.id) {
      case 'math':
      case 'aptitude':
        return 'Foundations';
      case 'ml':
      case 'dl':
      case 'llm':
      case 'agents':
      case 'papers':
      case 'mlops':
      case 'trentorch':
        return 'AI / Systems';
      case 'systems':
      case 'corecs':
      case 'dsa':
      case 'sql':
      case 'sysdesign':
        return 'Core CS';
      case 'comms':
      case 'career':
        return 'Interview';
      default:
        return 'Pillar';
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final stats = curriculum.pillarStats(progress, pillar.id);
    final pct = stats.total == 0 ? 0 : ((stats.done / stats.total) * 100).round();
    final accent = _accent;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      decoration: BoxDecoration(
        color: KaizenColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: expanded
              ? KaizenColors.primary.withValues(alpha: 0.28)
              : KaizenColors.outlineVariant.withValues(alpha: 0.35),
        ),
        boxShadow: [
          BoxShadow(
            color: expanded
                ? KaizenColors.primary.withValues(alpha: 0.1)
                : const Color(0x0A131B2E),
            blurRadius: expanded ? 18 : 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          InkWell(
            onTap: onToggle,
            borderRadius: BorderRadius.circular(18),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(14, 14, 12, 14),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: accent.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Icon(_icon, color: accent, size: 22),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          pillar.title,
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w800,
                            letterSpacing: -0.2,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            PillChip(label: _tag, tone: PillTone.neutral),
                            const SizedBox(width: 8),
                            Flexible(
                              child: Text(
                                '${stats.done} / ${stats.total} concepts',
                                style: theme.textTheme.labelSmall?.copyWith(
                                  color: KaizenColors.inkSoft,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  _RingProgress(percent: pct, color: accent),
                  const SizedBox(width: 4),
                  AnimatedRotation(
                    turns: expanded ? 0.5 : 0,
                    duration: const Duration(milliseconds: 180),
                    child: Icon(
                      Icons.expand_more_rounded,
                      color: KaizenColors.inkSoft,
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (expanded) ...[
            const Divider(height: 1, color: Color(0xFFEAEAFF)),
            Padding(
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 12),
              child: Column(
                children: [
                  for (final root in pillar.roots)
                    _TopicBranch(
                      node: root,
                      depth: 0,
                      progress: progress,
                      openNodes: openNodes,
                      accent: accent,
                      onToggleNode: onToggleNode,
                      onToggleLeaf: onToggleLeaf,
                    ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _RingProgress extends StatelessWidget {
  const _RingProgress({required this.percent, required this.color});

  final int percent;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 42,
      height: 42,
      child: CustomPaint(
        painter: _RingPainter(
          progress: percent / 100,
          color: color,
          track: color.withValues(alpha: 0.15),
        ),
        child: Center(
          child: Text(
            '$percent%',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.w800,
              color: color,
              fontSize: 10,
            ),
          ),
        ),
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  _RingPainter({
    required this.progress,
    required this.color,
    required this.track,
  });

  final double progress;
  final Color color;
  final Color track;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 2.5;
    final trackPaint = Paint()
      ..color = track
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round;
    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, trackPaint);
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress.clamp(0.0, 1.0),
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _RingPainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.color != color;
  }
}

class _TopicBranch extends StatelessWidget {
  const _TopicBranch({
    required this.node,
    required this.depth,
    required this.progress,
    required this.openNodes,
    required this.accent,
    required this.onToggleNode,
    required this.onToggleLeaf,
  });

  final ForgeNode node;
  final int depth;
  final Map<String, NodeState> progress;
  final Set<String> openNodes;
  final Color accent;
  final ValueChanged<String> onToggleNode;
  final ValueChanged<String> onToggleLeaf;

  ({int done, int total}) _leafStats(ForgeNode n) {
    if (!n.hasChildren) {
      final s = progress[n.id] ?? NodeState.todo;
      final done = s == NodeState.done || s == NodeState.mastered ? 1 : 0;
      return (done: done, total: 1);
    }
    var done = 0;
    var total = 0;
    for (final c in n.children) {
      final s = _leafStats(c);
      done += s.done;
      total += s.total;
    }
    return (done: done, total: total);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasKids = node.hasChildren;
    final expanded = openNodes.contains(node.id);
    final state = progress[node.id] ?? NodeState.todo;
    final indent = depth * 10.0;

    if (!hasKids) {
      return Padding(
        padding: EdgeInsets.only(left: indent, bottom: 8),
        child: _ConceptLeaf(
          title: node.title,
          xp: node.xp ?? 12,
          state: state,
          onTap: () => onToggleLeaf(node.id),
        ),
      );
    }

    final stats = _leafStats(node);
    final ratio = stats.total == 0 ? 0.0 : stats.done / stats.total;
    final isRoot = depth == 0;

    return Padding(
      padding: EdgeInsets.only(left: indent, bottom: expanded ? 6 : 2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Material(
            color: isRoot
                ? KaizenColors.primaryWash.withValues(alpha: 0.45)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            child: InkWell(
              onTap: () => onToggleNode(node.id),
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: EdgeInsets.fromLTRB(
                  isRoot ? 10 : 4,
                  isRoot ? 10 : 8,
                  8,
                  isRoot ? 10 : 8,
                ),
                child: Row(
                  children: [
                    AnimatedRotation(
                      turns: expanded ? 0.25 : 0,
                      duration: const Duration(milliseconds: 160),
                      child: Icon(
                        Icons.play_arrow_rounded,
                        size: isRoot ? 18 : 16,
                        color: accent.withValues(alpha: 0.85),
                      ),
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        node.title,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: isRoot ? FontWeight.w800 : FontWeight.w700,
                          letterSpacing: -0.15,
                          color: KaizenColors.ink,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 46,
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(999),
                        child: LinearProgressIndicator(
                          value: ratio,
                          minHeight: 4,
                          backgroundColor: accent.withValues(alpha: 0.12),
                          color: accent,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${stats.done}/${stats.total}',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: KaizenColors.inkSoft,
                        fontWeight: FontWeight.w700,
                        fontFeatures: const [FontFeature.tabularFigures()],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          if (expanded)
            Padding(
              padding: const EdgeInsets.only(left: 8, top: 4),
              child: DecoratedBox(
                decoration: BoxDecoration(
                  border: Border(
                    left: BorderSide(
                      color: accent.withValues(alpha: 0.18),
                      width: 2,
                    ),
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.only(left: 10),
                  child: Column(
                    children: [
                      for (final child in node.children)
                        _TopicBranch(
                          node: child,
                          depth: depth + 1,
                          progress: progress,
                          openNodes: openNodes,
                          accent: accent,
                          onToggleNode: onToggleNode,
                          onToggleLeaf: onToggleLeaf,
                        ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _ConceptLeaf extends StatelessWidget {
  const _ConceptLeaf({
    required this.title,
    required this.xp,
    required this.state,
    required this.onTap,
  });

  final String title;
  final int xp;
  final NodeState state;
  final VoidCallback onTap;

  Color get _stateColor {
    switch (state) {
      case NodeState.todo:
        return KaizenColors.inkSoft;
      case NodeState.learning:
        return const Color(0xFF0D9488);
      case NodeState.done:
        return KaizenColors.primaryDeep;
      case NodeState.mastered:
        return const Color(0xFFB45309);
    }
  }

  Color get _wash {
    switch (state) {
      case NodeState.todo:
        return KaizenColors.surface;
      case NodeState.learning:
        return KaizenColors.secondaryWash;
      case NodeState.done:
        return KaizenColors.primaryWash;
      case NodeState.mastered:
        return KaizenColors.tertiaryWash;
    }
  }

  String get _label {
    switch (state) {
      case NodeState.todo:
        return 'Todo';
      case NodeState.learning:
        return 'Learning';
      case NodeState.done:
        return 'Done';
      case NodeState.mastered:
        return 'Mastered';
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = _stateColor;
    final complete = state == NodeState.done || state == NodeState.mastered;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Ink(
          decoration: BoxDecoration(
            color: _wash,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: state == NodeState.todo
                  ? KaizenColors.outlineVariant.withValues(alpha: 0.45)
                  : color.withValues(alpha: 0.28),
            ),
            boxShadow: [
              BoxShadow(
                color: color.withValues(alpha: state == NodeState.todo ? 0.04 : 0.08),
                blurRadius: 10,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  width: 4,
                  decoration: BoxDecoration(
                    color: state == NodeState.todo
                        ? KaizenColors.outlineVariant.withValues(alpha: 0.55)
                        : color,
                    borderRadius: const BorderRadius.horizontal(
                      left: Radius.circular(14),
                    ),
                  ),
                ),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(12, 11, 12, 11),
                    child: Row(
                      children: [
                        _StateGlyph(state: state, color: color),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                title,
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: -0.2,
                                  height: 1.2,
                                  color: complete
                                      ? KaizenColors.inkMuted
                                      : KaizenColors.ink,
                                  decoration: complete
                                      ? TextDecoration.lineThrough
                                      : null,
                                  decorationColor: KaizenColors.inkSoft,
                                ),
                              ),
                              const SizedBox(height: 3),
                              Text(
                                '+$xp XP · tap to advance',
                                style: theme.textTheme.labelSmall?.copyWith(
                                  color: KaizenColors.inkSoft,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 9,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: color.withValues(
                              alpha: state == NodeState.todo ? 0.08 : 0.14,
                            ),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: Text(
                            _label,
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: color,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.1,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _StateGlyph extends StatelessWidget {
  const _StateGlyph({required this.state, required this.color});

  final NodeState state;
  final Color color;

  @override
  Widget build(BuildContext context) {
    switch (state) {
      case NodeState.done:
      case NodeState.mastered:
        return Container(
          width: 26,
          height: 26,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: color.withValues(alpha: 0.28),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Icon(
            state == NodeState.mastered
                ? Icons.workspace_premium_rounded
                : Icons.check_rounded,
            size: 15,
            color: Colors.white,
          ),
        );
      case NodeState.learning:
        return Container(
          width: 26,
          height: 26,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: 0.12),
            border: Border.all(color: color, width: 2),
          ),
          child: Center(
            child: Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
          ),
        );
      case NodeState.todo:
        return Container(
          width: 26,
          height: 26,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white,
            border: Border.all(
              color: KaizenColors.outlineVariant,
              width: 1.8,
            ),
          ),
        );
    }
  }
}
