import 'package:flutter/material.dart';

class KaizenLogo extends StatelessWidget {
  const KaizenLogo({
    super.key,
    this.showWordmark = true,
    this.markSize = 28,
    this.compact = false,
  });

  final bool showWordmark;
  final double markSize;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final height = compact ? 28.0 : markSize.toDouble().clamp(28.0, 40.0);
    return Image.asset(
      'assets/images/kaizen-wordmark.png',
      height: height,
      fit: BoxFit.contain,
      filterQuality: FilterQuality.high,
      alignment: Alignment.centerLeft,
    );
  }
}
