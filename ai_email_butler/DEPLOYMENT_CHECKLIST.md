# Google Play Deployment Checklist

Use this checklist to ensure you've completed all steps before deploying to Google Play.

## Pre-Deployment Checklist

### 1. Signing Configuration
- [ ] Generated upload keystore using `keytool`
- [ ] Stored keystore in a secure location
- [ ] Created backup of keystore file
- [ ] Documented keystore passwords securely
- [ ] Created `android/key.properties` from template
- [ ] Verified `key.properties` is in `.gitignore`

### 2. App Configuration
- [ ] Updated `applicationId` in `android/app/build.gradle.kts`
- [ ] Updated version in `pubspec.yaml` (e.g., `1.0.0+1`)
- [ ] Updated app label in `AndroidManifest.xml`
- [ ] Verified all required permissions are in `AndroidManifest.xml`

### 3. App Assets
- [ ] App icon (512x512 PNG)
- [ ] Feature graphic (1024x500 PNG)
- [ ] At least 2 screenshots (phone)
- [ ] Screenshots for tablet (optional but recommended)

### 4. App Information
- [ ] App name (max 50 characters)
- [ ] Short description (max 80 characters)
- [ ] Full description (max 4000 characters)
- [ ] Privacy policy URL (required)
- [ ] Contact email
- [ ] Website (optional)

### 5. Legal & Compliance
- [ ] Completed content rating questionnaire
- [ ] Reviewed Google Play policies
- [ ] Prepared privacy policy
- [ ] Agreed to developer distribution agreement

### 6. Build & Test
- [ ] Built app bundle: `flutter build appbundle`
- [ ] Verified `.aab` file exists at `build/app/outputs/bundle/release/app-release.aab`
- [ ] Tested app on physical device
- [ ] Tested all core features
- [ ] Verified no crashes or critical bugs

### 7. Google Play Console
- [ ] Created Google Play Developer account
- [ ] Created new app in Play Console
- [ ] Filled in store listing
- [ ] Uploaded app bundle
- [ ] Set up pricing & distribution
- [ ] Completed content rating
- [ ] Reviewed app preview before submission

## Post-Deployment Checklist

### After Submission
- [ ] Monitor app review status
- [ ] Respond to any review feedback
- [ ] Set up crash reporting (recommended)
- [ ] Set up analytics (recommended)

### After Approval
- [ ] Verify app appears in Play Store
- [ ] Test installation from Play Store
- [ ] Monitor user reviews
- [ ] Monitor crash reports
- [ ] Plan for updates and maintenance

## Version Update Checklist

When releasing an update:

- [ ] Increment version code in `pubspec.yaml`
- [ ] Update version name if needed
- [ ] Test all changes thoroughly
- [ ] Build new app bundle: `flutter build appbundle`
- [ ] Write release notes
- [ ] Upload to Play Console
- [ ] Create new release in production track
- [ ] Monitor rollout

## Notes

- Version code must always increase with each release
- Keep your keystore secure - losing it means you can't update your app
- Consider enrolling in Google Play App Signing for additional security
- Test on multiple devices and Android versions when possible
- Review Google Play policies regularly for updates
