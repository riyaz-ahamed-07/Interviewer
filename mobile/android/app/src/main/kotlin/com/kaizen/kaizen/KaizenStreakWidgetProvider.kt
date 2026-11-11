package com.kaizen.kaizen

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.widget.RemoteViews

class KaizenStreakWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        val prefs = context.getSharedPreferences(
            "FlutterSharedPreferences",
            Context.MODE_PRIVATE,
        )
        appWidgetIds.forEach { widgetId ->
            val views = RemoteViews(context.packageName, R.layout.kaizen_streak_widget).apply {
                setTextViewText(
                    R.id.widget_headline,
                    prefs.getString("flutter.headline", "Start today") ?: "Start today",
                )
                setTextViewText(
                    R.id.widget_next,
                    prefs.getString("flutter.next_task", "Open Atlas") ?: "Open Atlas",
                )
                val level = prefs.getLong("flutter.level", 1L).toInt()
                val streak = prefs.getLong("flutter.streak", 0L).toInt()
                val open = prefs.getLong("flutter.open_todos", 0L).toInt()
                setTextViewText(
                    R.id.widget_meta,
                    "Lvl $level · ${streak}d · $open open",
                )
            }
            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }
}
