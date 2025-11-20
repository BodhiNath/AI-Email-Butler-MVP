# ProGuard rules for Flutter app minification and optimization

# Preserve Flutter engine and main entry points
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }
-keep class io.flutter.embedding.** { *; }

# Preserve Dart/Flutter runtime
-dontwarn java.lang.invoke.**
-dontwarn sun.misc.Unsafe
-dontwarn com.google.dart.runner.**

# Keep HTTP client libraries
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }
-dontwarn okhttp3.**

# Keep OpenAI client
-keep class com.openai.** { *; }
-keep class okio.** { *; }

# Keep Dart reflection
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep enums
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Keep custom classes
-keep class com.** { *; }

# Remove logging from production builds
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}
