import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/ai_action.dart';

// The base URL for the FastAPI backend. This would be a production URL in a real app.
// For the sandbox, we use the exposed port.
const String _baseUrl = 'https://8000-i1ozxlyd16pjoyc08bur9-ce391835.manus.computer';

class ApiService {
  // Mock user ID for the MVP
  final String _userId = 'mock_user_123';

  Future<AiActionSuggestion> suggestAction(EmailContext context) async {
    final url = Uri.parse('$_baseUrl/api/v1/ai/suggest-action');
    
    // In a real app, we would include an Authorization header with a JWT token
    final headers = {'Content-Type': 'application/json'};
    
    // The context object already contains all necessary data
    final body = jsonEncode(context.toJson());

    try {
      final response = await http.post(
        url,
        headers: headers,
        body: body,
      );

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return AiActionSuggestion.fromJson(jsonResponse);
      } else {
        // Handle API errors
        throw Exception('Failed to get AI suggestion. Status: ${response.statusCode}. Body: ${response.body}');
      }
    } catch (e) {
      // Handle network or parsing errors
      throw Exception('Network or processing error: $e');
    }
  }

  // Mock function for user status
  Future<Map<String, dynamic>> getUserStatus() async {
    final url = Uri.parse('$_baseUrl/api/v1/user/status?user_id=$_userId');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get user status');
    }
  }
}
