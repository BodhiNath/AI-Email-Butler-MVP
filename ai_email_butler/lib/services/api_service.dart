import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/ai_action.dart';
import '../exceptions/api_exceptions.dart';

class ApiService {
  final http.Client _httpClient;
  final String _jwtToken;
  final String _userId;
  
  // Retry configuration
  static const int _maxRetries = ApiConfig.maxRetries;
  static const Duration _retryDelay = ApiConfig.retryDelay;

  ApiService({
    http.Client? httpClient,
    required String jwtToken,
    required String userId,
  })  : _httpClient = httpClient ?? http.Client(),
        _jwtToken = jwtToken,
        _userId = userId;

  /// Build standard headers with JWT authentication
  Map<String, String> _buildHeaders({String? aiProvider}) {
    final base = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Bearer $_jwtToken',
    };
    if (aiProvider != null && aiProvider.isNotEmpty) {
      base['X-AI-Provider'] = aiProvider;
    }
    return base;
  }

  /// Execute HTTP request with retry logic and error handling
  Future<T> _executeRequest<T>({
    required Future<http.Response> Function() request,
    required T Function(Map<String, dynamic>) parser,
  }) async {
    int retryCount = 0;
    
    while (retryCount < _maxRetries) {
      try {
        final response = await request().timeout(
          ApiConfig.connectionTimeout,
          onTimeout: () => throw TimeoutException('Request timeout'),
        );

        switch (response.statusCode) {
          case 200:
            final jsonResponse = jsonDecode(response.body) as Map<String, dynamic>;
            return parser(jsonResponse);
          
          case 400:
            throw ValidationException(
              message: _extractErrorMessage(response.body) ?? 'Invalid request',
            );
          
          case 401:
            throw AuthenticationException(
              message: _extractErrorMessage(response.body) ?? 'Unauthorized',
            );
          
          case 429:
            throw RateLimitException();
          
          case 500:
          case 502:
          case 503:
          case 504:
            throw ServerException(
              message: _extractErrorMessage(response.body) ?? 'Server error',
              statusCode: response.statusCode,
            );
          
          default:
            throw ServerException(
              message: 'Unexpected status code: ${response.statusCode}',
              statusCode: response.statusCode,
            );
        }
      } on TimeoutException catch (_) {
        retryCount++;
        if (retryCount >= _maxRetries) {
          throw NetworkException(
            message: 'Request timeout after $_maxRetries attempts',
            originalError: _,
          );
        }
        await Future.delayed(_retryDelay * retryCount);
      } on SocketException catch (e) {
        retryCount++;
        if (retryCount >= _maxRetries) {
          throw NetworkException(
            message: 'Network error: ${e.message}',
            originalError: e,
          );
        }
        await Future.delayed(_retryDelay * retryCount);
      } on ApiException {
        rethrow;
      } catch (e) {
        throw NetworkException(
          message: 'Unexpected error: $e',
          originalError: e,
        );
      }
    }
    
    throw NetworkException(
      message: 'Max retries exceeded',
      originalError: null,
    );
  }

  /// Extract error message from response body
  String? _extractErrorMessage(String body) {
    try {
      final json = jsonDecode(body) as Map<String, dynamic>;
      return json['detail'] as String?;
    } catch (_) {
      return null;
    }
  }

  /// Get AI action suggestion for an email
  Future<AiActionSuggestion> suggestAction(EmailContext context, {String? aiProvider}) async {
    return _executeRequest(
      request: () => _httpClient.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.suggestActionEndpoint}'),
        headers: _buildHeaders(aiProvider: aiProvider),
        body: jsonEncode(context.toJson()),
      ),
      parser: (json) => AiActionSuggestion.fromJson(json),
    );
  }

  /// Get user subscription status and usage metrics
  Future<Map<String, dynamic>> getUserStatus() async {
    return _executeRequest(
      request: () => _httpClient.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.userStatusEndpoint}?user_id=$_userId'),
        headers: _buildHeaders(),
      ),
      parser: (json) => json,
    );
  }

  /// Add a new external account (OAuth flow)
  Future<Map<String, dynamic>> addAccount(String provider) async {
    return _executeRequest(
      request: () => _httpClient.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.addAccountEndpoint}?user_id=$_userId&provider=$provider'),
        headers: _buildHeaders(),
      ),
      parser: (json) => json,
    );
  }

  /// Sync workflows to backend
  Future<Map<String, dynamic>> syncWorkflows(List<dynamic> workflows) async {
    return _executeRequest(
      request: () => _httpClient.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.syncWorkflowsEndpoint}?user_id=$_userId'),
        headers: _buildHeaders(),
        body: jsonEncode({'workflows': workflows}),
      ),
      parser: (json) => json,
    );
  }

  /// Log an action
  Future<Map<String, dynamic>> logAction(Map<String, dynamic> actionLog) async {
    return _executeRequest(
      request: () => _httpClient.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.logActionEndpoint}'),
        headers: _buildHeaders(),
        body: jsonEncode(actionLog),
      ),
      parser: (json) => json,
    );
  }

  /// Cleanup resources
  void dispose() {
    _httpClient.close();
  }
}
