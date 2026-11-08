# Google Play store listing

Paste-ready text and images are in `play-store/` at the repository root.

Google Play search weighs the **title** most, then the **short description**, then the
**full description**. Use the phrases people actually type ("breathwork",
"breathing exercises", "breath training", "ribcage", "midline", "deep breathing") naturally,
and don't list keywords or use words like "best" or "#1": Play's metadata policy rejects both.

## App name (max 30 characters)

    Stress to Strong: Breathe

25 characters. The brand comes first so it stands apart from the many apps called
"Breathe", and it uses plain words that Play won't spell-correct. "Stress" and "Breathe"
are both words people search for. The home-screen label is shorter, `Stress→Strong`
(`app_name` in `android/app/src/main/res/values/strings.xml`), so launchers don't cut it off.
Formerly "4-7-8 & Box Breathing: Ribwork"; the package ID and in-app product ID are unchanged.

## Short description (max 80 characters)

    Calm your breath, then build it: 4-7-8, long exhales, breath holds and ribs

75 characters. Says what the name means and covers the main search terms.

## Full description (max 4000 characters)

In `play-store/full-description.txt`. It names 4-7-6-6 also as "4766", the way people type it.

## Also set in Play Console

- **Category:** Health & Fitness
- **Tags:** pick the closest to breathing, meditation, relaxation and sleep
- **Privacy policy URL:** `https://rajbb429.github.io/cfc-revive-privacy/breathe/privacy.html`
- **In-app product:** one-time product with ID `ribwork_full`. The ID can't be changed
  after you create it; it must match `BILLING.sku` in `index.html`.
