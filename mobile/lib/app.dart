import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

import 'forge/curriculum.dart';
import 'forge/forge_scope.dart';
import 'forge/progress.dart';
import 'forge/todo_store.dart';
import 'router/app_router.dart';
import 'services/momentum_sync.dart';
import 'services/notification_service.dart';
import 'theme/ethereal_cadence.dart';

class KaizenApp extends StatefulWidget {
  const KaizenApp({super.key});

  @override
  State<KaizenApp> createState() => _KaizenAppState();
}

class _KaizenAppState extends State<KaizenApp> {
  late final GoRouter _router = buildAppRouter();
  ForgeCurriculum? _curriculum;
  ForgeProgressStore? _store;
  CustomTodoStore? _todos;
  Object? _error;

  @override
  void initState() {
    super.initState();
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: KaizenColors.canvas,
        statusBarIconBrightness: Brightness.dark,
        statusBarBrightness: Brightness.light,
        systemNavigationBarColor: KaizenColors.canvas,
        systemNavigationBarIconBrightness: Brightness.dark,
      ),
    );
    _boot();
  }

  Future<void> _boot() async {
    try {
      await NotificationService.instance.init();
      final curriculum = await ForgeCurriculum.load();
      final store = await ForgeProgressStore.open();
      final todos = await CustomTodoStore.open();
      await store.reconcileCarryForward(curriculum);
      await syncMomentum(store: store, todos: todos);
      if (!mounted) return;
      setState(() {
        _curriculum = curriculum;
        _store = store;
        _todos = todos;
        _error = null;
      });
      store.addListener(_onMomentumChanged);
      todos.addListener(_onMomentumChanged);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e);
    }
  }

  void _onMomentumChanged() {
    final store = _store;
    final todos = _todos;
    if (store == null || todos == null) return;
    syncMomentum(store: store, todos: todos);
  }

  @override
  void dispose() {
    _store?.removeListener(_onMomentumChanged);
    _todos?.removeListener(_onMomentumChanged);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final curriculum = _curriculum;
    final store = _store;
    final todos = _todos;

    if (_error != null) {
      return MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: buildKaizenTheme(),
        home: const Scaffold(
          body: Center(child: Text('Could not load Forge data')),
        ),
      );
    }

    if (curriculum == null || store == null || todos == null) {
      return MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: buildKaizenTheme(),
        home: const Scaffold(
          body: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    return ForgeScope(
      store: store,
      curriculum: curriculum,
      todos: todos,
      child: ListenableBuilder(
        listenable: Listenable.merge([store, todos]),
        builder: (context, _) {
          return AnnotatedRegion<SystemUiOverlayStyle>(
            value: const SystemUiOverlayStyle(
              statusBarColor: KaizenColors.canvas,
              statusBarIconBrightness: Brightness.dark,
              statusBarBrightness: Brightness.light,
              systemNavigationBarColor: KaizenColors.canvas,
              systemNavigationBarIconBrightness: Brightness.dark,
            ),
            child: MaterialApp.router(
              title: 'Kaizen',
              debugShowCheckedModeBanner: false,
              theme: buildKaizenTheme(),
              scrollBehavior: const _NoStretchScrollBehavior(),
              routerConfig: _router,
            ),
          );
        },
      ),
    );
  }
}

class _NoStretchScrollBehavior extends MaterialScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  Widget buildOverscrollIndicator(
    BuildContext context,
    Widget child,
    ScrollableDetails details,
  ) {
    return child;
  }

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics();
  }
}
