class KaizenProfile {
  const KaizenProfile({
    required this.displayName,
    required this.handle,
    required this.roleLabel,
  });

  final String displayName;
  final String handle;
  final String roleLabel;

  static const current = KaizenProfile(
    displayName: 'Riyaz',
    handle: '@riyaz',
    roleLabel: 'Systems Engineer',
  );
}

class FocusWindows {
  const FocusWindows({
    required this.practiceRanges,
    required this.protectedRange,
    required this.protectedLabel,
  });

  final String practiceRanges;
  final String protectedRange;
  final String protectedLabel;

  static const tonight = FocusWindows(
    practiceRanges: '7:00 – 8:00 PM  ·  10:00 PM – 12:00 AM',
    protectedRange: '8:00 – 10:00 PM',
    protectedLabel: 'Gatherly (Protected focus block)',
  );
}
