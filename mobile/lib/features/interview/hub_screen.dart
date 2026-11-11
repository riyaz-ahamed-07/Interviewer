import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../forge/forge_scope.dart';
import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class _Room {
  const _Room({
    required this.title,
    required this.roundId,
    required this.tag,
    required this.blurb,
    required this.icon,
    required this.wash,
    required this.iconBg,
    this.featured = false,
    this.badge,
  });

  final String title;
  final String roundId;
  final String tag;
  final String blurb;
  final IconData icon;
  final Color wash;
  final Color iconBg;
  final bool featured;
  final String? badge;
}

class InterviewHubScreen extends StatelessWidget {
  const InterviewHubScreen({super.key});

  static const _featured = [
    _Room(
      title: 'Soft Mock',
      roundId: 'cs_fundamentals',
      tag: '#SOFT',
      blurb: '15m Socratic whiteboard probe',
      icon: Icons.record_voice_over_rounded,
      wash: Color(0xFFEDE9FE),
      iconBg: Color(0xFFDDD6FE),
      featured: true,
      badge: 'Staff L6',
    ),
    _Room(
      title: 'Design Board',
      roundId: 'hld_system_design',
      tag: '#HLD',
      blurb: 'Distributed systems + telemetry',
      icon: Icons.account_tree_rounded,
      wash: Color(0xFFCCFBF1),
      iconBg: Color(0xFF99F6E4),
      featured: true,
      badge: 'HLD',
    ),
    _Room(
      title: 'Knowledge Fire',
      roundId: 'cs_fundamentals',
      tag: '#KF',
      blurb: 'Rapid-fire trade-off blitz',
      icon: Icons.local_fire_department_rounded,
      wash: Color(0xFFFEF3C7),
      iconBg: Color(0xFFFDE68A),
      featured: true,
      badge: 'Blitz',
    ),
  ];

  static const _rooms = [
    _Room(
      title: 'OA',
      roundId: 'online_assessment',
      tag: '#OA-01',
      blurb: '45m · Proctored matrix',
      icon: Icons.grid_on_rounded,
      wash: Color(0xFFF3F0FF),
      iconBg: Color(0xFFE9E3FF),
    ),
    _Room(
      title: 'DSA',
      roundId: 'dsa_live_coding',
      tag: '#DSA-02',
      blurb: 'Graphs & DP',
      icon: Icons.hub_rounded,
      wash: Color(0xFFF3F0FF),
      iconBg: Color(0xFFE9E3FF),
    ),
    _Room(
      title: 'Machine Coding',
      roundId: 'machine_coding',
      tag: '#MC-03',
      blurb: 'Clean OOP build',
      icon: Icons.code_rounded,
      wash: Color(0xFFF3F0FF),
      iconBg: Color(0xFFE9E3FF),
    ),
    _Room(
      title: 'Pair',
      roundId: 'pair_programming',
      tag: '#PAIR-04',
      blurb: 'Concurrent refactor',
      icon: Icons.people_alt_rounded,
      wash: Color(0xFFF3F0FF),
      iconBg: Color(0xFFE9E3FF),
    ),
    _Room(
      title: 'Take-home',
      roundId: 'take_home_review',
      tag: '#TH-05',
      blurb: 'Repo defense',
      icon: Icons.folder_open_rounded,
      wash: Color(0xFFF3F0FF),
      iconBg: Color(0xFFE9E3FF),
    ),
    _Room(
      title: 'ML Debug',
      roundId: 'ml_pytorch_coding_debug',
      tag: '#MLD-06',
      blurb: 'CUDA & autograd',
      icon: Icons.bug_report_rounded,
      wash: Color(0xFFECFDF5),
      iconBg: Color(0xFFD1FAE5),
    ),
    _Room(
      title: 'AI Pair',
      roundId: 'ai_assisted_coding',
      tag: '#AIP-07',
      blurb: 'Prompt-to-code',
      icon: Icons.auto_awesome_rounded,
      wash: Color(0xFFECFDF5),
      iconBg: Color(0xFFD1FAE5),
    ),
    _Room(
      title: 'Design Board',
      roundId: 'hld_system_design',
      tag: '#HLD-08',
      blurb: 'Distributed HLD',
      icon: Icons.account_tree_outlined,
      wash: Color(0xFFEEF2FF),
      iconBg: Color(0xFFE0E7FF),
    ),
    _Room(
      title: 'LLD',
      roundId: 'lld_ood',
      tag: '#LLD-09',
      blurb: 'Patterns & schema',
      icon: Icons.architecture_rounded,
      wash: Color(0xFFEEF2FF),
      iconBg: Color(0xFFE0E7FF),
    ),
    _Room(
      title: 'Frontend Design',
      roundId: 'frontend_system_design',
      tag: '#FED-10',
      blurb: 'DOM & vitals',
      icon: Icons.web_rounded,
      wash: Color(0xFFEEF2FF),
      iconBg: Color(0xFFE0E7FF),
    ),
    _Room(
      title: 'Knowledge Fire',
      roundId: 'cs_fundamentals',
      tag: '#KF-11',
      blurb: '10m blitz',
      icon: Icons.flash_on_rounded,
      wash: Color(0xFFFFF7ED),
      iconBg: Color(0xFFFFEDD5),
    ),
    _Room(
      title: 'ML Maths',
      roundId: 'ml_depth_maths',
      tag: '#MATH-12',
      blurb: 'Softmax & loss',
      icon: Icons.functions_rounded,
      wash: Color(0xFFECFDF5),
      iconBg: Color(0xFFD1FAE5),
    ),
    _Room(
      title: 'Behavioral',
      roundId: 'behavioral_star',
      tag: '#BEH-13',
      blurb: 'STAR bar-raiser',
      icon: Icons.forum_rounded,
      wash: Color(0xFFFFF1F2),
      iconBg: Color(0xFFFFE4E6),
    ),
    _Room(
      title: 'Resume Dive',
      roundId: 'project_resume_deep_dive',
      tag: '#RES-14',
      blurb: 'Authorship audit',
      icon: Icons.description_rounded,
      wash: Color(0xFFFFF1F2),
      iconBg: Color(0xFFFFE4E6),
    ),
    _Room(
      title: 'Research',
      roundId: 'research_paper_discussion',
      tag: '#RSCH-15',
      blurb: 'arXiv defense',
      icon: Icons.menu_book_rounded,
      wash: Color(0xFFECFDF5),
      iconBg: Color(0xFFD1FAE5),
    ),
    _Room(
      title: 'People Ops',
      roundId: 'recruiter_screen',
      tag: '#PO-16',
      blurb: 'Comp & anchor',
      icon: Icons.handshake_rounded,
      wash: Color(0xFFFFF1F2),
      iconBg: Color(0xFFFFE4E6),
    ),
  ];

  void _openRoom(BuildContext context, _Room room) {
    context.push(
      '/interview/setup',
      extra: {'roundId': room.roundId, 'title': room.title},
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final streak = ForgeScope.storeOf(context).streak;

    return Scaffold(
      backgroundColor: KaizenColors.canvas,
      appBar: const KaizenTopBar(subtitle: 'Arena'),
      body: SoftPagePadding(
        child: ListView(
          children: [
            Text(
              'Interview Arena',
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w800,
                letterSpacing: -0.8,
                height: 1.05,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Pick a room. Step in sharp.',
              style: theme.textTheme.bodyLarge?.copyWith(
                color: KaizenColors.inkMuted,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF3C7),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(
                      color: const Color(0xFFF59E0B).withValues(alpha: 0.28),
                    ),
                  ),
                  child: Text(
                    streak > 0
                        ? '🔥 $streak-day streak · ready'
                        : '✨ Ready when you are',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: const Color(0xFFB45309),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => context.push('/interview/setup'),
                    icon: const Icon(Icons.tune_rounded, size: 18),
                    label: const Text('Configure session'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                TextButton(
                  onPressed: () => context.push('/interview/presets'),
                  child: Text(
                    'Presets',
                    style: theme.textTheme.labelLarge?.copyWith(
                      color: KaizenColors.primaryDeep,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 22),
            Row(
              children: [
                Text(
                  'Featured rooms',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const Spacer(),
                Text(
                  'Swipe',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: KaizenColors.inkSoft,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 132,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _featured.length,
                separatorBuilder: (_, _) => const SizedBox(width: 10),
                itemBuilder: (context, i) {
                  final room = _featured[i];
                  return SizedBox(
                    width: 220,
                    child: Material(
                      color: room.wash,
                      borderRadius: BorderRadius.circular(20),
                      child: InkWell(
                        borderRadius: BorderRadius.circular(20),
                        onTap: () => _openRoom(context, room),
                        child: Padding(
                          padding: const EdgeInsets.all(14),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    width: 36,
                                    height: 36,
                                    decoration: BoxDecoration(
                                      color: room.iconBg,
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Icon(
                                      room.icon,
                                      color: KaizenColors.primaryDeep,
                                      size: 20,
                                    ),
                                  ),
                                  const Spacer(),
                                  if (room.badge != null)
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 4,
                                      ),
                                      decoration: BoxDecoration(
                                        color: Colors.white.withValues(
                                          alpha: 0.72,
                                        ),
                                        borderRadius: BorderRadius.circular(999),
                                      ),
                                      child: Text(
                                        room.badge!,
                                        style:
                                            theme.textTheme.labelSmall?.copyWith(
                                          fontWeight: FontWeight.w700,
                                          color: KaizenColors.primaryDeep,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                              const Spacer(),
                              Text(
                                room.title,
                                style: theme.textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                room.blurb,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: KaizenColors.inkMuted,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 22),
            Text(
              '16 specialized rooms',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 10),
            LayoutBuilder(
              builder: (context, constraints) {
                final width = (constraints.maxWidth - 10) / 2;
                return Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    for (final room in _rooms)
                      SizedBox(
                        width: width,
                        child: Material(
                          color: room.wash,
                          borderRadius: BorderRadius.circular(20),
                          child: InkWell(
                            borderRadius: BorderRadius.circular(20),
                            onTap: () => _openRoom(context, room),
                            child: Padding(
                              padding: const EdgeInsets.all(12),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    width: 34,
                                    height: 34,
                                    decoration: BoxDecoration(
                                      color: room.iconBg,
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Icon(
                                      room.icon,
                                      size: 18,
                                      color: KaizenColors.primaryDeep,
                                    ),
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    room.title,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: theme.textTheme.titleSmall?.copyWith(
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    room.tag,
                                    style: theme.textTheme.labelSmall?.copyWith(
                                      color: KaizenColors.inkSoft,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    room.blurb,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: theme.textTheme.bodySmall?.copyWith(
                                      color: KaizenColors.inkMuted,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                );
              },
            ),
            const SizedBox(height: 88),
          ],
        ),
      ),
    );
  }
}
