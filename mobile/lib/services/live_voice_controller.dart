import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:web_socket_channel/web_socket_channel.dart';

import 'api_config.dart';
import 'kaizen_api.dart';

enum LiveVoiceStatus {
  idle,
  connecting,
  live,
  listening,
  speaking,
  paused,
  error,
}

class LiveTurn {
  LiveTurn({required this.role, required this.text, DateTime? at})
      : at = at ?? DateTime.now();

  final String role;
  final String text;
  final DateTime at;
}

class LiveVoiceController extends ChangeNotifier {
  LiveVoiceController();

  final stt.SpeechToText _speech = stt.SpeechToText();
  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();

  WebSocketChannel? _channel;
  StreamSubscription? _wsSub;
  Timer? _streamTimer;
  String? _sessionId;
  String? _recordPath;
  LiveVoiceStatus status = LiveVoiceStatus.idle;
  String? error;
  String userPartial = '';
  String assistantPartial = '';
  final List<LiveTurn> turns = [];
  bool _micOn = true;
  bool _speechReady = false;

  String? get sessionId => _sessionId;

  Future<void> connect({String mode = 'medium'}) async {
    if (status == LiveVoiceStatus.connecting ||
        status == LiveVoiceStatus.listening ||
        status == LiveVoiceStatus.live ||
        status == LiveVoiceStatus.speaking) {
      return;
    }
    status = LiveVoiceStatus.connecting;
    error = null;
    notifyListeners();

    try {
      final mic = await Permission.microphone.request();
      if (!mic.isGranted) {
        throw Exception('Microphone permission denied');
      }

      final payload = await KaizenApi.startFriendSession(mode: mode);
      final session = payload['session'] as Map<String, dynamic>?;
      final id = session?['id'] as String?;
      if (id == null || id.isEmpty) {
        throw Exception('No session id from backend');
      }
      _sessionId = id;

      final channel = WebSocketChannel.connect(Uri.parse(ApiConfig.liveWsUrl(id)));
      _channel = channel;
      await channel.ready;

      _wsSub = channel.stream.listen(
        _onWsMessage,
        onError: (Object e) {
          error = e.toString();
          status = LiveVoiceStatus.error;
          notifyListeners();
        },
        onDone: () {
          if (status != LiveVoiceStatus.idle &&
              status != LiveVoiceStatus.paused) {
            status = LiveVoiceStatus.idle;
            notifyListeners();
          }
        },
      );

      _speechReady = await _speech.initialize(
        onError: (e) {
          error = e.errorMsg;
          notifyListeners();
        },
      );

      status = LiveVoiceStatus.listening;
      notifyListeners();
      await _startMicUplink();
      await _startLocalTranscript();
    } catch (e) {
      error = e.toString();
      status = LiveVoiceStatus.error;
      notifyListeners();
      await disconnect();
    }
  }

  Future<void> _startMicUplink() async {
    if (!await _recorder.hasPermission()) return;
    final dir = await getTemporaryDirectory();
    _recordPath = '${dir.path}/kaizen_live_${DateTime.now().millisecondsSinceEpoch}.wav';
    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: 16000,
        numChannels: 1,
      ),
      path: _recordPath!,
    );

    _streamTimer?.cancel();
    _streamTimer = Timer.periodic(const Duration(milliseconds: 800), (_) async {
      if (!_micOn || _channel == null || _recordPath == null) return;
      if (status == LiveVoiceStatus.paused ||
          status == LiveVoiceStatus.idle ||
          status == LiveVoiceStatus.error) {
        return;
      }
      try {
        final path = await _recorder.stop();
        if (path == null) return;
        final bytes = await File(path).readAsBytes();
        final pcm = _stripWavHeader(bytes);
        if (pcm.isNotEmpty && _channel != null) {
          _channel!.sink.add(pcm);
        }
        if (_micOn &&
            status != LiveVoiceStatus.paused &&
            status != LiveVoiceStatus.idle) {
          _recordPath =
              '${(await getTemporaryDirectory()).path}/kaizen_live_${DateTime.now().millisecondsSinceEpoch}.wav';
          await _recorder.start(
            const RecordConfig(
              encoder: AudioEncoder.wav,
              sampleRate: 16000,
              numChannels: 1,
            ),
            path: _recordPath!,
          );
        }
      } catch (e) {
        if (kDebugMode) debugPrint('mic uplink: $e');
      }
    });
  }

  Uint8List _stripWavHeader(Uint8List wav) {
    if (wav.length < 44) return wav;
    if (wav[0] == 0x52 && wav[1] == 0x49 && wav[2] == 0x46 && wav[3] == 0x46) {
      return Uint8List.sublistView(wav, 44);
    }
    return wav;
  }

  Future<void> _startLocalTranscript() async {
    if (!_speechReady) return;
    await _speech.listen(
      onResult: (result) {
        userPartial = result.recognizedWords;
        notifyListeners();
        if (result.finalResult && userPartial.trim().isNotEmpty) {
          final text = userPartial.trim();
          turns.add(LiveTurn(role: 'user', text: text));
          final sid = _sessionId;
          if (sid != null) {
            unawaited(
              KaizenApi.logTurn(sessionId: sid, role: 'user', content: text),
            );
          }
          _sendText(text);
          userPartial = '';
          notifyListeners();
        }
      },
      listenOptions: stt.SpeechListenOptions(
        partialResults: true,
        listenMode: stt.ListenMode.dictation,
        cancelOnError: false,
      ),
    );
  }

  void _sendText(String text) {
    final ch = _channel;
    if (ch == null) return;
    ch.sink.add(jsonEncode({'type': 'text', 'text': text}));
  }

  void sendChat(String text) {
    final t = text.trim();
    if (t.isEmpty) return;
    turns.add(LiveTurn(role: 'user', text: t));
    notifyListeners();
    _sendText(t);
    final sid = _sessionId;
    if (sid != null) {
      unawaited(KaizenApi.logTurn(sessionId: sid, role: 'user', content: t));
    }
  }

  Future<void> _onWsMessage(dynamic data) async {
    if (data is List<int>) {
      status = LiveVoiceStatus.speaking;
      notifyListeners();
      await _playPcm(Uint8List.fromList(data));
      if (status == LiveVoiceStatus.speaking) {
        status = LiveVoiceStatus.listening;
        notifyListeners();
      }
      return;
    }
    if (data is! String) return;
    try {
      final msg = jsonDecode(data) as Map<String, dynamic>;
      final type = msg['type'] as String?;
      if (type == 'user_transcript_interim' || type == 'user_transcript') {
        userPartial = '${msg['text'] ?? ''}';
        notifyListeners();
      } else if (type == 'assistant_transcript') {
        assistantPartial = _append(assistantPartial, '${msg['text'] ?? ''}');
        notifyListeners();
      } else if (type == 'turn_complete') {
        if (assistantPartial.trim().isNotEmpty) {
          final text = assistantPartial.trim();
          turns.add(LiveTurn(role: 'assistant', text: text));
          final sid = _sessionId;
          if (sid != null) {
            unawaited(
              KaizenApi.logTurn(
                sessionId: sid,
                role: 'assistant',
                content: text,
              ),
            );
          }
        }
        userPartial = '';
        assistantPartial = '';
        status = LiveVoiceStatus.listening;
        notifyListeners();
      } else if (type == 'live_connected' || type == 'ready') {
        status = LiveVoiceStatus.listening;
        notifyListeners();
      } else if (type == 'error') {
        error = '${msg['error'] ?? 'live error'}';
        status = LiveVoiceStatus.error;
        notifyListeners();
      }
    } catch (_) {}
  }

  String _append(String acc, String chunk) {
    if (chunk.isEmpty) return acc;
    if (acc.isEmpty || chunk.startsWith(acc)) return chunk;
    if (acc.startsWith(chunk)) return acc;
    return acc + chunk;
  }

  Future<void> _playPcm(Uint8List pcm) async {
    try {
      final dir = await getTemporaryDirectory();
      final path = '${dir.path}/kaizen_live_out.wav';
      final wav = _pcm16ToWav(pcm, sampleRate: 24000);
      await File(path).writeAsBytes(wav, flush: true);
      await _player.play(DeviceFileSource(path));
    } catch (e) {
      if (kDebugMode) debugPrint('play pcm: $e');
    }
  }

  Uint8List _pcm16ToWav(Uint8List pcm, {required int sampleRate}) {
    final byteRate = sampleRate * 2;
    final header = BytesBuilder();
    header.add(ascii.encode('RIFF'));
    header.add(_le32(36 + pcm.length));
    header.add(ascii.encode('WAVE'));
    header.add(ascii.encode('fmt '));
    header.add(_le32(16));
    header.add(_le16(1));
    header.add(_le16(1));
    header.add(_le32(sampleRate));
    header.add(_le32(byteRate));
    header.add(_le16(2));
    header.add(_le16(16));
    header.add(ascii.encode('data'));
    header.add(_le32(pcm.length));
    header.add(pcm);
    return header.toBytes();
  }

  Uint8List _le16(int v) => Uint8List.fromList([v & 0xff, (v >> 8) & 0xff]);
  Uint8List _le32(int v) => Uint8List.fromList([
        v & 0xff,
        (v >> 8) & 0xff,
        (v >> 16) & 0xff,
        (v >> 24) & 0xff,
      ]);

  Future<void> pause() async {
    _micOn = false;
    status = LiveVoiceStatus.paused;
    _streamTimer?.cancel();
    await _speech.stop();
    if (await _recorder.isRecording()) {
      await _recorder.stop();
    }
    notifyListeners();
  }

  Future<void> resume() async {
    if (_sessionId == null) {
      await connect();
      return;
    }
    _micOn = true;
    status = LiveVoiceStatus.listening;
    notifyListeners();
    await _startMicUplink();
    await _startLocalTranscript();
  }

  Future<void> disconnect() async {
    _micOn = false;
    _streamTimer?.cancel();
    _streamTimer = null;
    await _speech.stop();
    if (await _recorder.isRecording()) {
      await _recorder.stop();
    }
    await _wsSub?.cancel();
    await _channel?.sink.close();
    _wsSub = null;
    _channel = null;
    status = LiveVoiceStatus.idle;
    notifyListeners();
  }

  @override
  void dispose() {
    unawaited(disconnect());
    unawaited(_player.dispose());
    unawaited(_recorder.dispose());
    super.dispose();
  }
}
