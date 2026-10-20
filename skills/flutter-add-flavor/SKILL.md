---
name: flutter-add-flavor
description: Add a new build flavor / environment (e.g. staging, uat, demo) to a Nextline PGI Flutter project (UNITED, FinsofApp and their variants) — FlavorConfig enum, env prefix mapping, .env base URL, main_<project>_<flavor>.dart entrypoint, Android productFlavors, iOS schemes and build configurations, Firebase project and per-flavor theme. Use this whenever the user asks to add, create, or configure a new flavor, ambiente, entorno, environment, variante, or "un nuevo sabor", or asks why a new flavor fails to build on iOS or Android.
---

# Flutter add flavor

A flavor touches Dart, Android, iOS and Firebase. Missing any one of them produces a build that compiles on one platform and fails on the other, so go through every section and report each one.

Naming convention (shared with `flutter-build-release`, which discovers flavors by globbing entrypoints):
- Entrypoint: `lib/main_<project>_<flavor>.dart` → `lib/main_united_staging.dart`
- Flavor id: `<project><Flavor>` → `unitedStaging`
- Env prefix: `<KEY>_<PROJECT>_<FLAVOR>` → `BASE_URL_UNITED_STAGING`

## Step 0 — Resolve and pick a template flavor

```bash
ls lib/main_*_*.dart                              # project prefix + existing flavors
grep -rn "enum" lib/flavors/flavor_init.dart      # flavor enum
cat lib/flavors/config/flavor_config.dart         # env prefix mapping
ls android/app/build.gradle* ; ls ios/Flutter/*.xcconfig
ls ios/Runner.xcodeproj/xcshareddata/xcschemes/
```

Use the **closest existing flavor** as the template (usually `qa` for a pre-prod environment). Every step below is "copy the template's block and change only the flavor name and its values".

Ask the user for anything you can't infer: the API base URL, Android applicationId / iOS bundle id for the new flavor, app display name, and which Firebase project to use. Never point a non-prod flavor at the prod Firebase project or prod URL by default.

## 1. Dart

### Flavor enum — `lib/flavors/flavor_init.dart`

Add the value to the `Flavor` enum, keeping the `<project><Flavor>` naming. `FlavorConfig` itself needs no change: it is a singleton that receives the flavor and a display name.

```dart
enum Flavor {
  unitedDev,
  unitedQa,
  unitedStaging,
  unitedProd,
}

class FlavorConfig {
  static FlavorConfig? _instance;
  final Flavor flavor;
  final String name;

  static FlavorConfig get instance => _instance!;

  FlavorConfig._({
    required this.flavor,
    required this.name,
  });

  factory FlavorConfig({
    required Flavor flavor,
    required String name,
  }) {
    return _instance ??= FlavorConfig._(
      flavor: flavor,
      name: name,
    );
  }
}
```

Then search for every `switch` / `case` on `Flavor` and add the new value — a non-exhaustive switch is a compile error in Dart 3, which is useful: `flutter analyze` lists each place to update.

```bash
grep -rn "Flavor\.unitedQa" lib/
```

### Flavor values — `lib/flavors/config/flavor_config.dart`

`FlavorConfigure.configure()` reads three values per flavor from `_getFlavorConfig()`:

| Key | Used for |
|---|---|
| `envPrefix` | Builds the `.env` key `BASE_URL_<envPrefix>` → `AppConfig.apiUrl` |
| `pathName` | `AppImages.pathName` — the flavor's image asset folder |
| `appName` | `AppConfig.appName` and `AppConstants.appFlavorName` |

Add a case to the switch, copying the template flavor's map and changing only `envPrefix` (and `pathName` / `appName` if the user says this flavor has its own assets or branding):

```dart
static Map<String, String> _getFlavorConfig() {
  switch (FlavorConfig.instance.flavor) {
    case Flavor.unitedDev:
      return {
        'envPrefix': 'UNITED_DEV',
        'pathName': 'united',
        'appName': 'UNITED',
      };
    case Flavor.unitedQa:
      return {
        'envPrefix': 'UNITED_QA',
        'pathName': 'united',
        'appName': 'UNITED',
      };
    case Flavor.unitedStaging:
      return {
        'envPrefix': 'UNITED_STAGING',
        'pathName': 'united',
        'appName': 'UNITED',
      };
    case Flavor.unitedProd:
      return {
        'envPrefix': 'UNITED_PROD',
        'pathName': 'united',
        'appName': 'UNITED',
      };
  }
}
```

The switch has no `default`, so after adding the enum value `flutter analyze` reports it as non-exhaustive until this case exists. Never add a `default` to silence it.

If `pathName` changes, the asset folder for that name must exist with the same file names as the template's folder (check `AppImages` and the `assets:` section of `pubspec.yaml`).

### Entrypoint — `lib/main_united_staging.dart`

Copy the template flavor's entrypoint and change only the enum value and the display name. **Keep the argument passed to `mainCommon` exactly as the template has it** unless the user says this flavor needs a different value.

```dart
import 'package:united/flavors/main_common.dart';

import 'flavors/flavor_init.dart';

void main() {
  FlavorConfig(
    flavor: Flavor.unitedStaging,
    name: 'UNITED Staging',
  );
  mainCommon(2000);
}
```

`name` is the flavor's display name inside the app; the launcher name on the device is set per platform (Android `resValue`, iOS display name) in the next sections.

### `.env`

Add every key the template flavor has, with this flavor's values:

```
BASE_URL_UNITED_STAGING=https://staging-api.example.com
```

### Theme

If `lib/flavors/theme/theme_flavors.dart` switches on the flavor, add a case (reusing the template's colors is fine unless the user says otherwise).

## 2. Android

Groovy (`android/app/build.gradle`):
```groovy
productFlavors {
    unitedStaging {
        dimension "app"                       // mirror
        applicationId "com.nextline.united.staging"
        resValue "string", "app_name", "UNITED Staging"
    }
}
```

Kotlin DSL (`build.gradle.kts`):
```kotlin
create("unitedStaging") {
    dimension = "app"
    applicationId = "com.nextline.united.staging"
    resValue("string", "app_name", "UNITED Staging")
}
```

Firebase: place this flavor's `google-services.json` at `android/app/src/unitedStaging/google-services.json` (mirror where the template flavor keeps its file).

## 3. iOS

Flutter maps `--flavor unitedStaging` to the Xcode **scheme** `unitedStaging` and to build configurations named `Debug-unitedStaging`, `Release-unitedStaging`, `Profile-unitedStaging`. All four must exist with those exact names.

1. In Xcode → Runner project → Info → Configurations: duplicate the template's three configurations and rename them with the new flavor suffix.
2. Create `ios/Flutter/` xcconfig files for them if the template has per-flavor xcconfigs (copy and rename).
3. Product → Scheme → Manage Schemes: duplicate the template scheme, rename to `unitedStaging`, mark **Shared**, and point each action (Run/Test/Profile/Analyze/Archive) to the matching new configuration.
4. Set `PRODUCT_BUNDLE_IDENTIFIER` and display name for the new configurations.
5. Firebase: add this flavor's `GoogleService-Info.plist` the same way the template does (per-config copy script or per-flavor folder).

## 4. Firebase options

If the project uses `lib/firebase_options.dart` per flavor (FlutterFire CLI), run `flutterfire configure` for the new Firebase project with the new bundle/application ids and wire it in `lib/flavors/config/firebase_config.dart` the way the template flavor is wired.

## 5. Verify

```bash
flutter run -t lib/main_united_staging.dart --flavor unitedStaging   # Android device
flutter run -t lib/main_united_staging.dart --flavor unitedStaging   # iOS simulator
flutter analyze
```

Then update the repo's `CLAUDE.md` variables table (flavors / entrypoints).

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Change the `mainCommon(...)` argument while copying the entrypoint | Keep the template's value | It is shared bootstrap configuration; changing it silently alters app behavior for that flavor |
| Create only the Dart entrypoint | Dart + Android + iOS + Firebase + `.env` | The build fails on whichever platform was skipped |
| iOS scheme named `staging` or `UnitedStaging` | Exactly `unitedStaging`, configs `Release-unitedStaging` etc. | Flutter looks up the names literally |
| Scheme not marked Shared | Mark it Shared | Unshared schemes live in xcuserdata and disappear on other machines / CI |
| Reuse the prod `google-services.json` / `GoogleService-Info.plist` | Separate Firebase app (or the one the user specifies) | Push tokens and analytics would mix with production |
| Same applicationId / bundle id as another flavor | Unique id per flavor | Installing one flavor overwrites the other on the device |
| Hardcode the base URL in Dart | `.env` key `BASE_URL_<envPrefix>` | Every flavor resolves its URL the same way |
| `.env` key missing or misspelled (`BASE_URL_UNITED_STG` vs `envPrefix: 'UNITED_STAGING'`) | Key name = `BASE_URL_` + the exact `envPrefix` | `configure()` falls back to `''` — the app starts but every request fails, with no error at startup |
| Add `default:` to the `_getFlavorConfig()` switch | One explicit `case` per flavor | `default` hides a missing flavor and silently gives it another flavor's URL |
| New `pathName` without its asset folder | Reuse the template's `pathName` or create the folder with the same files | Images fail to load only at runtime |

## Finish

Report a checklist with each area (Dart, `.env`, Android, iOS configs, iOS scheme, Firebase, CLAUDE.md) marked done or pending, and list anything that must be done manually in Xcode or the Firebase console.
