# AI Email Butler - Flutter Frontend

A Flutter-based mobile and desktop application for intelligent email automation with AI-powered action suggestions.

## Overview

The AI Email Butler frontend is a cross-platform application built with Flutter that communicates with a secure FastAPI backend to provide:

- ✅ AI-powered email analysis
- ✅ Smart action suggestions (reply, archive, flag)
- ✅ User-defined workflow automation
- ✅ JWT-based authentication
- ✅ Comprehensive error handling
- ✅ Support for Android, iOS, Web, and Desktop

## Architecture

### Technology Stack
- **Framework:** Flutter 3.10+
- **Language:** Dart 3.10+
- **State Management:** Provider
- **HTTP Client:** http + Dio
- **Storage:** SharedPreferences
- **Authentication:** JWT with jwt_decoder
- **Environment:** flutter_dotenv

### Project Structure

```
ai_email_butler/
├── lib/
│   ├── main.dart                 # Application entry point
│   ├── config/
│   │   └── api_config.dart       # API configuration and endpoints
│   ├── models/
│   │   └── ai_action.dart        # Data models (AiActionSuggestion, EmailContext)
│   ├── services/
│   │   └── api_service.dart      # API communication with retry logic
│   ├── exceptions/
│   │   └── api_exceptions.dart   # Custom exception classes
│   └── screens/
│       └── email_dashboard.dart  # Main UI screen
├── test/
│   └── widget_test.dart          # Widget and integration tests
├── pubspec.yaml                  # Dependencies
├── .env.example                  # Environment configuration template
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- Flutter SDK 3.10 or higher ([Install Flutter](https://flutter.dev/docs/get-started/install))
- Dart 3.10 or higher (included with Flutter)
- A backend instance running on `localhost:8000` or configure the API URL
- Valid JWT token from the backend

### 2. Installation

```bash
# Clone or navigate to the project
cd ai_email_butler

# Get dependencies
flutter pub get

# (Optional) Generate code if using json_serializable
flutter pub run build_runner build
```

### 3. Environment Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Configure the backend URL:

```env
API_BASE_URL=http://localhost:8000
DEBUG_MODE=true
```

### 4. Run the Application

```bash
# Development mode (hot reload)
flutter run

# Release build (Android)
flutter build apk --release

# Release build (iOS)
flutter build ios --release

# Web build
flutter build web

# Desktop (Linux/Windows/macOS)
flutter run -d linux
```

## API Integration

### Authentication

The app uses JWT token-based authentication. Tokens are passed in the Authorization header:

```dart
headers: {
  'Authorization': 'Bearer $jwtToken',
  'Content-Type': 'application/json',
}
```

### API Service

The `ApiService` class handles all backend communication with:
- Automatic retry logic (configurable)
- Connection timeout handling
- Comprehensive error handling
- Rate limit awareness

**Example Usage:**

```dart
final apiService = ApiService(
  jwtToken: 'your_jwt_token',
  userId: 'user_id',
);

try {
  final suggestion = await apiService.suggestAction(emailContext);
  print('Action: ${suggestion.action}');
} on RateLimitException catch (e) {
  print('Rate limited: ${e.message}');
} on NetworkException catch (e) {
  print('Network error: ${e.message}');
}
```

### Error Handling

The app includes custom exception classes for different error scenarios:

```dart
- ValidationException    // 400 Bad Request
- AuthenticationException // 401 Unauthorized
- RateLimitException     // 429 Too Many Requests
- ServerException        // 500+ Server Errors
- NetworkException       // Connection failures
```

## Features

### Email Dashboard
- Display incoming email preview
- Show AI action suggestion with confidence score
- Display permission level (auto-send, draft-only, needs-review)
- Show draft reply if available
- Error messages with user-friendly formatting

### API Configuration
- Environment-specific base URLs
- Configurable timeouts and retry logic
- Easy switching between dev/staging/production

### State Management
- StatefulWidget with proper lifecycle management
- Error state handling
- Loading indicators
- Responsive UI updates

## Testing

### Run Tests

```bash
# Run all widget tests
flutter test

# Run with coverage
flutter test --coverage

# View coverage report (requires lcov)
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

### Test Coverage
- Widget rendering
- Button interactions
- Error display
- Data model serialization
- API service communication

## Configuration

### API Configuration (`lib/config/api_config.dart`)

```dart
class ApiConfig {
  static const String devBaseUrl = 'http://localhost:8000';
  static const String prodBaseUrl = 'https://api.email-butler.com';
  static const String stagingBaseUrl = 'https://staging-api.email-butler.com';
  
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const int maxRetries = 3;
}
```

Override the base URL:
```bash
flutter run --dart-define=API_BASE_URL=https://api.email-butler.com
```

## Building for Production

### Android
```bash
# Build signed APK
flutter build apk --release

# Build App Bundle (for Google Play)
flutter build appbundle --release
```

### iOS
```bash
# Build and sign
flutter build ios --release

# Create IPA
cd ios && xcodebuild -workspace Runner.xcworkspace -scheme Runner -configuration Release -derivedDataPath build -archivePath build/Runner.xcarchive -archive
```

### Web
```bash
flutter build web --web-renderer html
# Or for better performance:
flutter build web --web-renderer canvaskit
```

## Troubleshooting

### "Connection refused" errors
- Ensure backend is running on the configured URL
- Check `API_BASE_URL` in `.env`
- Verify firewall allows connections

### "Invalid token" errors
- Get a new JWT token from the backend
- Verify token is not expired
- Check JWT_SECRET on backend matches

### "Rate limit exceeded"
- Wait before retrying (exponential backoff is automatic)
- Reduce request frequency
- Contact backend admin for higher limits

### Hot reload not working
- Run `flutter clean`
- Restart the app
- Check for Dart syntax errors

## Performance Optimization

1. **Image caching:** Use `cached_network_image` for remote images
2. **Lazy loading:** Load data on demand
3. **Code splitting:** Use dynamic imports for large features
4. **Profiling:** Use `flutter run --profile`

## Security Best Practices

1. **Never hardcode tokens** in source code
2. **Use secure storage** for sensitive data (SharedPreferences + encryption)
3. **Validate SSL certificates** in production
4. **Implement token refresh** before expiration
5. **Sanitize user input** before sending to API
6. **Use HTTPS** in production

## CI/CD

The project includes GitHub Actions workflows:
- Automated testing on every push
- Code analysis and linting
- APK/IPA builds on successful tests
- Artifact uploads

See `.github/workflows/flutter.yml`

## Dependencies

- **http** (1.6.0+) - HTTP client
- **dio** (5.3.0+) - Advanced HTTP client
- **provider** (6.1.0+) - State management
- **shared_preferences** (2.2.0+) - Local storage
- **jwt_decoder** (2.0.1+) - JWT token parsing
- **flutter_dotenv** (5.1.0+) - Environment variables
- **logger** (2.0.0+) - Logging utility

## Future Scope (Calendar + Contacts)

The architecture is designed to support expansion to Calendar and Contacts:
1. Adding new API endpoints to the backend (e.g., `/api/v1/calendar/sync`, `/api/v1/contacts/sync`)
2. Updating Flutter app to handle OAuth for Calendar/Contacts services
3. Expanding the `AiActionSuggestion` model to include actions like `schedule_meeting` or `update_contact`
4. Adding new UI screens for Calendar and Contacts management

## Contribution Guidelines

1. Create a branch for your feature
2. Follow Dart style guidelines
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flutter documentation: https://flutter.dev/docs
3. Open an issue in the repository
4. Contact the development team

---

**Last Updated:** November 15, 2025
**Version:** 1.0.0-MVP
