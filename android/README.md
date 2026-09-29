# Ribwork for Android

A Capacitor app: the web app in `../breathe/` is packed inside the app and runs in
Android's built-in web view, so it works offline and doesn't depend on the website.
Purchases go through Google Play Billing with the
[`@capgo/native-purchases`](https://github.com/Cap-go/capacitor-native-purchases) plugin.

| | |
|---|---|
| Package name | `io.github.rajbb429.ribwork` (permanent) |
| App name | Breathwork: Ribcage & Midline (launcher: Ribwork) |
| Version | 2.0.0 (versionCode 2) in `app/build.gradle` |
| Targets | Android 16 (API 36), runs on Android 7.0 (API 24) and up |
| In-app product | `ribwork_full` (one-time) |

Version 1 was a Trusted Web Activity that opened the website in Chrome. This version
replaces it; it's an ordinary update on Google Play.

## Build

Everything starts from the repository root, not this folder:

    npm ci          # once, and after package.json changes
    npm run sync    # copies breathe/ into the app; run after every web change

`npm run sync` builds `www/` from `breathe/` (plus `native.js`, the Capacitor runtime
and plugins) and copies it into `android/app/src/main/assets/public`.

### With GitHub Actions

Every push that touches the app runs `.github/workflows/android.yml`. Open the run
under the **Actions** tab and download:

- **ribwork-debug-apk**: install it on a phone to try the app. Purchases only work in
  a copy installed from Google Play (any testing track).
- **ribwork-play-bundle**: the signed `.aab` for Google Play, built when these
  repository secrets exist (**Settings → Secrets and variables → Actions**):

| Secret | Value |
|---|---|
| `RIBWORK_KEYSTORE_BASE64` | output of `base64 -w0 your-upload.jks` (macOS: `base64 -i your-upload.jks`) |
| `RIBWORK_KEYSTORE_PASSWORD` | the keystore password |
| `RIBWORK_KEY_ALIAS` | the key alias |
| `RIBWORK_KEY_PASSWORD` | the key password (if different from the keystore password) |

### With Android Studio

1. Install Node.js 22 and run the two commands above from the repository root.
2. In Android Studio, **Open** the `android` folder.
3. **Build → Generate Signed App Bundle or APK → Android App Bundle**, and choose the
   **same upload key** you used for version 1. Google Play rejects a bundle signed
   with any other key.
4. The bundle lands in `android/app/release/`.

## Releasing an update

1. Raise `versionCode` (and `versionName`) in `app/build.gradle`. Play refuses a
   versionCode it has seen before.
2. Build the signed bundle and upload it in Play Console to a testing track, then
   promote it to production.

Changes to `breathe/` reach Android users only through a new release like this.
They go live on the website as soon as they're merged to `main`.

## Purchases

- **Acknowledgement:** Google Play refunds a purchase that isn't acknowledged within
  3 days, including redeemed promo codes. The plugin acknowledges each purchase as
  it completes, and the web app's `Pro.restore` acknowledges any it still finds at
  launch and every time the app comes back to the foreground.
- **Promo codes:** **Monetize → Promotions → Promo codes** in Play Console, as
  one-time codes for `ribwork_full`. Users redeem them from "Have a promo code?" on
  the unlock screen, which opens Google Play; the app unlocks when they come back.
- **Testing:** add testers under **Settings → License testing** so their purchases
  aren't charged, and install from a testing track's opt-in link.
