# Google Play Deployment Architecture

This document describes the deployment architecture and workflow for the AI Email Butler app.

## Deployment Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEVELOPER WORKSTATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Generate Signing Key (One-time)                             │
│     └─> keytool -genkey -v -keystore upload-keystore.jks       │
│         └─> Outputs: upload-keystore.jks                        │
│                                                                   │
│  2. Configure Signing                                            │
│     └─> Copy key.properties.template → key.properties           │
│     └─> Edit with keystore path and passwords                   │
│                                                                   │
│  3. Build App Bundle                                             │
│     └─> flutter build appbundle                                 │
│         └─> Reads: android/key.properties                       │
│         └─> Uses: upload-keystore.jks                           │
│         └─> Outputs: build/app/outputs/bundle/release/*.aab     │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Upload .aab file
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   GOOGLE PLAY CONSOLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Create/Select App                                            │
│  2. Production → Create Release                                  │
│  3. Upload app-release.aab                                       │
│  4. Add Release Notes                                            │
│  5. Review & Submit                                              │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ App Review Process (1-3 days)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      GOOGLE PLAY STORE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  App Published & Available for Download                          │
│  └─> Users can install AI Email Butler                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## CI/CD Pipeline (Optional)

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Trigger: Push to main/develop                                   │
│     │                                                             │
│     ├─> 1. Checkout Code                                         │
│     ├─> 2. Setup Java 17                                         │
│     ├─> 3. Setup Flutter 3.24.0                                  │
│     ├─> 4. flutter pub get                                       │
│     ├─> 5. flutter analyze                                       │
│     ├─> 6. flutter test                                          │
│     └─> 7. flutter build appbundle --debug                       │
│         └─> Upload artifact (for testing)                        │
│                                                                   │
│  For Release Builds (with secrets):                              │
│     ├─> Decode KEYSTORE_BASE64 → upload-keystore.jks           │
│     ├─> Create key.properties from secrets                      │
│     └─> flutter build appbundle --release                       │
│         └─> Upload signed .aab artifact                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
AI-Email-Butler-MVP/
├── .github/
│   └── workflows/
│       └── android-build.yml          # CI/CD workflow
│
├── ai_email_butler/                   # Flutter app
│   ├── android/
│   │   ├── app/
│   │   │   ├── build.gradle.kts       # ✏️ Modified: Signing config
│   │   │   └── src/main/
│   │   │       └── AndroidManifest.xml # ✏️ Modified: Added INTERNET permission
│   │   │
│   │   └── key.properties.template     # 🆕 Template for signing config
│   │   └── key.properties             # ⚠️  GITIGNORED - Create from template
│   │
│   ├── build/app/outputs/bundle/
│   │   └── release/
│   │       └── app-release.aab        # Generated by flutter build
│   │
│   ├── DEPLOYMENT.md                   # 🆕 Complete deployment guide
│   ├── DEPLOYMENT_CHECKLIST.md         # 🆕 Deployment checklist
│   ├── GOOGLE_PLAY_QUICK_START.md      # 🆕 Quick reference
│   └── README.md                       # ✏️ Modified: Added deployment section
│
└── upload-keystore.jks                 # ⚠️  GITIGNORED - Keep secure!
```

## Component Responsibilities

### Configuration Files

| File | Purpose | Security | Modified By |
|------|---------|----------|-------------|
| `build.gradle.kts` | Build configuration, signing setup | Public (no secrets) | This PR |
| `AndroidManifest.xml` | App permissions and metadata | Public | This PR |
| `key.properties.template` | Template for signing config | Public | This PR |
| `key.properties` | Actual signing credentials | **GITIGNORED** | Developer |
| `upload-keystore.jks` | Signing key | **GITIGNORED** | keytool |

### Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| `DEPLOYMENT.md` | Complete deployment guide | Developers deploying to Play Store |
| `DEPLOYMENT_CHECKLIST.md` | Interactive checklist | Developers during deployment |
| `GOOGLE_PLAY_QUICK_START.md` | Quick reference | Developers (quick lookup) |
| `README.md` | Project overview | All developers |
| `DEPLOYMENT_ARCHITECTURE.md` | This file - architecture overview | Technical stakeholders |

## Signing Key Security Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Layer 1: .gitignore                                             │
│  ├─> key.properties      → Never committed                       │
│  ├─> *.keystore          → Never committed                       │
│  └─> *.jks               → Never committed                       │
│                                                                   │
│  Layer 2: Local Storage                                          │
│  ├─> Keystore stored outside repo (recommended)                  │
│  └─> Backed up to secure location                               │
│                                                                   │
│  Layer 3: Password Protection                                    │
│  ├─> Keystore password protects the file                        │
│  └─> Key password protects the signing key                      │
│                                                                   │
│  Layer 4: CI/CD (Optional)                                       │
│  ├─> Keystore encoded as base64 in GitHub Secrets               │
│  └─> Passwords stored in GitHub Secrets                         │
│                                                                   │
│  Layer 5: Google Play App Signing (Recommended)                  │
│  ├─> Google manages app signing key                             │
│  └─> Developer only needs upload key                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Build Configuration Logic

```kotlin
// In build.gradle.kts

1. Check if key.properties exists
   ├─> YES: Load signing configuration
   │   ├─> Create "release" signing config
   │   ├─> keyAlias from key.properties
   │   ├─> keyPassword from key.properties
   │   ├─> storeFile from key.properties
   │   └─> storePassword from key.properties
   │
   └─> NO: Use debug signing (for testing/CI)

2. Release build type
   ├─> If key.properties exists: Use release signing
   └─> Otherwise: Use debug signing (fallback)
```

## Version Management Strategy

```
Version Format: MAJOR.MINOR.PATCH+BUILD

Example Progression:
  1.0.0+1   → Initial release
  1.0.1+2   → Bug fix
  1.0.2+3   → Another bug fix
  1.1.0+4   → New feature
  2.0.0+5   → Major update

Rules:
  ✓ BUILD number must always increase
  ✓ BUILD number never resets
  ✓ Version shown to users: MAJOR.MINOR.PATCH
  ✓ Version used by Play Store: BUILD
```

## Deployment Lifecycle

```
Phase 1: Initial Setup (One-time)
├─> Generate keystore
├─> Configure key.properties
├─> Create Play Console account
└─> Create app in Play Console

Phase 2: First Release
├─> Build app bundle
├─> Complete store listing
├─> Upload .aab
├─> Submit for review
└─> Wait for approval (1-3 days)

Phase 3: Ongoing Updates
├─> Increment version
├─> Build new bundle
├─> Upload to Play Console
├─> Add release notes
└─> Submit for review

Phase 4: Maintenance
├─> Monitor crash reports
├─> Review user feedback
├─> Plan updates
└─> Iterate
```

## Testing Strategy

### Local Testing
```bash
# Debug build (no signing required)
flutter run

# Release build (requires signing)
flutter build appbundle
```

### CI/CD Testing
```
GitHub Actions runs on every push:
├─> flutter analyze (code quality)
├─> flutter test (unit tests)
└─> flutter build appbundle --debug (build verification)
```

### Pre-Production Testing
```
Internal Testing Track (Play Console):
├─> Upload .aab to internal testing
├─> Invite testers via email
└─> Gather feedback before production
```

## Rollback Strategy

If an update causes issues:

```
Option 1: Emergency Rollback (Play Console)
└─> Production → Releases → Halt rollout
    └─> Rollback to previous version

Option 2: Hotfix Release
├─> Fix the issue
├─> Increment version (e.g., 1.0.2+3)
├─> Build and upload
└─> Submit as emergency update

Option 3: Staged Rollout
├─> Start with 5% of users
├─> Monitor for issues
├─> Gradually increase to 100%
└─> Halt and fix if problems detected
```

## Summary

This deployment architecture provides:

✅ **Security**: Multi-layered protection for signing keys
✅ **Automation**: CI/CD pipeline for continuous building
✅ **Documentation**: Comprehensive guides at every level
✅ **Flexibility**: Works locally and in CI/CD
✅ **Safety**: Fallback mechanisms and rollback options
✅ **Scalability**: Structured for team collaboration

All components are production-ready and follow Android and Flutter best practices.
