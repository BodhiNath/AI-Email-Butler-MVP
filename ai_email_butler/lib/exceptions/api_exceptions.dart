/// Custom exceptions for API operations
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic originalError;

  ApiException({
    required this.message,
    this.statusCode,
    this.originalError,
  });

  @override
  String toString() => 'ApiException: $message${statusCode != null ? ' (Status: $statusCode)' : ''}';
}

class NetworkException extends ApiException {
  NetworkException({required String message, dynamic originalError})
      : super(message: message, originalError: originalError);
}

class AuthenticationException extends ApiException {
  AuthenticationException({required String message})
      : super(message: message, statusCode: 401);
}

class RateLimitException extends ApiException {
  RateLimitException({String message = 'Rate limit exceeded. Please try again later.'})
      : super(message: message, statusCode: 429);
}

class ValidationException extends ApiException {
  ValidationException({required String message})
      : super(message: message, statusCode: 400);
}

class ServerException extends ApiException {
  ServerException({required String message, int? statusCode})
      : super(message: message, statusCode: statusCode ?? 500);
}
