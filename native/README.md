# SherpaWare iPad app (Capacitor wrapper)

Wraps the same single-file web app in a native iPad shell so location keeps running while ForeFlight is on screen, and so questions (block out, block in, still scheduled) arrive as notification banners with Yes / No buttons.

## What is here
- `package.json`, `capacitor.config.json`: project definition. Plugins: background geolocation (community plugin), local notifications. Versions are "latest" and were NOT checked against the registry from the build sandbox (blocked); pin them after the first working build.
- `scripts/prepare_web.py`: copies the PUBLIC build (no trip data) into `www/`.
- `scripts/patch_ios.py`: after `cap add ios`, adds the location permission texts, the "location" background mode, and iPad-only.
- `.github/workflows/ios-build.yml` (repo root): compile check on a GitHub macOS runner, no Apple account needed.
- Web side: `src/native.js` (bridge) and the changes in `src/flightlog_ui.js`. In a normal browser the bridge does nothing. Tests: `node tests/native.test.js`, `python3 -I tests/native_ui.test.py dist/SherpaWare.html`.

## Status (16 Oct 16:10)
- The app compiles. The GitHub macOS workflow (`ios-build`, repo Sherpaware/SherpaWare, Actions tab) installs Capacitor with the plugins, adds the iOS project, applies the location/background/iPad-only settings and builds for the iPad simulator. Passed twice, the second time with a strict check that fails on any Xcode error (run 38957527257).
- The native project lives in the `native/` folder at the top of the existing GitHub repo (which publishes the web page). The workflow uses the published public page as the app's web content, so the repo holds no trip data. `native/` is also served on the website (harmless).
- The sandbox cannot reach the npm registry (policy denial, not worked around). GitHub's machines do the install.
- NOT done: running on an iPad, signing, TestFlight. The bridge was tested only against mock plugins.

## Steps (in order)
1. Compile check: DONE (above). Re-run from the Actions tab after any change to native/.
2. Apple Developer Program (individual): enroll at developer.apple.com (paid annual fee, verify current price). Pilot or Matt.
3. Signed build: on a Mac (or Xcode Cloud / a signing step in the workflow with certificates stored as secrets), set the team, bundle id `com.sherpaware.n282bt`, archive, upload to App Store Connect.
4. TestFlight: invite crew by email. Builds expire after 90 days, so plan a re-upload.
5. On each iPad: install, open once, allow Location "Always" (Settings > SherpaWare > Location), allow Notifications. Keep the app open at least once per flying day (do not swipe it away in the app switcher during a flight).
6. Real test flight with ForeFlight full screen. Record the track and tune thresholds in `src/flighttimes.js` (background updates arrive less often than in a browser).

## Known limits to confirm on a device
- Background JavaScript: the plugin should keep the app running while it receives location; confirm the tracker keeps running and saves state.
- Notification action buttons answer without opening the app; confirm the answer reaches the tracker while backgrounded.
- Location indicator and battery use. Force-quit stops tracking.
- iOS app does not use the service worker or the hosted weather; use the relay (SW_RELAY) for weather and NOTAMs.

## TestFlight setup (written 16 Oct 16:50, pilot registered an individual Apple Developer account that day; approval pending)
Workflow `ios-testflight` (repo root .github/workflows, source copy native/ios-testflight.yml) archives with automatic signing through an App Store Connect API key and uploads to TestFlight. UNTESTED until the secrets exist. The compile check (`ios-build`) passed with the app icon and encryption flag added (run after commit 13bd57b).
Pilot steps after approval: (1) Team ID from developer.apple.com Membership; (2) App Store Connect API key (start with App Manager, raise to Admin if certificate creation fails): note Issuer ID and Key ID, download the .p8 once; (3) create the app record with bundle id com.sherpaware.n282bt (name may need a suffix if taken); (4) add GitHub secrets APPLE_TEAM_ID, ASC_ISSUER_ID, ASC_KEY_ID, ASC_KEY_P8 (never paste these into chat); (5) invite Matt and others as App Store Connect users (internal TestFlight testers skip beta review); (6) run the workflow from the Actions tab; (7) install through the TestFlight app on each iPad mini. TestFlight builds expire after 90 days; the build number is the GitHub run number.
