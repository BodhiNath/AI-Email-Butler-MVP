# Pre-Submission Checklist - Google Play Console

## ✅ Before Uploading to Google Play

### Step 1: Update Application ID
- [ ] Change from `com.example.ai_email_butler` to your unique ID
- [ ] Example: `com.yourdomain.aiemailbutler` or `com.yourcompany.emailbutler`

### Step 2: Create Signing Key
```bash
cd android/app
keytool -genkey -v -keystore release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias release-key
```

### Step 3: Configure Signing
- [ ] Create `key.properties` file with key details
- [ ] Update `build.gradle.kts` with signing config
- [ ] Add `key.properties` to `.gitignore`

### Step 4: Update App Metadata
- [ ] App name (max 50 chars)
- [ ] App description (max 80 chars for short, 4000 for full)
- [ ] Privacy policy URL
- [ ] Support email

### Step 5: Prepare Assets
- [ ] App icon (512x512 PNG)
- [ ] Feature graphic (1024x500 PNG)
- [ ] Screenshots (at least 2, up to 8)
- [ ] Promotional banner (optional, 180x120 PNG)

### Step 6: Content Rating
- [ ] Complete content questionnaire
- [ ] Get rating certificate

### Step 7: Pricing & Distribution
- [ ] Select countries
- [ ] Choose free/paid
- [ ] Set content rating

### Step 8: Build Release APK/AAB
```bash
flutter build appbundle --release
```

### Step 9: Test Before Submission
- [ ] Run on multiple devices
- [ ] Test all features
- [ ] Check error handling
- [ ] Verify backend connectivity

### Step 10: Submit for Review
- [ ] Upload to Google Play Console
- [ ] Review takes 24-48 hours
- [ ] Monitor for rejection reasons

---

## 🔴 Current Issues in Your Project:

1. **applicationId = "com.example.ai_email_butler"** ← MUST CHANGE
2. **signingConfig = signingConfigs.getByName("debug")** ← MUST CREATE RELEASE KEY
3. **No privacy policy URL** ← REQUIRED
4. **No app icon** ← REQUIRED

---

## Cost:
- Google Play Developer Account: $25 (one-time, you may already have this)
- Each app: Free to list and distribute

