import 'package:flutter/material.dart';

import 'curriculum.dart';
import 'progress.dart';
import 'todo_store.dart';

class ForgeScope extends InheritedNotifier<ForgeProgressStore> {
  const ForgeScope({
    super.key,
    required ForgeProgressStore store,
    required this.curriculum,
    required this.todos,
    required super.child,
  }) : super(notifier: store);

  final ForgeCurriculum curriculum;
  final CustomTodoStore todos;

  static ForgeScope of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<ForgeScope>();
    assert(scope != null, 'ForgeScope not found');
    return scope!;
  }

  static ForgeProgressStore storeOf(BuildContext context) => of(context).notifier!;

  static ForgeCurriculum curriculumOf(BuildContext context) =>
      of(context).curriculum;

  static CustomTodoStore todosOf(BuildContext context) => of(context).todos;
}
