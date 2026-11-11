import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/ethereal_cadence.dart';
import 'kaizen_logo.dart';

class KaizenTopBar extends StatelessWidget implements PreferredSizeWidget {
  const KaizenTopBar({
    super.key,
    this.showStats = true,
    this.subtitle,
    this.trailing,
  });

  final bool showStats;
  final String? subtitle;
  final Widget? trailing;

  @override
  Size get preferredSize => Size.fromHeight(subtitle == null ? 56 : 64);

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: KaizenColors.canvas,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 8, 8),
          child: Row(
            children: [
              const KaizenLogo(markSize: 26, compact: true),
              if (subtitle != null) ...[
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    subtitle!,
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: KaizenColors.inkSoft,
                    ),
                  ),
                ),
              ] else
                const Spacer(),
              if (showStats) ...[
                TextButton(
                  onPressed: () => context.push('/stats'),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: Text(
                    'Stats',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: KaizenColors.primaryDeep,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => context.push('/todos'),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: Text(
                    'Todo',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: KaizenColors.primaryDeep,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => context.push('/you'),
                  tooltip: 'You',
                  visualDensity: VisualDensity.compact,
                  padding: const EdgeInsets.symmetric(horizontal: 6),
                  constraints: const BoxConstraints(minWidth: 36, minHeight: 36),
                  icon: const Icon(
                    Icons.person_outline_rounded,
                    color: KaizenColors.primaryDeep,
                    size: 22,
                  ),
                ),
              ],
              ?trailing,
            ],
          ),
        ),
      ),
    );
  }
}

class KaizenCard extends StatelessWidget {
  const KaizenCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.onTap,
    this.borderColor,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    final card = Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: KaizenColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor ?? KaizenColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D7C5CFC),
            blurRadius: 20,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: child,
    );

    if (onTap == null) return card;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: card,
      ),
    );
  }
}

class PillChip extends StatelessWidget {
  const PillChip({
    super.key,
    required this.label,
    this.tone = PillTone.primary,
  });

  final String label;
  final PillTone tone;

  @override
  Widget build(BuildContext context) {
    final (bg, fg, border) = switch (tone) {
      PillTone.primary => (
        const Color(0xFFE6DEFF),
        KaizenColors.primaryDeep,
        KaizenColors.primary.withValues(alpha: 0.2),
      ),
      PillTone.secondary => (
        KaizenColors.secondaryWash,
        const Color(0xFF0D9488),
        KaizenColors.secondary.withValues(alpha: 0.2),
      ),
      PillTone.tertiary => (
        KaizenColors.tertiaryWash,
        const Color(0xFFB45309),
        const Color(0x40F59E0B),
      ),
      PillTone.neutral => (
        KaizenColors.surfaceContainer,
        KaizenColors.inkMuted,
        KaizenColors.outlineVariant.withValues(alpha: 0.4),
      ),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: border),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelMedium?.copyWith(
          color: fg,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

enum PillTone { primary, secondary, tertiary, neutral }

class HabitCheckbox extends StatelessWidget {
  const HabitCheckbox({
    super.key,
    required this.done,
    required this.onChanged,
    this.color = KaizenColors.primary,
  });

  final bool done;
  final ValueChanged<bool> onChanged;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onChanged(!done),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        width: 24,
        height: 24,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: done ? color : Colors.white,
          border: Border.all(
            color: done ? color : KaizenColors.outlineVariant,
            width: 1.5,
          ),
          boxShadow: done
              ? [BoxShadow(color: color.withValues(alpha: 0.25), blurRadius: 8)]
              : null,
        ),
        child: done
            ? const Icon(Icons.check, size: 14, color: Colors.white)
            : null,
      ),
    );
  }
}

class SectionHeader extends StatelessWidget {
  const SectionHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.trailing,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              if (subtitle != null) ...[
                const SizedBox(height: 4),
                Text(
                  subtitle!,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: KaizenColors.inkSoft,
                  ),
                ),
              ],
            ],
          ),
        ),
        ?trailing,
      ],
    );
  }
}

class SoftPagePadding extends StatelessWidget {
  const SoftPagePadding({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 72),
      child: child,
    );
  }
}

class RaeezAvatar extends StatelessWidget {
  const RaeezAvatar({
    super.key,
    this.size = 56,
    this.asset = 'assets/images/raeez-face.png',
    this.fit = BoxFit.cover,
  });

  final double size;
  final String asset;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: KaizenColors.primary.withValues(alpha: 0.22),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.asset(
        asset,
        fit: fit,
      ),
    );
  }
}
