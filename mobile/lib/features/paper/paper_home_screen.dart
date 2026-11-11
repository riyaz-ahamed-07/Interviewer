import 'package:flutter/material.dart';

import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class PaperHomeScreen extends StatelessWidget {
  const PaperHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: const KaizenTopBar(),
      body: SoftPagePadding(
        child: ListView(
          children: [
            KaizenCard(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const RaeezAvatar(size: 52),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                "Dr. Delta's Paper Stacks",
                                style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                            const PillChip(
                              label: 'Synthesis',
                              tone: PillTone.secondary,
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Distilling deep literature into core intuitions.',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: KaizenColors.inkMuted,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: KaizenColors.surfaceContainerLow,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.lightbulb_outline,
                                size: 18,
                                color: KaizenColors.primaryDeep,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'Raeez says: "Read the methodology section with a skeptic\'s eye."',
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            KaizenCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.add_circle, color: KaizenColors.primaryDeep),
                      const SizedBox(width: 8),
                      Text(
                        'Add Research Paper',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        'arXiv / PDF',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: KaizenColors.inkSoft,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    decoration: InputDecoration(
                      hintText: 'Paste arXiv link (e.g. arxiv.org/abs/...)',
                      prefixIcon: const Icon(Icons.link),
                      suffixIcon: IconButton(
                        onPressed: () {},
                        icon: const Icon(Icons.content_paste),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.arrow_forward, size: 16),
                          label: const Text('Ingest & Distill'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.upload_file, size: 18),
                        label: const Text('Upload PDF'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                Text(
                  'Papers in flight',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  width: 22,
                  height: 22,
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(
                    color: Color(0xFFE6DEFF),
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '3',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: KaizenColors.primaryDeep,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const Spacer(),
                Text(
                  'Active distillation',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: KaizenColors.inkSoft,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const _PaperFlightCard(
              tag: 'Core Foundations',
              title: 'Attention Is All You Need',
              authors: 'Vaswani et al. · 2017',
              stage: 'Section 3.2: Multi-Head Attention',
              progress: 0.72,
              left: '~12m left',
              saved: '4 intuitions saved',
            ),
            const SizedBox(height: 10),
            const _PaperFlightCard(
              tag: 'Kernel Speedup',
              tagTone: PillTone.secondary,
              title: 'FlashAttention-2: Faster Attention with Better Work Partitioning',
              authors: 'Dao · 2023',
              stage: 'Forward Pass Tiling',
              progress: 0.35,
              left: '~25m left',
              saved: '2 intuitions saved',
            ),
            const SizedBox(height: 10),
            const _PaperFlightCard(
              tag: 'Architecture',
              tagTone: PillTone.tertiary,
              title: 'DeepSeek-V3 Technical Report',
              authors: 'DeepSeek-AI · 2024',
              stage: 'DualPipe & FP8 Training',
              progress: 0.15,
              left: '~40m left',
              saved: '1 intuition saved',
            ),
          ],
        ),
      ),
    );
  }
}

class _PaperFlightCard extends StatelessWidget {
  const _PaperFlightCard({
    required this.tag,
    required this.title,
    required this.authors,
    required this.stage,
    required this.progress,
    required this.left,
    required this.saved,
    this.tagTone = PillTone.primary,
  });

  final String tag;
  final String title;
  final String authors;
  final String stage;
  final double progress;
  final String left;
  final String saved;
  final PillTone tagTone;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return KaizenCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              PillChip(label: tag, tone: tagTone),
              const Spacer(),
              Icon(Icons.schedule, size: 14, color: KaizenColors.inkSoft),
              const SizedBox(width: 4),
              Text(
                left,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: KaizenColors.inkSoft,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            title,
            style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 2),
          Text(
            authors,
            style: theme.textTheme.bodySmall?.copyWith(color: KaizenColors.inkMuted),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: KaizenColors.surfaceContainerLow.withValues(alpha: 0.7),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text.rich(
                        TextSpan(
                          style: theme.textTheme.labelSmall,
                          children: [
                            const TextSpan(text: 'Stage: '),
                            TextSpan(
                              text: stage,
                              style: const TextStyle(fontWeight: FontWeight.w700),
                            ),
                          ],
                        ),
                      ),
                    ),
                    Text(
                      '${(progress * 100).round()}%',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: KaizenColors.primaryDeep,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(999),
                  child: LinearProgressIndicator(
                    value: progress,
                    minHeight: 6,
                    backgroundColor: KaizenColors.surfaceContainer,
                    color: KaizenColors.primary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Icon(Icons.bookmark_outline, size: 16, color: KaizenColors.secondary),
              const SizedBox(width: 4),
              Text(
                saved,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: KaizenColors.secondary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              FilledButton.tonal(
                onPressed: () {},
                child: const Row(
                  children: [
                    Text('Resume'),
                    SizedBox(width: 4),
                    Icon(Icons.play_arrow, size: 16),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
