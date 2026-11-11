import 'package:flutter/material.dart';

import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Interview History')),
      body: SoftPagePadding(
        child: ListView(
          children: [
            KaizenCard(
              child: SectionHeader(
                title: 'No sessions yet',
                subtitle: 'Finished mocks land here with scorecards.',
                trailing: Icon(
                  Icons.history,
                  color: KaizenColors.inkSoft.withValues(alpha: 0.7),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
