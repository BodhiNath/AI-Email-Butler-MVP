# Google Play Deployment - Quick Reference

This document provides a quick overview of the Google Play deployment setup for AI Email Butler.

## What's Been Set Up

This repository is now fully configured for deploying the Flutter app to Google Play Store with:

✅ **Signing Configuration**
- Template file for signing keys (`android/key.properties.template`)
- Build configuration that loads signing keys securely
- Fallback to debug signing for development/CI

✅ **Build Configuration**
- Android build gradle files properly configured
- Internet permissions added to AndroidManifest
- Version management ready in pubspec.yaml

✅ **Documentation**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Complete step-by-step deployment guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Interactive checklist
- [README.md](README.md) - Quick start instructions

✅ **Automation**
- GitHub Actions workflow for automated builds
- Security scanning configured
- Build artifacts automatically uploaded

✅ **Security**
- Sensitive files properly excluded from git
- Minimal permissions in CI/CD
- Security best practices documented

## Quick Start (First Time Deployment)

### 1. Generate Signing Key (5 minutes)
```bash
keytool -genkey -v -keystore ~/upload-keystore.jks \
  -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

### 2. Configure Signing (2 minutes)
```bash
cd ai_email_butler/android
cp key.properties.template key.properties
# Edit key.properties with your keystore details
```

### 3. Build App Bundle (5-10 minutes)
```bash
cd ai_email_butler
flutter build appbundle
```
Output: `build/app/outputs/bundle/release/app-release.aab`

### 4. Upload to Google Play (15-30 minutes)
1. Go to [Google Play Console](https://play.google.com/console/)
2. Create new app or select existing app
3. Go to Production → Releases → Create new release
4. Upload `app-release.aab`
5. Complete store listing information
6. Submit for review

**Total time for first deployment: ~30-60 minutes**

## Quick Start (Updating Existing App)

### 1. Update Version (1 minute)
Edit `ai_email_butler/pubspec.yaml`:
```yaml
version: 1.1.0+2  # Increment version
```

### 2. Build New Bundle (5 minutes)
```bash
cd ai_email_butler
flutter build appbundle
```

### 3. Upload to Play Console (5 minutes)
1. Production → Create new release
2. Upload new `app-release.aab`
3. Add release notes
4. Submit

**Total time for updates: ~10-15 minutes**

## File Locations

| File | Purpose | Location |
|------|---------|----------|
| App Bundle | Upload to Play Store | `ai_email_butler/build/app/outputs/bundle/release/app-release.aab` |
| Keystore | Signing releases (keep secure!) | `~/upload-keystore.jks` (or your chosen location) |
| Signing Config | Local signing settings | `ai_email_butler/android/key.properties` |
| Build Config | Gradle build settings | `ai_email_butler/android/app/build.gradle.kts` |

## Important Notes

### ⚠️ Security
- **Never commit** `key.properties`, `*.keystore`, or `*.jks` files to git
- **Back up** your keystore file - you cannot update your app without it
- **Document** your keystore passwords securely

### 📱 Version Management
- **Version Code** (the number after +) must always increase
- **Version Name** (before +) is shown to users
- Example progression: `1.0.0+1` → `1.0.1+2` → `1.1.0+3`

### 🔄 CI/CD
- GitHub Actions automatically builds on every push
- Uses debug signing by default
- See [DEPLOYMENT.md](DEPLOYMENT.md#continuous-integration--continuous-deployment-cicd) for release signing setup

## Need Help?

- **Detailed Instructions**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Step-by-step Checklist**: See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Build Issues**: Check the troubleshooting section in [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)
- **Google Play Help**: [support.google.com/googleplay/android-developer](https://support.google.com/googleplay/android-developer)

## Next Steps

1. ✅ Configuration complete - you're ready to deploy!
2. 📝 Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
3. 🔐 Generate your signing key
4. 🚀 Build and deploy to Google Play

---

**Last Updated**: This setup was completed as part of the "Deploy to Google Play" implementation.
