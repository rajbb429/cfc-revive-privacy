# Ribwork for Android

This is a Trusted Web Activity (TWA): a thin Android app that opens the Ribwork web
app full screen in Chrome, with no address bar. It is the Google-supported way to
ship a web app on Google Play, and the only way for a web app to take payments
through Google Play Billing, which the full-app unlock uses.

It was generated with Google's Bubblewrap (`@bubblewrap/core` 1.25.0). The settings
live in `twa-manifest.json`, so you can regenerate later with `bubblewrap update`.

| | |
|---|---|
| Package name | `io.github.rajbb429.ribwork` (permanent once published) |
| App name | Breathwork: Ribcage & Midline (launcher: Ribwork) |
| Opens | `https://rajbb429.github.io/cfc-revive-privacy/breathe/` |
| Targets | Android 16 (API 36), runs on Android 6.0 (API 23) and up (the Play Billing library needs 23) |
| In-app product | `ribwork_full` (one-time) |

## Build

GitHub Actions builds the app on every push that touches `android/`
(`.github/workflows/android.yml`). Open the run under the **Actions** tab and
download:

- **ribwork-debug-apk**: install it on a phone to try the app. It is signed with a
  throwaway debug key, so it shows a browser address bar and purchases don't work.
- **ribwork-play-bundle**: the signed `.aab` to upload to Google Play. Built only
  once the signing secrets below exist.

The web app has to be live first: GitHub Pages deploys from `main`, so merge the
`breathe/` changes before testing on a phone.

## One-time setup

### 1. Create your upload key

On your own computer (keep the file and passwords safe; losing them means you can
no longer update the app without asking Google to reset the key):

    keytool -genkeypair -v -keystore ribwork-upload.keystore -alias ribwork \
      -keyalg RSA -keysize 2048 -validity 10000

### 2. Add the GitHub secrets

In the repository: **Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Value |
|---|---|
| `RIBWORK_KEYSTORE_BASE64` | output of `base64 -w0 ribwork-upload.keystore` (macOS: `base64 -i ribwork-upload.keystore`) |
| `RIBWORK_KEYSTORE_PASSWORD` | the keystore password |
| `RIBWORK_KEY_ALIAS` | `ribwork` |
| `RIBWORK_KEY_PASSWORD` | the key password (if different from the keystore password) |

Then re-run the workflow (**Actions → Build Android app → Run workflow**).

### 3. Verify the domain (removes the address bar, enables purchases)

Android checks `https://rajbb429.github.io/.well-known/assetlinks.json`. That path
is at the **root** of your GitHub Pages domain, which this repository can't serve
(it lives under `/cfc-revive-privacy/`). Create a repository named exactly
`rajbb429.github.io`, turn on Pages for it, and add `.well-known/assetlinks.json`:

    [{
      "relation": ["delegate_permission/common.handle_all_urls"],
      "target": {
        "namespace": "android_app",
        "package_name": "io.github.rajbb429.ribwork",
        "sha256_cert_fingerprints": [
          "PLAY_APP_SIGNING_KEY_SHA256",
          "UPLOAD_KEY_SHA256"
        ]
      }
    }]

Also add an empty `.nojekyll` file so GitHub Pages serves the `.well-known` folder.

Get the fingerprints from:

- **Play App Signing key**: Play Console → your app → **Test and release → App
  integrity → App signing**, "SHA-256 certificate fingerprint". This is the one that
  matters for installs from Play.
- **Upload key**: `keytool -list -v -keystore ribwork-upload.keystore -alias ribwork`,
  the `SHA256:` line. Lets builds you sideload verify too.

A custom domain works as well: point it at the Pages site and serve
`/.well-known/assetlinks.json` from its root instead, then change `host` in
`twa-manifest.json` and `hostName` in `app/build.gradle`.

### 4. Publish on Google Play

1. Play Console → **Create app**, name "Breathwork: Ribcage & Midline".
2. Upload the `.aab` from step 2 to an internal testing track first.
3. **Monetize → Products → In-app products**: create `ribwork_full` as a
   one-time product and set its price. The app shows Play's price.
4. Fill in the listing from `breathe/store-listing.md`, and set the privacy policy
   URL to `https://rajbb429.github.io/cfc-revive-privacy/breathe/privacy.html`.
5. Promo codes: **Monetize → Promotions → Promo codes → Create promotion**, one-time
   use codes for `ribwork_full`. Users redeem them from "Have a promo code?" on the
   unlock screen (or in the Play Store app).

## Purchase acknowledgement (no server needed)

Google Play refunds and revokes any purchase that isn't acknowledged within 3 days,
including redeemed promo codes. The app acknowledges on the device:
`PurchaseAcknowledger.java` sits in front of the Digital Goods handler in
`DelegationService` and, whenever the web app asks Play about purchases (at launch,
when it comes back into view, right after a purchase or code redemption), it
acknowledges anything still unacknowledged using the Play Billing Library.
`LauncherActivity` also runs it once at each launch.

A server is optional. Google recommends verifying purchase tokens on a server to
catch fraudulent purchases; if you add one, point `BILLING.verifyUrl` in
`breathe/index.html` at it.
