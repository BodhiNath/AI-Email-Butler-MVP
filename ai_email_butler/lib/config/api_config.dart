/// API Configuration for AI Email Butler
/// This centralized configuration allows for environment-specific API endpoints
class ApiConfig {
  // Development
  static const String devBaseUrl = 'http://localhost:8000';
  
  // Production
  static const String prodBaseUrl = 'https://api.email-butler.com';
  
  // Staging
  static const String stagingBaseUrl = 'https://staging-api.email-butler.com';
  
  /// Get the appropriate base URL based on environment
  /// Override via String.fromEnvironment('API_BASE_URL') or Platform environment variables
  static String get baseUrl {
    const baseUrl = String.fromEnvironment('API_BASE_URL');
    if (baseUrl.isNotEmpty) {
      return baseUrl;
    }
    // Default to development for local testing
    return devBaseUrl;
  }
  
  /// API Endpoints
  static const String userStatusEndpoint = '/api/v1/user/status';
  static const String suggestActionEndpoint = '/api/v1/ai/suggest-action';
  static const String addAccountEndpoint = '/api/v1/accounts/add';
  static const String syncWorkflowsEndpoint = '/api/v1/workflows/sync';
  static const String logActionEndpoint = '/api/v1/actions/log';
  
  /// HTTP configuration
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 2);
}
