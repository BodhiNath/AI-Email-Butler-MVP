# AI Email Butler (Flutter MVP)

This is the cross-platform client application for the AI Email Automation project, built with **Flutter** to ensure a lightweight, single-codebase solution for Android, Windows, and Linux.

## Features (MVP)
- **Core UI:** Dashboard for viewing mock email and workflow status.
- **API Integration:** Secure communication with the serverless FastAPI backend.
- **Workflow Simulation:** Triggers the AI workflow engine to get a structured action suggestion (draft reply, archive, etc.).

## Getting Started

### 1. Prerequisites
- Flutter SDK installed and configured.
- Android Studio/VS Code with Flutter plugins (for development).

### 2. Setup
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ai_email_butler
    ```
2.  **Get dependencies:**
    ```bash
    flutter pub get
    ```

### 3. Running the App

The application is configured to call the backend API at the URL specified in `lib/services/api_service.dart`. **Ensure the backend is running and accessible.**

- **For Android/iOS (Mobile):**
  ```bash
  flutter run
  ```
- **For Desktop (Linux/Windows/macOS):**
  ```bash
  # Enable desktop support (if not already done)
  flutter config --enable-linux-desktop # or --enable-windows-desktop
  flutter run -d linux # or -d windows
  ```

## Deployment to Google Play

For detailed instructions on deploying this app to Google Play Store, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Quick Start

1. Generate a signing key:
   ```bash
   keytool -genkey -v -keystore ~/upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
   ```

2. Configure signing:
   ```bash
   cd android
   cp key.properties.template key.properties
   # Edit key.properties with your keystore details
   ```

3. Build the app bundle:
   ```bash
   flutter build appbundle
   ```

4. Upload `build/app/outputs/bundle/release/app-release.aab` to Google Play Console.

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions.

## Future Scope (Calendar + Contacts)

The architecture is designed to support the expansion to Calendar and Contacts. This will primarily involve:
1.  Adding new API endpoints to the backend (e.g., `/api/v1/calendar/sync`, `/api/v1/contacts/sync`).
2.  Updating the Flutter app to handle OAuth for Calendar/Contacts services and display the new UI components.
3.  Expanding the `AiActionSuggestion` model to include actions like `schedule_meeting` or `update_contact`.
'contact`update_contact`.
