import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/ethereal_cadence.dart';
import '../widgets/kaizen_widgets.dart';

class MainShell extends StatelessWidget {
  const MainShell({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  static const _sideDestinations = [
    (0, Icons.home_outlined, Icons.home, 'Home'),
    (1, Icons.checklist_outlined, Icons.checklist, 'Atlas'),
    (3, Icons.record_voice_over_outlined, Icons.record_voice_over, 'Interview'),
    (4, Icons.menu_book_outlined, Icons.menu_book, 'Paper'),
  ];

  @override
  Widget build(BuildContext context) {
    final selected = navigationShell.currentIndex;
    final hideNav = selected == 2;
    return Scaffold(
      backgroundColor: KaizenColors.canvas,
      extendBody: !hideNav,
      body: navigationShell,
      bottomNavigationBar: hideNav
          ? null
          : SafeArea(
              minimum: const EdgeInsets.fromLTRB(4, 0, 4, 2),
              child: SizedBox(
                height: 58,
                child: Stack(
                  clipBehavior: Clip.none,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        for (final dest in _sideDestinations.take(2))
                          Expanded(
                            child: _NavItem(
                              label: dest.$4,
                              icon: dest.$2,
                              selectedIcon: dest.$3,
                              selected: selected == dest.$1,
                              onTap: () => navigationShell.goBranch(dest.$1),
                            ),
                          ),
                        const Expanded(child: SizedBox.shrink()),
                        for (final dest in _sideDestinations.skip(2))
                          Expanded(
                            child: _NavItem(
                              label: dest.$4,
                              icon: dest.$2,
                              selectedIcon: dest.$3,
                              selected: selected == dest.$1,
                              onTap: () => navigationShell.goBranch(dest.$1),
                            ),
                          ),
                      ],
                    ),
                    Positioned(
                      left: 0,
                      right: 0,
                      bottom: 2,
                      child: Center(
                        child: _RaeezNavItem(
                          selected: selected == 2,
                          onTap: () => navigationShell.goBranch(2),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.label,
    required this.icon,
    required this.selectedIcon,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final IconData selectedIcon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = selected ? KaizenColors.primaryDeep : KaizenColors.inkSoft;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Icon(selected ? selectedIcon : icon, size: 22, color: color),
          const SizedBox(height: 2),
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 2),
        ],
      ),
    );
  }
}

class _RaeezNavItem extends StatelessWidget {
  const _RaeezNavItem({required this.selected, required this.onTap});

  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Transform.translate(
            offset: const Offset(0, -10),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              padding: const EdgeInsets.all(3),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: selected
                    ? KaizenColors.primary.withValues(alpha: 0.14)
                    : KaizenColors.surface,
                border: Border.all(
                  color: selected
                      ? KaizenColors.primary.withValues(alpha: 0.55)
                      : KaizenColors.outlineVariant.withValues(alpha: 0.4),
                  width: selected ? 2.5 : 1.5,
                ),
                boxShadow: [
                  BoxShadow(
                    color: KaizenColors.primary.withValues(
                      alpha: selected ? 0.28 : 0.12,
                    ),
                    blurRadius: selected ? 14 : 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const RaeezAvatar(size: 48),
            ),
          ),
          Transform.translate(
            offset: const Offset(0, -6),
            child: Text(
              'Raeez',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color:
                    selected ? KaizenColors.primaryDeep : KaizenColors.inkSoft,
                fontWeight: selected ? FontWeight.w800 : FontWeight.w600,
                fontSize: 11,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
