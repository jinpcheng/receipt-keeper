# Android scaffold

This is an Android app (Kotlin + XML views) for capturing receipts and talking to the backend API over WiFi.

Open `android/` in Android Studio to import the project.

Build (command line):

- Ensure the Android SDK is installed (Android Studio is easiest).
- Point Gradle at the SDK using either:
  - `android/local.properties` (recommended, ignored by git): `sdk.dir=C:\\path\\to\\Android\\Sdk`
  - or set `ANDROID_SDK_ROOT` / `ANDROID_HOME`

Then:

```powershell
cd android
.\gradlew.bat :app:assembleDebug
```

APK output:
`android/app/build/outputs/apk/debug/app-debug.apk`

API base URL:
- Set it at runtime via the Settings button on the main screen.
- Examples:
  - Phone (HTTP): `http://<PC-LAN-IP>:8081/api/v1/`
  - Phone (HTTPS via Caddy): `https://<PC-LAN-IP>:8443/api/v1/`

Notes:
- Debug builds allow cleartext HTTP and trust user-installed CAs (required for local HTTPS-on-LAN testing).
