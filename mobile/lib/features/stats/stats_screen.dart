import 'package:flutter/material.dart';

import '../../forge/forge_scope.dart';
import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class StatsScreen extends StatelessWidget {
  const StatsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final store = ForgeScope.storeOf(context);
    final curriculum = ForgeScope.curriculumOf(context);
    final level = store.level;
    final lanes = store.laneWeekStats(curriculum);
    final heat = store.heatmapCounts(curriculum);
    final mastery = store.overallMastery(curriculum);
    final practiceRatio = lanes.practiceTotal == 0
        ? 0.0
        : lanes.practiceDone / lanes.practiceTotal;
    final conceptRatio = lanes.conceptTotal == 0
        ? 0.0
        : lanes.conceptDone / lanes.conceptTotal;

    final days = List.generate(35, (i) {
      final d = DateTime.now().subtract(Duration(days: 34 - i));
      final key =
          '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
      return (date: d, count: heat[key] ?? 0);
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Stats'),
      ),
      body: SoftPagePadding(
        child: ListView(
          physics: const ClampingScrollPhysics(),
          children: [
            Text(
              'Signals',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Streak, calendar heat, and lane balance.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: KaizenColors.inkSoft,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _BigStat(
                    label: 'Streak',
                    value: '${store.streak}',
                    sub: 'Best ${store.bestStreak}',
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _BigStat(
                    label: 'XP',
                    value: '${store.xp}',
                    sub: 'Lvl ${level.level} · ${level.title}',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            KaizenCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Level progress',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 10),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(999),
                    child: LinearProgressIndicator(
                      value: level.progress,
                      minHeight: 10,
                      backgroundColor: KaizenColors.surfaceContainer,
                      color: KaizenColors.primary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${store.xp} / ${level.nextXp} XP',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: KaizenColors.inkSoft,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            KaizenCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Activity heatmap · 5 weeks',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 4,
                    runSpacing: 4,
                    children: [
                      for (final day in days)
                        Tooltip(
                          message:
                              '${day.date.day}/${day.date.month}: ${day.count} checks',
                          child: Container(
                            width: 14,
                            height: 14,
                            decoration: BoxDecoration(
                              color: _heatColor(day.count),
                              borderRadius: BorderRadius.circular(3),
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            KaizenCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'This week · lanes',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 14),
                  _LaneBar(
                    label: 'Practice',
                    done: lanes.practiceDone,
                    total: lanes.practiceTotal,
                    ratio: practiceRatio,
                    color: KaizenColors.primaryDeep,
                  ),
                  const SizedBox(height: 12),
                  _LaneBar(
                    label: 'Concepts',
                    done: lanes.conceptDone,
                    total: lanes.conceptTotal,
                    ratio: conceptRatio,
                    color: KaizenColors.secondary,
                  ),
                  const SizedBox(height: 14),
                  Text(
                    practiceRatio + 0.001 >= conceptRatio
                        ? 'Practice is ahead — protect concept depth tonight.'
                        : 'Concepts are ahead — keep a practice rep in the first window.',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: KaizenColors.inkMuted,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            KaizenCard(
              child: SectionHeader(
                title: 'Atlas quotient',
                subtitle:
                    '${mastery.done}/${mastery.total} leaves · ${mastery.total == 0 ? 0 : ((mastery.done / mastery.total) * 100).round()}%',
              ),
            ),
            const SizedBox(height: 12),
            KaizenCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Month calendar',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 10),
                  _MiniCalendar(heat: heat),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Color _heatColor(int count) {
    if (count <= 0) return KaizenColors.surfaceContainer;
    if (count == 1) return const Color(0xFFDDD6FE);
    if (count == 2) return const Color(0xFFC4B5FD);
    if (count == 3) return const Color(0xFFA78BFA);
    return KaizenColors.primaryDeep;
  }
}

class _BigStat extends StatelessWidget {
  const _BigStat({
    required this.label,
    required this.value,
    required this.sub,
  });

  final String label;
  final String value;
  final String sub;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return KaizenCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(
              color: KaizenColors.inkSoft,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
          Text(
            sub,
            style: theme.textTheme.labelSmall?.copyWith(
              color: KaizenColors.inkMuted,
            ),
          ),
        ],
      ),
    );
  }
}

class _LaneBar extends StatelessWidget {
  const _LaneBar({
    required this.label,
    required this.done,
    required this.total,
    required this.ratio,
    required this.color,
  });

  final String label;
  final int done;
  final int total;
  final double ratio;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              label,
              style: theme.textTheme.labelLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const Spacer(),
            Text(
              '$done / $total',
              style: theme.textTheme.labelMedium?.copyWith(
                color: KaizenColors.inkSoft,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: LinearProgressIndicator(
            value: ratio.clamp(0.0, 1.0),
            minHeight: 10,
            backgroundColor: KaizenColors.surfaceContainer,
            color: color,
          ),
        ),
      ],
    );
  }
}

class _MiniCalendar extends StatelessWidget {
  const _MiniCalendar({required this.heat});

  final Map<String, int> heat;

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final first = DateTime(now.year, now.month, 1);
    final daysInMonth = DateTime(now.year, now.month + 1, 0).day;
    final startOffset = (first.weekday + 6) % 7;
    final theme = Theme.of(context);

    return Column(
      children: [
        Row(
          children: [
            for (final d in ['M', 'T', 'W', 'T', 'F', 'S', 'S'])
              Expanded(
                child: Center(
                  child: Text(
                    d,
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: KaizenColors.inkSoft,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: startOffset + daysInMonth,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 7,
            mainAxisSpacing: 6,
            crossAxisSpacing: 6,
          ),
          itemBuilder: (context, index) {
            if (index < startOffset) return const SizedBox.shrink();
            final day = index - startOffset + 1;
            final date = DateTime(now.year, now.month, day);
            final key =
                '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
            final count = heat[key] ?? 0;
            final isToday = day == now.day;
            return Container(
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: count > 0
                    ? KaizenColors.primaryWash
                    : KaizenColors.surfaceContainerLow,
                borderRadius: BorderRadius.circular(10),
                border: isToday
                    ? Border.all(color: KaizenColors.primaryDeep)
                    : null,
              ),
              child: Text(
                '$day',
                style: theme.textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: count > 0
                      ? KaizenColors.primaryDeep
                      : KaizenColors.inkMuted,
                ),
              ),
            );
          },
        ),
      ],
    );
  }
}
