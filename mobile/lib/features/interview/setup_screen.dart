import 'package:flutter/material.dart';

import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class InterviewSetupScreen extends StatefulWidget {
  const InterviewSetupScreen({
    super.key,
    this.preset,
    this.roundId,
    this.roundTitle,
  });

  final String? preset;
  final String? roundId;
  final String? roundTitle;

  @override
  State<InterviewSetupScreen> createState() => _InterviewSetupScreenState();
}

class _InterviewSetupScreenState extends State<InterviewSetupScreen> {
  String _seniority = 'sde_2';
  String _mode = 'medium';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final title = widget.roundTitle ?? 'Session setup';

    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: SoftPagePadding(
        child: ListView(
          children: [
            if (widget.preset != null) ...[
              PillChip(label: widget.preset!, tone: PillTone.secondary),
              const SizedBox(height: 12),
            ],
            if (widget.roundId != null) ...[
              Text(
                widget.roundId!,
                style: theme.textTheme.labelMedium?.copyWith(
                  color: KaizenColors.inkSoft,
                ),
              ),
              const SizedBox(height: 16),
            ],
            KaizenCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SectionHeader(title: 'Seniority'),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    children: [
                      for (final level in const [
                        'intern_fresher',
                        'sde_1',
                        'sde_2',
                        'sde_3_staff',
                      ])
                        ChoiceChip(
                          label: Text(level),
                          selected: _seniority == level,
                          onSelected: (_) => setState(() => _seniority = level),
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
                  const SectionHeader(title: 'Interviewer mode'),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    children: [
                      for (final mode in const [
                        'soft',
                        'medium',
                        'strict',
                        'hardcore',
                      ])
                        ChoiceChip(
                          label: Text(mode),
                          selected: _mode == mode,
                          onSelected: (_) => setState(() => _mode = mode),
                        ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Session stub · $_seniority · $_mode'
                      '${widget.roundId != null ? ' · ${widget.roundId}' : ''}',
                    ),
                  ),
                );
              },
              child: const Text('Start with Raeez'),
            ),
          ],
        ),
      ),
    );
  }
}
