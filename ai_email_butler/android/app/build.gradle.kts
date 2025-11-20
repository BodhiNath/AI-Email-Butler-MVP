import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// Load keystore properties from key.properties (do not commit this file)
val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    FileInputStream(keystorePropertiesFile).use { fis ->
        keystoreProperties.load(fis)
    }
}

android {
    namespace = "com.example.ai_email_butler"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        // Application ID: com.theambassador.emailbutler
        applicationId = "com.theambassador.emailbutler"
        
        // Minimum Android version (most devices support this)
        minSdk = flutter.minSdkVersion
        
        // Target the latest Android version
        targetSdk = flutter.targetSdkVersion
        
        // Version code (increment by 1 for each release)
        versionCode = flutter.versionCode
        
        // Version name (shown to users)
        versionName = flutter.versionName
    }

    signingConfigs {
        create("release") {
            // Expect these keys in android/key.properties (resolved as rootProject/key.properties)
            val alias = keystoreProperties.getProperty("keyAlias")
            val keyPass = keystoreProperties.getProperty("keyPassword")
            val storePath = keystoreProperties.getProperty("storeFile")
            val storePass = keystoreProperties.getProperty("storePassword")

            if (!storePath.isNullOrBlank()) {
                storeFile = file(storePath)
            }
            keyAlias = alias
            keyPassword = keyPass
            storePassword = storePass
        }
    }

    buildTypes {
        release {
            // Use release signing config
            signingConfig = signingConfigs.getByName("release")
            // Enable minification for smaller APK
            minifyEnabled = true
            shrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

flutter {
    source = "../.."
}
