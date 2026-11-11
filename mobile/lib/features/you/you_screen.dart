import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../forge/forge_scope.dart';
import '../../forge/profile.dart';
import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class YouScreen extends StatelessWidget {
  const YouScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final store = ForgeScope.storeOf(context);
    final curriculum = ForgeScope.curriculumOf(context);
    final level = store.level;
    final mastery = store.overallMastery(curriculum);
    final masteryPct =
        mastery.total == 0 ? 0 : ((mastery.done / mastery.total) * 100).round();
    final profile = KaizenProfile.current;

    return Scaffold(
      backgroundColor: KaizenColors.canvas,
      appBar: AppBar(
        title: const Text('You'),
        actions: [
          IconButton(
            onPressed: () => context.push('/settings'),
            icon: const Icon(Icons.settings_outlined),
          ),
        ],
      ),
      body: SoftPagePadding(
        child: ListView(
          children: [
            KaizenCard(
              child: Column(
                children: [
                  const RaeezAvatar(size: 96),
                  const SizedBox(height: 12),
                  Text(
                    profile.displayName,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${profile.roleLabel}  ·  ${profile.handle}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: KaizenColors.inkMuted,
                    ),
                  ),
                  const SizedBox(height: 10),
                  PillChip(
                    label: '⚡  Lvl ${level.level} · ${level.title}',
                  ),
                  const SizedBox(height: 16),
                  const Divider(height: 1),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Text(
                        'Progress to Level ${level.level + (level.progress >= 1 ? 0 : 1)}',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: KaizenColors.inkMuted,
                        ),
                      ),
                      const Spacer(),
                      Text.rich(
                        TextSpan(
                          style: theme.textTheme.labelSmall,
                          children: [
                            TextSpan(
                              text: '${store.xp} ',
                              style: const TextStyle(
                                color: KaizenColors.primaryDeep,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            TextSpan(
                              text: '/ ${level.nextXp} XP',
                              style: const TextStyle(color: KaizenColors.inkSoft),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(999),
                    child: LinearProgressIndicator(
                      value: level.progress,
                      minHeight: 8,
                      backgroundColor: KaizenColors.surfaceContainer,
                      color: KaizenColors.primary,
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: _MetricTile(
                          emoji: '🔥',
                          value: '${store.streak}',
                          label: 'Day Streak',
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _MetricTile(
                          icon: Icons.stars,
                          value: _compactXp(store.xp),
                          label: 'Total XP',
                          color: KaizenColors.primaryDeep,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _MetricTile(
                          icon: Icons.ac_unit,
                          value: '${store.freezeLeft}',
                          label: 'Freezes left',
                          color: KaizenColors.secondary,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _MetricTile(
                          icon: Icons.psychology,
                          value: '$masteryPct%',
                          label: 'Atlas Q',
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                const Icon(
                  Icons.timelapse,
                  color: KaizenColors.primaryDeep,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Sacred Focus Windows',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Spacer(),
                const PillChip(
                  label: 'Optimal Flow',
                  tone: PillTone.secondary,
                ),
              ],
            ),
            const SizedBox(height: 10),
            KaizenCard(
              borderColor: KaizenColors.primary.withValues(alpha: 0.2),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    FocusWindows.tonight.practiceRanges,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${FocusWindows.tonight.protectedRange}: ${FocusWindows.tonight.protectedLabel}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: KaizenColors.inkMuted,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  static String _compactXp(int xp) {
    if (xp >= 1000) {
      final v = xp / 1000;
      return v >= 10 ? '${v.round()}k' : '${v.toStringAsFixed(1)}k';
    }
    return '$xp';
  }
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({
    required this.value,
    required this.label,
    this.emoji,
    this.icon,
    this.color = KaizenColors.ink,
  });

  final String value;
  final String label;
  final String? emoji;
  final IconData? icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
      decoration: BoxDecoration(
        color: KaizenColors.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          if (emoji != null)
            Text(emoji!, style: const TextStyle(fontSize: 14))
          else if (icon != null)
            Icon(icon, size: 16, color: color),
          const SizedBox(height: 4),
          Text(
            value,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
          Text(
            label,
            textAlign: TextAlign.center,
            style: theme.textTheme.labelSmall?.copyWith(
              color: KaizenColors.inkSoft,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
}
