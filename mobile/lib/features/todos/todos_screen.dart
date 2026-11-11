import 'package:flutter/material.dart';

import '../../forge/forge_scope.dart';
import '../../forge/todo_store.dart';
import '../../theme/ethereal_cadence.dart';
import '../../widgets/kaizen_widgets.dart';

class TodosScreen extends StatelessWidget {
  const TodosScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final todos = ForgeScope.todosOf(context);
    return AnimatedBuilder(
      animation: todos,
      builder: (context, _) {
        final theme = Theme.of(context);
        final items = todos.items;
        return Scaffold(
          appBar: AppBar(
            title: const Text('Weekly To-Do'),
            actions: [
              IconButton(
                onPressed: () => _showEditor(context, todos),
                icon: const Icon(Icons.add_rounded),
              ),
            ],
          ),
          body: SoftPagePadding(
            child: items.isEmpty
                ? Center(
                    child: Text(
                      'No personal to-dos yet.\nThese stay off the career track.',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: KaizenColors.inkSoft,
                      ),
                    ),
                  )
                : ReorderableListView.builder(
                    physics: const ClampingScrollPhysics(),
                    itemCount: items.length,
                    onReorderItem: todos.reorder,
                    itemBuilder: (context, index) {
                      final todo = items[index];
                      return Padding(
                        key: ValueKey(todo.id),
                        padding: const EdgeInsets.only(bottom: 10),
                        child: KaizenCard(
                          padding: const EdgeInsets.fromLTRB(10, 10, 6, 10),
                          child: Row(
                            children: [
                              HabitCheckbox(
                                done: todo.done,
                                onChanged: (_) => todos.toggle(todo.id),
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: InkWell(
                                  onTap: () =>
                                      _showEditor(context, todos, existing: todo),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        todo.title,
                                        style: theme.textTheme.bodyMedium
                                            ?.copyWith(
                                          fontWeight: FontWeight.w700,
                                          decoration: todo.done
                                              ? TextDecoration.lineThrough
                                              : null,
                                          color: todo.done
                                              ? KaizenColors.inkSoft
                                              : KaizenColors.ink,
                                        ),
                                      ),
                                      if (todo.notes.isNotEmpty) ...[
                                        const SizedBox(height: 2),
                                        Text(
                                          todo.notes,
                                          maxLines: 2,
                                          overflow: TextOverflow.ellipsis,
                                          style: theme.textTheme.bodySmall
                                              ?.copyWith(
                                            color: KaizenColors.inkMuted,
                                          ),
                                        ),
                                      ],
                                      if (todo.deadline != null) ...[
                                        const SizedBox(height: 6),
                                        PillChip(
                                          label:
                                              'Due ${todo.deadline!.day}/${todo.deadline!.month}/${todo.deadline!.year}',
                                          tone: PillTone.neutral,
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                              ),
                              ReorderableDragStartListener(
                                index: index,
                                child: const Padding(
                                  padding: EdgeInsets.all(8),
                                  child: Icon(
                                    Icons.drag_handle_rounded,
                                    color: KaizenColors.inkSoft,
                                  ),
                                ),
                              ),
                              IconButton(
                                onPressed: () => todos.remove(todo.id),
                                icon: const Icon(Icons.delete_outline_rounded),
                                color: KaizenColors.inkSoft,
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
          floatingActionButton: FloatingActionButton.extended(
            onPressed: () => _showEditor(context, todos),
            icon: const Icon(Icons.add),
            label: const Text('Add to-do'),
          ),
        );
      },
    );
  }

  Future<void> _showEditor(
    BuildContext context,
    CustomTodoStore todos, {
    CustomTodo? existing,
  }) async {
    final titleCtrl = TextEditingController(text: existing?.title ?? '');
    final notesCtrl = TextEditingController(text: existing?.notes ?? '');
    DateTime? deadline = existing?.deadline;

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModal) {
            return Padding(
              padding: EdgeInsets.fromLTRB(
                16,
                8,
                16,
                MediaQuery.of(context).viewInsets.bottom + 20,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    existing == null ? 'New to-do' : 'Edit to-do',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: titleCtrl,
                    decoration: const InputDecoration(labelText: 'Title'),
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: notesCtrl,
                    decoration: const InputDecoration(labelText: 'Notes'),
                    minLines: 2,
                    maxLines: 4,
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          deadline == null
                              ? 'No deadline'
                              : 'Due ${deadline!.day}/${deadline!.month}/${deadline!.year}',
                        ),
                      ),
                      TextButton(
                        onPressed: () async {
                          final picked = await showDatePicker(
                            context: context,
                            initialDate: deadline ?? DateTime.now(),
                            firstDate: DateTime.now()
                                .subtract(const Duration(days: 1)),
                            lastDate: DateTime.now()
                                .add(const Duration(days: 365)),
                          );
                          if (picked != null) {
                            setModal(() => deadline = picked);
                          }
                        },
                        child: const Text('Set deadline'),
                      ),
                      if (deadline != null)
                        TextButton(
                          onPressed: () => setModal(() => deadline = null),
                          child: const Text('Clear'),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () async {
                      final title = titleCtrl.text.trim();
                      if (title.isEmpty) return;
                      if (existing == null) {
                        await todos.add(
                          title: title,
                          notes: notesCtrl.text,
                          deadline: deadline,
                        );
                      } else {
                        await todos.update(
                          existing.id,
                          title: title,
                          notes: notesCtrl.text,
                          deadline: deadline,
                          clearDeadline: deadline == null,
                        );
                      }
                      if (context.mounted) Navigator.pop(context);
                    },
                    child: Text(existing == null ? 'Add' : 'Save'),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
