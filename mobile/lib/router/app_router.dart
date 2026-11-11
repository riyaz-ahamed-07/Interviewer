import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../features/curriculum/master_list_screen.dart';
import '../features/history/history_screen.dart';
import '../features/home/home_screen.dart';
import '../features/interview/company_presets_screen.dart';
import '../features/interview/hub_screen.dart';
import '../features/interview/setup_screen.dart';
import '../features/paper/paper_home_screen.dart';
import '../features/raeez/raeez_screen.dart';
import '../features/settings/settings_screen.dart';
import '../features/stats/stats_screen.dart';
import '../features/todos/todos_screen.dart';
import '../features/you/you_screen.dart';
import '../shell/main_shell.dart';

final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>();

GoRouter buildAppRouter() {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/home',
    routes: [
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return MainShell(navigationShell: navigationShell);
        },
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/home',
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/list',
                builder: (context, state) => const MasterListScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/raeez',
                builder: (context, state) => const RaeezScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/interview',
                builder: (context, state) => const InterviewHubScreen(),
                routes: [
                  GoRoute(
                    path: 'presets',
                    parentNavigatorKey: _rootNavigatorKey,
                    builder: (context, state) => const CompanyPresetsScreen(),
                  ),
                  GoRoute(
                    path: 'setup',
                    parentNavigatorKey: _rootNavigatorKey,
                    builder: (context, state) {
                      final extra = state.extra;
                      String? preset;
                      String? roundId;
                      String? roundTitle;
                      if (extra is Map) {
                        preset = extra['preset'] as String?;
                        roundId = extra['roundId'] as String?;
                        roundTitle = extra['title'] as String?;
                      }
                      return InterviewSetupScreen(
                        preset: preset,
                        roundId: roundId,
                        roundTitle: roundTitle,
                      );
                    },
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/paper',
                builder: (context, state) => const PaperHomeScreen(),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: '/settings',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/history',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const HistoryScreen(),
      ),
      GoRoute(
        path: '/stats',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const StatsScreen(),
      ),
      GoRoute(
        path: '/todos',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const TodosScreen(),
      ),
      GoRoute(
        path: '/you',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const YouScreen(),
      ),
    ],
  );
}
