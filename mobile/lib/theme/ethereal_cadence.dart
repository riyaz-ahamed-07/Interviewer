import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

abstract final class KaizenColors {
  static const primary = Color(0xFF7C5CFC);
  static const primaryDeep = Color(0xFF5F3ADD);
  static const primaryContainer = Color(0xFF7857F8);
  static const secondary = Color(0xFF006B5F);
  static const tertiary = Color(0xFF825100);
  static const canvas = Color(0xFFFAF8FF);
  static const surface = Color(0xFFFFFFFF);
  static const surfaceContainer = Color(0xFFEAEDFF);
  static const surfaceContainerLow = Color(0xFFF2F3FF);
  static const ink = Color(0xFF131B2E);
  static const inkMuted = Color(0xFF484555);
  static const inkSoft = Color(0xFF797587);
  static const outlineVariant = Color(0xFFC9C4D8);
  static const primaryWash = Color(0xFFF3F0FF);
  static const secondaryWash = Color(0xFFF0FDFA);
  static const tertiaryWash = Color(0xFFFEF3C7);
  static const border = Color(0x147C5CFC);
}

ThemeData buildKaizenTheme() {
  final base = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: KaizenColors.primary,
      primary: KaizenColors.primaryDeep,
      secondary: KaizenColors.secondary,
      tertiary: KaizenColors.tertiary,
      surface: KaizenColors.canvas,
      brightness: Brightness.light,
    ),
    scaffoldBackgroundColor: KaizenColors.canvas,
  );

  final fontFamily = GoogleFonts.plusJakartaSans().fontFamily;
  final textTheme = base.textTheme.apply(
    fontFamily: fontFamily,
    bodyColor: KaizenColors.ink,
    displayColor: KaizenColors.ink,
  );

  return base.copyWith(
    textTheme: textTheme,
    primaryTextTheme: textTheme,
    appBarTheme: AppBarTheme(
      backgroundColor: KaizenColors.canvas,
      foregroundColor: KaizenColors.ink,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      systemOverlayStyle: const SystemUiOverlayStyle(
        statusBarColor: KaizenColors.canvas,
        statusBarIconBrightness: Brightness.dark,
        statusBarBrightness: Brightness.light,
        systemNavigationBarColor: KaizenColors.canvas,
        systemNavigationBarIconBrightness: Brightness.dark,
      ),
      titleTextStyle: textTheme.titleLarge?.copyWith(
        fontWeight: FontWeight.w600,
        letterSpacing: -0.3,
      ),
    ),
    cardTheme: CardThemeData(
      color: KaizenColors.surface,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: KaizenColors.border),
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: KaizenColors.primaryWash,
      selectedColor: KaizenColors.primary,
      labelStyle: textTheme.labelMedium?.copyWith(
        color: KaizenColors.primaryDeep,
        fontWeight: FontWeight.w600,
      ),
      side: BorderSide.none,
      shape: const StadiumBorder(),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: KaizenColors.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: const StadiumBorder(),
        textStyle: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: KaizenColors.inkMuted,
        side: BorderSide(color: KaizenColors.inkSoft.withValues(alpha: 0.35)),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        shape: const StadiumBorder(),
      ),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: KaizenColors.surface.withValues(alpha: 0.92),
      elevation: 0,
      height: 72,
      indicatorColor: KaizenColors.primaryWash,
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        final selected = states.contains(WidgetState.selected);
        return textTheme.labelSmall?.copyWith(
          fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
          color: selected ? KaizenColors.primaryDeep : KaizenColors.inkSoft,
        );
      }),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        final selected = states.contains(WidgetState.selected);
        return IconThemeData(
          color: selected ? KaizenColors.primaryDeep : KaizenColors.inkSoft,
          size: 22,
        );
      }),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: KaizenColors.surface.withValues(alpha: 0.9),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: KaizenColors.inkSoft.withValues(alpha: 0.2)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: KaizenColors.inkSoft.withValues(alpha: 0.2)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: KaizenColors.primary, width: 1.5),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
    ),
  );
}
