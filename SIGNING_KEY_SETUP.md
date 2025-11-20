# Instructions for Creating Release Signing Key

## Step 1: Generate Release Key (One-Time Setup)

Run this command in PowerShell:

```powershell
cd "e:\email butler\Full Build Functional Deployment Development\ai_email_butler_project\ai_email_butler\android\app"

# Generate release key (valid for 10,000 days = ~27 years)
keytool -genkey -v -keystore release-key.jks `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000 `
  -alias release-key
```

**You'll be prompted to enter:**
```
Enter keystore password: [create strong password - min 6 chars]
Re-enter new password: [confirm password]
First and last name: [Your Name or Company Name]
Organizational unit: [e.g., Development]
Organization: [Your Company]
City or Locality: [Your City]
State or Province: [Your State]
Country Code: [US, UK, etc. - 2 letter code]
```

**This creates:** `release-key.jks` file (KEEP SAFE - needed for all future updates!)

## Step 2: Create key.properties File

Create file: `android/key.properties`

```properties
storePassword=YOUR_KEYSTORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=release-key
storeFile=release-key.jks
```

**IMPORTANT:** 
- Replace `YOUR_KEYSTORE_PASSWORD` with the password you entered
- Add `key.properties` to `.gitignore` (NEVER commit this!)

## Step 3: Update build.gradle.kts

The file at: `android/app/build.gradle.kts`

Update the signing configuration section to:

```kotlin
signingConfigs {
    release {
        keyAlias = project.findProperty("key.alias") as String?
        keyPassword = project.findProperty("key.password") as String?
        storeFile = file(project.findProperty("store.file") ?: "dummy")
        storePassword = project.findProperty("store.password") as String?
    }
}

buildTypes {
    release {
        signingConfig = signingConfigs.getByName("release")
    }
}
```

Add to `android/build.gradle.kts`:

```kotlin
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```

## Step 4: Build Release APK/AAB

```bash
cd ai_email_butler
flutter build appbundle --release
```

Output will be at:
`build/app/outputs/bundle/release/app-release.aab`

## Step 5: Upload to Google Play Console

1. Go to https://play.google.com/console
2. Select your app
3. Go to "Release" → "Production"
4. Click "Create new release"
5. Upload the `.aab` file
6. Fill in release notes
7. Review and submit

---

## ⚠️ IMPORTANT SECURITY NOTES:

1. **Backup release-key.jks** - If you lose this, you can NEVER update your app
2. **Keep key.properties secure** - This file is passwordless access
3. **Add to .gitignore:**
   ```
   key.properties
   release-key.jks
   ```
4. **Store passwords securely** - Use a password manager

---

## Troubleshooting:

### "keytool: command not found"
- Java is not installed or not in PATH
- Install Java from: https://www.oracle.com/java/technologies/downloads/
- Verify: `java -version`

### "Invalid keystore format"
- Key file is corrupted
- Delete and recreate: `del release-key.jks`

### "Build failed - keystore password incorrect"
- Check password in key.properties matches
- Recreate if forgotten (will need new app ID)

