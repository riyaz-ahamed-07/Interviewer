class ForgeLevel {
  const ForgeLevel({
    required this.level,
    required this.xp,
    required this.title,
  });

  final int level;
  final int xp;
  final String title;
}

const kForgeLevels = <ForgeLevel>[
  ForgeLevel(level: 1, xp: 0, title: 'Spark'),
  ForgeLevel(level: 2, xp: 120, title: 'Builder'),
  ForgeLevel(level: 3, xp: 350, title: 'Engineer'),
  ForgeLevel(level: 4, xp: 700, title: 'Systems mind'),
  ForgeLevel(level: 5, xp: 1200, title: 'Inference craft'),
  ForgeLevel(level: 6, xp: 1900, title: 'Paper blooded'),
  ForgeLevel(level: 7, xp: 2800, title: 'Off-campus weapon'),
  ForgeLevel(level: 8, xp: 4000, title: 'NVIDIA-ready'),
  ForgeLevel(level: 9, xp: 5500, title: 'Invincible'),
];

class LevelProgress {
  const LevelProgress({
    required this.level,
    required this.title,
    required this.xp,
    required this.floorXp,
    required this.nextXp,
    required this.progress,
  });

  final int level;
  final String title;
  final int xp;
  final int floorXp;
  final int nextXp;
  final double progress;
}

LevelProgress levelForXp(int xp) {
  var cur = kForgeLevels.first;
  for (final level in kForgeLevels) {
    if (xp >= level.xp) cur = level;
  }
  ForgeLevel? next;
  for (final level in kForgeLevels) {
    if (level.level == cur.level + 1) {
      next = level;
      break;
    }
  }
  final nextXp = next?.xp ?? cur.xp;
  final progress = next != null && next.xp > cur.xp
      ? (xp - cur.xp) / (next.xp - cur.xp)
      : 1.0;
  return LevelProgress(
    level: cur.level,
    title: cur.title,
    xp: xp,
    floorXp: cur.xp,
    nextXp: nextXp,
    progress: progress.clamp(0.0, 1.0),
  );
}
