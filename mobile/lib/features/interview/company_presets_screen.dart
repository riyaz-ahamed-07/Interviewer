import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class CompanyPresetsScreen extends StatelessWidget {
  const CompanyPresetsScreen({super.key});

  static const _presets = [
    (
      'Indian IT Services',
      'TCS · Infosys · Wipro',
      ['OA & Aptitude', 'CS Fundamentals', 'Coding', 'Managerial'],
    ),
    (
      'Indian Product Unicorns',
      'Swiggy · Flipkart · Razorpay',
      ['Machine Coding', 'LLD', 'HLD', 'EM Values'],
    ),
    (
      'FAANG / Tier-1',
      'Google · Meta · Amazon',
      ['DSA', 'HLD', 'LLD', 'Behavioral'],
    ),
    (
      'High-Growth Startup',
      'YC · Series A–C',
      ['Pair', 'Take-home', 'Pragmatic Arch', 'Founder Fit'],
    ),
    (
      'AI-First Labs',
      'OpenAI · Anthropic · DeepMind',
      ['ML Maths', 'PyTorch Debug', 'LLM/RAG Arch', 'Paper Defense'],
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Company Presets')),
      body: SoftPagePadding(
        child: ListView(
          children: [
            Text(
              'Calibrate your loop',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Pick an archetype · Configure opens Setup with round chips.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: KaizenColors.inkSoft,
              ),
            ),
            const SizedBox(height: 20),
            for (final preset in _presets) ...[
              KaizenCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      preset.$1,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      preset.$2,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: KaizenColors.inkSoft,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        for (final chip in preset.$3)
                          PillChip(label: chip),
                      ],
                    ),
                    const SizedBox(height: 14),
                    FilledButton(
                      onPressed: () => context.push(
                        '/interview/setup',
                        extra: {'preset': preset.$1},
                      ),
                      child: const Text('Configure loop'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],
          ],
        ),
      ),
    );
  }
}
