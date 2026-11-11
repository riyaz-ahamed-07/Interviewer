import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../forge/profile.dart';
import '../../services/live_voice_controller.dart';
import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class RaeezScreen extends StatefulWidget {
  const RaeezScreen({super.key});

  @override
  State<RaeezScreen> createState() => _RaeezScreenState();
}

class _RaeezScreenState extends State<RaeezScreen> {
  final _input = TextEditingController();
  final _live = LiveVoiceController();
  bool _actionsOpen = false;

  static const _actions = [
    (Icons.record_voice_over_rounded, 'Soft mock', '/interview'),
    (Icons.psychology_rounded, 'Concept drill', '/list'),
    (Icons.menu_book_rounded, 'Paper buddy', '/paper'),
    (Icons.task_alt_rounded, 'Plan check', '/home'),
  ];

  @override
  void initState() {
    super.initState();
    _live.addListener(_onLive);
  }

  void _onLive() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _live.removeListener(_onLive);
    _live.dispose();
    _input.dispose();
    super.dispose();
  }

  bool get _listening =>
      _live.status == LiveVoiceStatus.listening ||
      _live.status == LiveVoiceStatus.speaking ||
      _live.status == LiveVoiceStatus.connecting ||
      _live.status == LiveVoiceStatus.live;

  Future<void> _toggleListen() async {
    setState(() => _actionsOpen = false);
    if (_listening) {
      await _live.disconnect();
      return;
    }
    if (_live.status == LiveVoiceStatus.paused) {
      await _live.resume();
      return;
    }
    await _live.connect();
  }

  void _send() {
    final text = _input.text.trim();
    if (text.isEmpty) return;
    _input.clear();
    if (_live.sessionId == null) {
      _live.connect().then((_) => _live.sendChat(text));
    } else {
      _live.sendChat(text);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final name = KaizenProfile.current.displayName;
    final history = _live.turns.reversed.take(8).toList();

    return Scaffold(
      backgroundColor: KaizenColors.canvas,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(8, 4, 8, 0),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => context.go('/home'),
                    icon: const Icon(Icons.home_rounded),
                    color: KaizenColors.inkMuted,
                  ),
                  Expanded(
                    child: Text(
                      'Raeez',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.4,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => context.push('/settings'),
                    icon: const Icon(Icons.settings_outlined),
                    color: KaizenColors.inkMuted,
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                physics: const ClampingScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(20, 4, 20, 12),
                children: [
                  const Center(
                    child: RaeezAvatar(size: 168),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    'Hello $name',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: KaizenColors.primaryDeep,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'How can I assist you today?',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: KaizenColors.inkMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (_live.status == LiveVoiceStatus.error &&
                      _live.error != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      _live.error!,
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: const Color(0xFFB45309),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                  if (_live.userPartial.isNotEmpty ||
                      _live.assistantPartial.isNotEmpty) ...[
                    const SizedBox(height: 14),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: KaizenColors.surface,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: KaizenColors.border),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (_live.userPartial.isNotEmpty)
                            Text(
                              'You · ${_live.userPartial}',
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          if (_live.assistantPartial.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Text(
                              'Raeez · ${_live.assistantPartial}',
                              style: theme.textTheme.bodyMedium?.copyWith(
                                color: KaizenColors.primaryDeep,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 18),
                  Text(
                    history.isEmpty ? 'History' : 'Live turns',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 10),
                  if (history.isEmpty)
                    KaizenCard(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 14,
                      ),
                      child: Text(
                        'Tap the mic to start a live Study Friend session with transcription.',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: KaizenColors.inkMuted,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    )
                  else
                    for (final item in history) ...[
                      KaizenCard(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 14,
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.role == 'user' ? 'You' : 'Raeez',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: KaizenColors.primaryDeep,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              item.text,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 8),
                    ],
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Column(
                children: [
                  if (_actionsOpen) ...[
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Container(
                        width: 220,
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        decoration: BoxDecoration(
                          color: KaizenColors.surface,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: KaizenColors.border),
                          boxShadow: const [
                            BoxShadow(
                              color: Color(0x147C5CFC),
                              blurRadius: 16,
                              offset: Offset(0, 6),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            for (final action in _actions)
                              ListTile(
                                dense: true,
                                leading: Icon(
                                  action.$1,
                                  color: KaizenColors.primaryDeep,
                                ),
                                title: Text(
                                  action.$2,
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                onTap: () {
                                  setState(() => _actionsOpen = false);
                                  context.go(action.$3);
                                },
                              ),
                          ],
                        ),
                      ),
                    ),
                  ],
                  Row(
                    children: [
                      Material(
                        color: KaizenColors.surface,
                        shape: const CircleBorder(),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: () =>
                              setState(() => _actionsOpen = !_actionsOpen),
                          child: SizedBox(
                            width: 44,
                            height: 44,
                            child: Icon(
                              _actionsOpen
                                  ? Icons.close_rounded
                                  : Icons.menu_rounded,
                              color: KaizenColors.inkMuted,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: SizedBox(
                          height: 48,
                          child: TextField(
                            controller: _input,
                            onSubmitted: (_) => _send(),
                            style: theme.textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                            decoration: InputDecoration(
                              isDense: true,
                              filled: false,
                              border: InputBorder.none,
                              enabledBorder: InputBorder.none,
                              focusedBorder: InputBorder.none,
                              contentPadding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 14,
                              ),
                              hintText: 'Message Raeez…',
                              hintStyle: theme.textTheme.bodyMedium?.copyWith(
                                color: KaizenColors.inkSoft,
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Material(
                        color: KaizenColors.primaryDeep,
                        shape: const CircleBorder(),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: _send,
                          child: const SizedBox(
                            width: 44,
                            height: 44,
                            child: Icon(
                              Icons.send_rounded,
                              color: Colors.white,
                              size: 20,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Material(
                        color: _listening
                            ? const Color(0xFFEF4444)
                            : KaizenColors.primary,
                        shape: const CircleBorder(),
                        elevation: 2,
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: _toggleListen,
                          child: SizedBox(
                            width: 52,
                            height: 52,
                            child: Icon(
                              _listening
                                  ? Icons.stop_rounded
                                  : Icons.mic_rounded,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
