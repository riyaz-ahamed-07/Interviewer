import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class CustomTodo {
  CustomTodo({
    required this.id,
    required this.title,
    required this.createdAt,
    this.notes = '',
    this.deadline,
    this.done = false,
    this.order = 0,
  });

  final String id;
  String title;
  String notes;
  DateTime? deadline;
  bool done;
  int order;
  final DateTime createdAt;

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'notes': notes,
        'deadline': deadline?.toIso8601String(),
        'done': done,
        'order': order,
        'createdAt': createdAt.toIso8601String(),
      };

  factory CustomTodo.fromJson(Map<String, dynamic> json) {
    return CustomTodo(
      id: json['id'] as String,
      title: json['title'] as String? ?? '',
      notes: json['notes'] as String? ?? '',
      deadline: json['deadline'] == null
          ? null
          : DateTime.tryParse(json['deadline'] as String),
      done: json['done'] as bool? ?? false,
      order: json['order'] as int? ?? 0,
      createdAt: DateTime.tryParse(json['createdAt'] as String? ?? '') ??
          DateTime.now(),
    );
  }
}

class CustomTodoStore extends ChangeNotifier {
  CustomTodoStore._(this._prefs);

  final SharedPreferences _prefs;
  final List<CustomTodo> _items = [];

  List<CustomTodo> get items {
    final copy = [..._items]..sort((a, b) => a.order.compareTo(b.order));
    return copy;
  }

  List<CustomTodo> get openItems =>
      items.where((t) => !t.done).toList(growable: false);

  static Future<CustomTodoStore> open() async {
    final prefs = await SharedPreferences.getInstance();
    final store = CustomTodoStore._(prefs);
    store._hydrate();
    return store;
  }

  void _hydrate() {
    final raw = _prefs.getString('kaizen.custom_todos.v1');
    if (raw == null || raw.isEmpty) return;
    try {
      final decoded = jsonDecode(raw);
      if (decoded is! List) return;
      _items
        ..clear()
        ..addAll(
          decoded
              .whereType<Map<String, dynamic>>()
              .map(CustomTodo.fromJson),
        );
    } catch (_) {}
  }

  Future<void> _persist() async {
    await _prefs.setString(
      'kaizen.custom_todos.v1',
      jsonEncode(_items.map((e) => e.toJson()).toList()),
    );
  }

  Future<void> add({
    required String title,
    String notes = '',
    DateTime? deadline,
  }) async {
    final todo = CustomTodo(
      id: 'todo-${DateTime.now().millisecondsSinceEpoch}',
      title: title.trim(),
      notes: notes.trim(),
      deadline: deadline,
      order: _items.length,
      createdAt: DateTime.now(),
    );
    _items.add(todo);
    await _persist();
    notifyListeners();
  }

  Future<void> toggle(String id) async {
    final hit = _items.where((t) => t.id == id).firstOrNull;
    if (hit == null) return;
    hit.done = !hit.done;
    await _persist();
    notifyListeners();
  }

  Future<void> remove(String id) async {
    _items.removeWhere((t) => t.id == id);
    for (var i = 0; i < _items.length; i++) {
      _items[i].order = i;
    }
    await _persist();
    notifyListeners();
  }

  Future<void> reorder(int oldIndex, int newIndex) async {
    final sorted = items;
    final item = sorted.removeAt(oldIndex);
    final insertAt = newIndex.clamp(0, sorted.length);
    sorted.insert(insertAt, item);
    for (var i = 0; i < sorted.length; i++) {
      sorted[i].order = i;
    }
    _items
      ..clear()
      ..addAll(sorted);
    await _persist();
    notifyListeners();
  }

  Future<void> update(
    String id, {
    String? title,
    String? notes,
    DateTime? deadline,
    bool clearDeadline = false,
  }) async {
    final hit = _items.where((t) => t.id == id).firstOrNull;
    if (hit == null) return;
    if (title != null) hit.title = title.trim();
    if (notes != null) hit.notes = notes.trim();
    if (clearDeadline) {
      hit.deadline = null;
    } else if (deadline != null) {
      hit.deadline = deadline;
    }
    await _persist();
    notifyListeners();
  }
}
