import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_config.dart';

class KaizenApi {
  KaizenApi._();

  static Future<Map<String, dynamic>> startFriendSession({
    String mode = 'medium',
  }) async {
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/api/session/friend/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'mode': mode}),
    );
    if (res.statusCode >= 400) {
      throw Exception(res.body.isEmpty ? res.reasonPhrase : res.body);
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<void> logTurn({
    required String sessionId,
    required String role,
    required String content,
  }) async {
    await http.post(
      Uri.parse('${ApiConfig.baseUrl}/api/session/$sessionId/log'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'role': role, 'content': content}),
    );
  }
}
