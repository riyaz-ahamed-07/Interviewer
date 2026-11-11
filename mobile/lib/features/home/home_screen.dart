import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../forge/curriculum.dart';
import '../../forge/forge_scope.dart';
import '../../forge/progress.dart';
import '../../forge/schedule.dart';
import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final store = ForgeScope.storeOf(context);
      final curriculum = ForgeScope.curriculumOf(context);
      await store.reconcileCarryForward(curriculum);
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final store = ForgeScope.storeOf(context);
    final curriculum = ForgeScope.curriculumOf(context);
    final todos = ForgeScope.todosOf(context);
    final level = store.level;
    final today = curriculum.todayPlanDay();
    final dateKey = curriculum.todayDateKey();
    final composed = store.composedTodayItems(today);
    final todayStats = store.todayTaskStats(composed, dateKey);
    final streakLit = todayStats.done > 0;
    final weekDots = _weekDots(curriculum, store);
    final windows = scheduleTasksForEvening(
      composed,
      carriedFrom: store.carriedFromMap(),
    );
    final practiceWindows =
        windows.where((w) => w.item.lane == 'practice').toList();
    final conceptWindows =
        windows.where((w) => w.item.lane == 'concept').toList();
    final openTodos = todos.openItems.take(3).toList();

    return Scaffold(
      backgroundColor: KaizenColors.canvas,
      appBar: const KaizenTopBar(),
      body: SoftPagePadding(
        child: ListView(
          physics: const ClampingScrollPhysics(),
          children: [
            Text(
              today?.label ?? 'Today',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
                letterSpacing: -0.5,
                height: 1.1,
              ),
            ),
            const SizedBox(height: 12),
            _MomentumCard(
              streak: store.streak,
              streakActive: streakLit,
              level: level.level,
              levelTitle: level.title,
              xp: store.xp,
              nextXp: level.nextXp,
              progress: level.progress,
              weekDots: weekDots,
              onTap: () => context.push('/stats'),
            ),
            if (practiceWindows.isNotEmpty) ...[
              const SizedBox(height: 16),
              _LaneHeader(
                color: KaizenColors.primaryContainer,
                title: 'Practice',
                meta: '${practiceWindows.length} · timed',
                tone: PillTone.primary,
              ),
              const SizedBox(height: 10),
              for (final window in practiceWindows) ...[
                _TimedTaskCard(
                  window: window,
                  done: store.isWeekTaskDone(dateKey, window.item.id),
                  onToggle: () => store.toggleWeekTask(dateKey, window.item.id),
                ),
                const SizedBox(height: 10),
              ],
            ],
            if (conceptWindows.isNotEmpty) ...[
              const SizedBox(height: 8),
              _LaneHeader(
                color: KaizenColors.secondary,
                title: 'Concepts',
                meta: '${conceptWindows.length} · timed',
                tone: PillTone.secondary,
              ),
              const SizedBox(height: 10),
              for (final window in conceptWindows) ...[
                _TimedTaskCard(
                  window: window,
                  done: store.isWeekTaskDone(dateKey, window.item.id),
                  onToggle: () => store.toggleWeekTask(dateKey, window.item.id),
                  tone: PillTone.secondary,
                  checkboxColor: KaizenColors.secondary,
                ),
                const SizedBox(height: 10),
              ],
            ],
            if (openTodos.isNotEmpty) ...[
              const SizedBox(height: 8),
              _LaneHeader(
                color: KaizenColors.tertiary,
                title: 'Personal to-dos',
                meta: '${todos.openItems.length} open',
                tone: PillTone.tertiary,
              ),
              const SizedBox(height: 10),
              for (final todo in openTodos) ...[
                KaizenCard(
                  onTap: () => context.push('/todos'),
                  padding: const EdgeInsets.all(14),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          todo.title,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      if (todo.deadline != null)
                        PillChip(
                          label:
                              'Due ${todo.deadline!.day}/${todo.deadline!.month}',
                          tone: PillTone.neutral,
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),
              ],
            ],
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  static List<({String label, bool done})> _weekDots(
    ForgeCurriculum curriculum,
    ForgeProgressStore store,
  ) {
    const labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    final now = DateTime.now();
    final start = DateTime(now.year, now.month, now.day)
        .subtract(Duration(days: now.weekday % 7));
    final heat = store.heatmapCounts(curriculum, days: 14);
    return List.generate(7, (i) {
      final day = start.add(Duration(days: i));
      final key = curriculum.todayDateKey(day);
      return (label: labels[i], done: (heat[key] ?? 0) > 0);
    });
  }
}

class _MomentumCard extends StatelessWidget {
  const _MomentumCard({
    required this.streak,
    required this.streakActive,
    required this.level,
    required this.levelTitle,
    required this.xp,
    required this.nextXp,
    required this.progress,
    required this.weekDots,
    this.onTap,
  });

  final int streak;
  final bool streakActive;
  final int level;
  final String levelTitle;
  final int xp;
  final int nextXp;
  final double progress;
  final List<({String label, bool done})> weekDots;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dayLabel = streak == 1 ? 'Day' : 'Days';
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(22),
        child: Ink(
          padding: const EdgeInsets.fromLTRB(14, 14, 14, 12),
          decoration: BoxDecoration(
            color: KaizenColors.surface,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(
              color: KaizenColors.outlineVariant.withValues(alpha: 0.35),
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x147C5CFC),
                blurRadius: 18,
                offset: Offset(0, 6),
              ),
            ],
          ),
          child: IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(
                  width: 78,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: streakActive
                              ? const Color(0xFFFFE4D6)
                              : KaizenColors.surfaceContainerLow,
                          boxShadow: streakActive
                              ? [
                                  BoxShadow(
                                    color: const Color(0x66F97316),
                                    blurRadius: 14,
                                    spreadRadius: 1,
                                  ),
                                ]
                              : null,
                        ),
                        child: Icon(
                          Icons.local_fire_department_rounded,
                          size: 28,
                          color: streakActive
                              ? const Color(0xFFEA580C)
                              : KaizenColors.inkSoft.withValues(alpha: 0.55),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text.rich(
                        TextSpan(
                          children: [
                            TextSpan(
                              text: '$streak',
                              style: theme.textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.w900,
                                letterSpacing: -0.6,
                                height: 1,
                              ),
                            ),
                            TextSpan(
                              text: ' $dayLabel',
                              style: theme.textTheme.labelLarge?.copyWith(
                                color: KaizenColors.inkMuted,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'STREAK',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: KaizenColors.inkSoft,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.2,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                ),
                VerticalDivider(
                  width: 20,
                  thickness: 1,
                  color: KaizenColors.outlineVariant.withValues(alpha: 0.45),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 26,
                            height: 26,
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(8),
                              gradient: const LinearGradient(
                                colors: [
                                  KaizenColors.primary,
                                  Color(0xFFEC4899),
                                ],
                              ),
                            ),
                            child: const Icon(
                              Icons.star_rounded,
                              size: 16,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Level $level',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              levelTitle,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: theme.textTheme.labelLarge?.copyWith(
                                color: KaizenColors.inkSoft,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      _XpBar(
                        progress: progress,
                        label: '$xp / $nextXp XP',
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          for (final day in weekDots)
                            Column(
                              children: [
                                Container(
                                  width: 22,
                                  height: 22,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    gradient: day.done
                                        ? const LinearGradient(
                                            colors: [
                                              KaizenColors.primary,
                                              Color(0xFFEC4899),
                                            ],
                                          )
                                        : null,
                                    color: day.done
                                        ? null
                                        : KaizenColors.surfaceContainer,
                                  ),
                                  child: Icon(
                                    Icons.check_rounded,
                                    size: 13,
                                    color: day.done
                                        ? Colors.white
                                        : KaizenColors.inkSoft
                                            .withValues(alpha: 0.45),
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  day.label,
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    color: KaizenColors.inkSoft,
                                    fontSize: 9,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                        ],
                      ),
                    ],
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

class _XpBar extends StatelessWidget {
  const _XpBar({required this.progress, required this.label});

  final double progress;
  final String label;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: SizedBox(
        height: 28,
        child: Stack(
          fit: StackFit.expand,
          children: [
            ColoredBox(color: KaizenColors.surfaceContainer),
            FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: progress.clamp(0.0, 1.0),
              child: const DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [KaizenColors.primary, Color(0xFFEC4899)],
                  ),
                ),
              ),
            ),
            Center(
              child: Text(
                label,
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                  shadows: const [
                    Shadow(
                      color: Color(0x66000000),
                      blurRadius: 4,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LaneHeader extends StatelessWidget {
  const _LaneHeader({
    required this.color,
    required this.title,
    required this.meta,
    required this.tone,
  });

  final Color color;
  final String title;
  final String meta;
  final PillTone tone;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
        const Spacer(),
        PillChip(label: meta, tone: tone),
      ],
    );
  }
}

class _TimedTaskCard extends StatelessWidget {
  const _TimedTaskCard({
    required this.window,
    required this.done,
    required this.onToggle,
    this.tone = PillTone.primary,
    this.checkboxColor = KaizenColors.primary,
  });

  final TaskWindow window;
  final bool done;
  final VoidCallback onToggle;
  final PillTone tone;
  final Color checkboxColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final item = window.item;
    return KaizenCard(
      padding: const EdgeInsets.all(14),
      borderColor: tone == PillTone.secondary
          ? KaizenColors.secondary.withValues(alpha: 0.2)
          : KaizenColors.primary.withValues(alpha: 0.15),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: HabitCheckbox(
              done: done,
              onChanged: (_) => onToggle(),
              color: checkboxColor,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    decoration: done ? TextDecoration.lineThrough : null,
                    color: done ? KaizenColors.inkSoft : KaizenColors.ink,
                  ),
                ),
                const SizedBox(height: 6),
                Wrap(
                  spacing: 8,
                  runSpacing: 6,
                  children: [
                    PillChip(label: window.rangeLabel, tone: PillTone.neutral),
                    PillChip(label: '~${item.estMin}m', tone: tone),
                    if (window.carriedFromDateKey != null)
                      const PillChip(
                        label: 'Carried',
                        tone: PillTone.tertiary,
                      ),
                  ],
                ),
              ],
            ),
          ),
          IconButton(
            visualDensity: VisualDensity.compact,
            onPressed: () {
              showDialog<void>(
                context: context,
                builder: (context) {
                  return AlertDialog(
                    title: Text(item.title),
                    content: Text(taskBrief(item)),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('Got it'),
                      ),
                    ],
                  );
                },
              );
            },
            icon: const Icon(Icons.info_outline_rounded, size: 20),
            color: KaizenColors.inkSoft,
          ),
        ],
      ),
    );
  }
}
