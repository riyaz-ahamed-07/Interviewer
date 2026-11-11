import 'package:flutter/material.dart';

import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: SoftPagePadding(
        child: ListView(
          children: [
            KaizenCard(
              child: SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Protect Gatherly hours'),
                subtitle: Text(
                  'Block interview drills 8–10pm',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: KaizenColors.inkSoft,
                  ),
                ),
                value: true,
                activeThumbColor: KaizenColors.primary,
                onChanged: (_) {},
              ),
            ),
            const SizedBox(height: 12),
            KaizenCard(
              child: SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Reduce motion'),
                subtitle: Text(
                  'Softer transitions for focus sessions',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: KaizenColors.inkSoft,
                  ),
                ),
                value: false,
                onChanged: (_) {},
              ),
            ),
            const SizedBox(height: 12),
            const KaizenCard(
              child: SectionHeader(
                title: 'Raeez voice',
                subtitle: 'Gemini Live primary · Edge-TTS fallback',
              ),
            ),
          ],
        ),
      ),
    );
  }
}
