# Google Play Deployment Guide

This guide walks you through deploying the AI Email Butler app to Google Play Store.

## Prerequisites

1. **Google Play Developer Account**: You need an active Google Play Developer account ($25 one-time fee)
2. **Flutter SDK**: Ensure Flutter is installed and up to date
3. **Android SDK**: Required for building Android apps (comes with Android Studio)

## Step 1: Generate a Signing Key

You need to create a signing key to sign your app bundle for release. **Keep this key secure** - you'll need it to publish updates.

### Generate the Upload Keystore

Run the following command in your terminal:

```bash
keytool -genkey -v -keystore ~/upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

You'll be prompted to:
- Enter a password for the keystore
- Enter a password for the key (can be the same as keystore password)
- Provide your information (name, organization, city, state, country)

**Important**: 
- Store the keystore file (`upload-keystore.jks`) in a secure location
- Keep a backup of the keystore and passwords - if you lose them, you cannot update your app
- Never commit the keystore to version control

## Step 2: Configure Signing

1. Copy the template file to create your configuration:
   ```bash
   cd android
   cp key.properties.template key.properties
   ```

2. Edit `android/key.properties` with your actual values:
   ```
   storePassword=<your-keystore-password>
   keyPassword=<your-key-password>
   keyAlias=upload
   storeFile=<path-to-your-upload-keystore.jks>
   ```

   Example:
   ```
   storePassword=mySecurePassword123
   keyPassword=mySecurePassword123
   keyAlias=upload
   storeFile=/Users/yourname/upload-keystore.jks
   ```

   Or use a relative path from the android directory:
   ```
   storeFile=../upload-keystore.jks
   ```

**Note**: The `key.properties` file is already in `.gitignore` and will not be committed to version control.

## Step 3: Update Application ID (Package Name)

Before building, you should update the application ID to your own unique identifier.

1. Edit `android/app/build.gradle.kts`
2. Change the `applicationId`:
   ```kotlin
   applicationId = "com.yourcompany.aiemailbutler"
   ```

**Important**: 
- Use reverse domain notation (e.g., `com.example.appname`)
- Once published to Google Play, this cannot be changed
- Must be unique across all apps on Google Play

## Step 4: Update App Metadata

1. Edit `pubspec.yaml` to set your version:
   ```yaml
   version: 1.0.0+1
   ```
   - The first part (1.0.0) is the version name shown to users
   - The +1 is the version code (build number) - increment this for each release

2. Update the app name in `android/app/src/main/AndroidManifest.xml`:
   ```xml
   android:label="AI Email Butler"
   ```

## Step 5: Build the App Bundle

Flutter can build an Android App Bundle (.aab), which is the recommended format for Google Play.

```bash
cd ai_email_butler
flutter build appbundle
```

This will:
1. Compile your Flutter app
2. Generate an optimized release build
3. Sign it with your upload key
4. Create the `.aab` file

The final file will be located at:
```
build/app/outputs/bundle/release/app-release.aab
```

### Build Options

You can specify custom version information:
```bash
flutter build appbundle --build-name=1.0.0 --build-number=1
```

## Step 6: Prepare Play Store Listing

Before uploading, prepare the following assets:

### Required Assets

1. **App Icon**: 512x512 PNG (high-res icon)
2. **Feature Graphic**: 1024x500 PNG
3. **Screenshots**: At least 2 screenshots
   - Phone: 16:9 or 9:16 aspect ratio
   - Minimum dimension: 320px
   - Maximum dimension: 3840px

### Required Information

1. **App Details**:
   - App name (up to 50 characters)
   - Short description (up to 80 characters)
   - Full description (up to 4000 characters)

2. **Categorization**:
   - Application type (App or Game)
   - Category (e.g., Productivity, Communication)
   - Content rating (complete questionnaire)

3. **Contact Details**:
   - Email address
   - Privacy policy URL (required)
   - Website (optional)

4. **Pricing & Distribution**:
   - Free or Paid
   - Countries to distribute
   - Content rating

## Step 7: Upload to Google Play Console

1. Go to [Google Play Console](https://play.google.com/console/)
2. Click "Create app"
3. Fill in the basic app details
4. In the left sidebar, go to "Production" → "Releases"
5. Click "Create new release"
6. Upload your `app-release.aab` file
7. Fill in the release notes
8. Click "Review release" and then "Start rollout to production"

## Step 8: App Review

After submission:
1. Google will review your app (typically 1-3 days)
2. You may need to address any policy violations or technical issues
3. Once approved, your app will be live on Google Play

## Updating Your App

To release an update:

1. Update the version in `pubspec.yaml`:
   ```yaml
   version: 1.1.0+2  # Increment version name and/or build number
   ```

2. Rebuild the app bundle:
   ```bash
   flutter build appbundle
   ```

3. Upload the new `.aab` file in Play Console → Production → Create new release

## Troubleshooting

### Build Errors

If you get signing errors:
- Verify `key.properties` file exists and has correct values
- Check that the keystore file path is correct
- Ensure passwords are correct

### Version Conflicts

If Google Play rejects your upload:
- Ensure the version code is higher than the previous release
- Each upload must have a unique version code

### Missing Permissions

If the app doesn't work correctly:
- Check that all required permissions are in `AndroidManifest.xml`
- The app currently has `INTERNET` permission for API calls

## Security Best Practices

1. **Never commit sensitive files**:
   - `key.properties`
   - `*.keystore` or `*.jks` files
   - These are already in `.gitignore`

2. **Backup your keystore**:
   - Store in a secure, encrypted location
   - Keep multiple backups
   - Document the passwords securely

3. **Use Google Play App Signing** (Recommended):
   - Enroll in Google Play App Signing in Play Console
   - Google will manage your app signing key
   - You only need to keep your upload key

## Additional Resources

- [Flutter Deployment Documentation](https://docs.flutter.dev/deployment/android)
- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [Android App Bundle Format](https://developer.android.com/guide/app-bundle)
- [Google Play Policies](https://play.google.com/about/developer-content-policy/)

## Continuous Integration / Continuous Deployment (CI/CD)

### GitHub Actions Setup

The repository includes a GitHub Actions workflow (`.github/workflows/android-build.yml`) that automatically builds the app on every push. By default, it creates a debug build.

To enable automated release builds with proper signing:

1. **Encode your keystore file as base64**:
   ```bash
   base64 -i upload-keystore.jks | tr -d '\n' > keystore-base64.txt
   ```

2. **Add secrets to GitHub repository**:
   Go to your repository → Settings → Secrets and variables → Actions, and add:
   - `KEYSTORE_BASE64`: Content of `keystore-base64.txt`
   - `KEYSTORE_PASSWORD`: Your keystore password
   - `KEY_PASSWORD`: Your key password
   - `KEY_ALIAS`: Your key alias (usually "upload")

3. **Update the workflow** to decode the keystore and create key.properties:
   ```yaml
   - name: Decode keystore
     env:
       KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
     run: |
       echo $KEYSTORE_BASE64 | base64 -d > android/upload-keystore.jks
     working-directory: ai_email_butler

   - name: Create key.properties
     env:
       KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
       KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
       KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
     run: |
       cat > android/key.properties << EOF
       storePassword=$KEYSTORE_PASSWORD
       keyPassword=$KEY_PASSWORD
       keyAlias=$KEY_ALIAS
       storeFile=../upload-keystore.jks
       EOF
     working-directory: ai_email_butler

   - name: Build release bundle
     run: flutter build appbundle --release
     working-directory: ai_email_butler
   ```

This allows you to build signed release bundles in your CI/CD pipeline.
