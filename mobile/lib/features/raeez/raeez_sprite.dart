import 'dart:async';
import 'dart:math';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class RaeezSheetMeta {
  const RaeezSheetMeta({
    required this.key,
    required this.asset,
    required this.cols,
    required this.rows,
    required this.frames,
    required this.fps,
    this.loop = false,
    this.holdFrame,
    this.holdMs = 0,
  });

  final String key;
  final String asset;
  final int cols;
  final int rows;
  final int frames;
  final int fps;
  final bool loop;
  final int? holdFrame;
  final int holdMs;
}

const kRaeezSheets = <RaeezSheetMeta>[
  RaeezSheetMeta(
    key: 'idle',
    asset: 'assets/raeez/idle-breathing-sheet-alpha.png',
    cols: 6,
    rows: 2,
    frames: 12,
    fps: 10,
    loop: true,
  ),
  RaeezSheetMeta(
    key: 'phone',
    asset: 'assets/raeez/fidget-phone-check-sheet-alpha.png',
    cols: 8,
    rows: 2,
    frames: 16,
    fps: 12,
    holdFrame: 7,
    holdMs: 1500,
  ),
  RaeezSheetMeta(
    key: 'look',
    asset: 'assets/raeez/fidget-looking-around-sheet-alpha.png',
    cols: 8,
    rows: 2,
    frames: 16,
    fps: 12,
    holdFrame: 7,
    holdMs: 1500,
  ),
  RaeezSheetMeta(
    key: 'glasses',
    asset: 'assets/raeez/fidget-adjust-glasses-sheet-alpha.png',
    cols: 8,
    rows: 2,
    frames: 16,
    fps: 12,
    holdFrame: 7,
    holdMs: 1500,
  ),
  RaeezSheetMeta(
    key: 'stretch',
    asset: 'assets/raeez/fidget-stretch-sheet-alpha.png',
    cols: 8,
    rows: 2,
    frames: 16,
    fps: 12,
    holdFrame: 7,
    holdMs: 1500,
  ),
  RaeezSheetMeta(
    key: 'yawn',
    asset: 'assets/raeez/fidget-yawn-sheet-alpha.png',
    cols: 8,
    rows: 2,
    frames: 16,
    fps: 12,
    holdFrame: 7,
    holdMs: 1500,
  ),
];

class RaeezSpriteAnimator extends StatefulWidget {
  const RaeezSpriteAnimator({
    super.key,
    this.height = 220,
    this.onSheetChanged,
  });

  final double height;
  final ValueChanged<String>? onSheetChanged;

  @override
  State<RaeezSpriteAnimator> createState() => _RaeezSpriteAnimatorState();
}

class _RaeezSpriteAnimatorState extends State<RaeezSpriteAnimator> {
  static const _fidgetKeys = ['phone', 'look', 'glasses', 'stretch', 'yawn'];
  final _rng = Random();
  final _images = <String, ui.Image>{};

  String _sheetKey = 'idle';
  int _frame = 0;
  String _lastFidget = '';
  bool _holding = false;
  bool _ready = false;
  Timer? _tick;
  Timer? _fidgetTimer;
  Timer? _holdTimer;

  RaeezSheetMeta get _meta =>
      kRaeezSheets.firstWhere((s) => s.key == _sheetKey);

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _tick?.cancel();
    _fidgetTimer?.cancel();
    _holdTimer?.cancel();
    for (final img in _images.values) {
      img.dispose();
    }
    super.dispose();
  }

  Future<void> _load() async {
    for (final sheet in kRaeezSheets) {
      final data = await rootBundle.load(sheet.asset);
      final codec = await ui.instantiateImageCodec(data.buffer.asUint8List());
      final frame = await codec.getNextFrame();
      _images[sheet.key] = frame.image;
    }
    if (!mounted) return;
    setState(() => _ready = true);
    _startClock();
    _scheduleFidget();
  }

  void _startClock() {
    _tick?.cancel();
    final fps = _meta.fps;
    _tick = Timer.periodic(
      Duration(milliseconds: (1000 / fps).round()),
      (_) => _advance(),
    );
  }

  void _setSheet(String key, {int frame = 0}) {
    if (_sheetKey == key && _frame == frame) return;
    _holdTimer?.cancel();
    _holding = false;
    setState(() {
      _sheetKey = key;
      _frame = frame;
    });
    widget.onSheetChanged?.call(key);
    _startClock();
  }

  void _advance() {
    if (!_ready || _holding) return;
    final meta = _meta;
    if (meta.loop) {
      setState(() => _frame = (_frame + 1) % meta.frames);
      return;
    }
    if (meta.holdFrame != null &&
        _frame == meta.holdFrame &&
        meta.holdMs > 0 &&
        !_holding) {
      _holding = true;
      _holdTimer = Timer(Duration(milliseconds: meta.holdMs), () {
        _holding = false;
        if (!mounted) return;
        if (_frame < meta.frames - 1) {
          setState(() => _frame += 1);
        } else {
          _setSheet('idle');
          _scheduleFidget();
        }
      });
      return;
    }
    if (_frame < meta.frames - 1) {
      setState(() => _frame += 1);
      return;
    }
    _setSheet('idle');
    _scheduleFidget();
  }

  void _scheduleFidget() {
    _fidgetTimer?.cancel();
    final wait = 4000 + _rng.nextInt(5000);
    _fidgetTimer = Timer(Duration(milliseconds: wait), () {
      if (!mounted || _sheetKey != 'idle') {
        _scheduleFidget();
        return;
      }
      final pool = _fidgetKeys.where((k) => k != _lastFidget).toList();
      if (pool.isEmpty) {
        _scheduleFidget();
        return;
      }
      final next = pool[_rng.nextInt(pool.length)];
      _lastFidget = next;
      _setSheet(next);
    });
  }

  @override
  Widget build(BuildContext context) {
    final image = _images[_sheetKey];
    if (!_ready || image == null) {
      return SizedBox(
        height: widget.height,
        child: const Center(child: CircularProgressIndicator(strokeWidth: 2)),
      );
    }
    final meta = _meta;
    return SizedBox(
      height: widget.height,
      width: double.infinity,
      child: CustomPaint(
        painter: _SpritePainter(
          image: image,
          cols: meta.cols,
          rows: meta.rows,
          frame: _frame,
        ),
      ),
    );
  }
}

class _SpritePainter extends CustomPainter {
  _SpritePainter({
    required this.image,
    required this.cols,
    required this.rows,
    required this.frame,
  });

  final ui.Image image;
  final int cols;
  final int rows;
  final int frame;

  @override
  void paint(Canvas canvas, Size size) {
    final cellW = image.width ~/ cols;
    final cellH = image.height ~/ rows;
    final col = frame % cols;
    final row = frame ~/ cols;
    final src = Rect.fromLTWH(
      (col * cellW).toDouble(),
      (row * cellH).toDouble(),
      cellW.toDouble(),
      cellH.toDouble(),
    );
    final scale = size.height / cellH;
    final drawW = cellW * scale;
    final drawH = size.height;
    final dx = ((size.width - drawW) / 2).roundToDouble();
    final dst = Rect.fromLTWH(dx, 0, drawW.roundToDouble(), drawH.roundToDouble());
    final paint = Paint()
      ..isAntiAlias = false
      ..filterQuality = FilterQuality.none;
    canvas.drawImageRect(image, src, dst, paint);
  }

  @override
  bool shouldRepaint(covariant _SpritePainter oldDelegate) {
    return oldDelegate.image != image ||
        oldDelegate.frame != frame ||
        oldDelegate.cols != cols ||
        oldDelegate.rows != rows;
  }
}
