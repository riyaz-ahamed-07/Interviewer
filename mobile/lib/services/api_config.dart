class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE',
    defaultValue: 'https://interviewer-api-w02p.onrender.com',
  );

  static String get wsBase {
    if (baseUrl.startsWith('https')) {
      return baseUrl.replaceFirst('https', 'wss');
    }
    return baseUrl.replaceFirst('http', 'ws');
  }

  static String liveWsUrl(String sessionId, {bool resume = false}) {
    final q = resume ? '?resume=1' : '';
    return '$wsBase/ws/live/$sessionId$q';
  }
}
