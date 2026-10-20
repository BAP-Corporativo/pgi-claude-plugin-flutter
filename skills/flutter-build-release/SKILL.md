---
name: flutter-build-release
description: Build release artifacts (Android APK and/or iOS IPA) for a flavor-based Flutter project, picking the right entrypoint and flavor for the requested environment, and auto-incrementing the iOS build number on each new IPA unless a specific version or build is given. Use this whenever the user asks to generate, build, compile, or release an apk or ipa, mentions "generar una versión", "build release", "compilar", "saca una qa/prod", or names a flavor/environment (dev, qa, prod) to build. Trigger even if the user only says "genera el apk" or "necesito un ipa de qa" without more detail.
---

# Flutter build release (APK / IPA)

Build release artifacts for a flavor-based Flutter project. Handles: which artifact(s) to build, which flavor/environment, and the iOS build-number increment.

## Project conventions this relies on

These projects use one entrypoint per flavor and a matching build flavor id:

- Entrypoint file: `lib/main_<project>_<flavor>.dart` (e.g. `lib/main_united_qa.dart`)
- Build flavor id: `<project><Flavor>` in camelCase (e.g. `unitedQa`, `unitedProd`, `unitedDev`)
- Flavors are the environments: `dev`, `qa`, `prod`

**Discover the project prefix and available flavors instead of hardcoding** — glob the entrypoints:

```bash
ls lib/main_*_*.dart
```

Each match `lib/main_<project>_<flavor>.dart` gives the project prefix and a valid flavor. Map the flavor to its camelCase id: `<project>` + `<Flavor capitalized>` (e.g. `united` + `Qa` = `unitedQa`).

Respect the SDK pin: these repos pin a Flutter version via `.fvmrc`. Use plain `flutter ...` (per the project's CLAUDE.md); if the user's global SDK differs, prefix with `fvm flutter ...`. If a `CLAUDE.md` exists, follow its command conventions.

## Inputs to resolve (ask only if missing)

1. **Artifact(s):** `apk`, `ipa`, or both. If the user didn't specify, build **both**.
2. **Flavor / environment:** `dev`, `qa`, or `prod`. Required — if not given, ASK (do not guess prod).
3. **Version (IPA only):** if the user names a version and/or build number, use exactly that. Otherwise auto-increment the build number by 1 (see below). APK does not drive an increment.

Do not ask about anything already stated in the request.

## Build commands

```bash
# APK
flutter build apk -t lib/main_<project>_<flavor>.dart --flavor <project><Flavor> \
  [--build-name=<X.Y.Z> --build-number=<N>]

# IPA
flutter build ipa -t lib/main_<project>_<flavor>.dart --flavor <project><Flavor> \
  --build-name=<X.Y.Z> --build-number=<N>
```

Always pass `--build-name` / `--build-number` explicitly on the IPA so the artifact carries the intended version regardless of what is currently written in `pubspec.yaml`. When building both artifacts in one request, use the **same** version for both.

## iOS build-number handling

The build number is the `+B` in `pubspec.yaml`'s `version: X.Y.Z+B`, which Flutter uses for iOS `CFBundleVersion`. The script `scripts/bump_build_number.py` reads/computes/writes it. Persist the increment **only after a successful build**, so a failed build never burns a number.

### Case A — user did NOT specify a version/build (auto-increment)

1. Compute the next build number without writing:
   ```bash
   python3 <skill-dir>/scripts/bump_build_number.py --bump
   ```
   Read `BUILD_NAME` and `BUILD_NUMBER` from the output.
2. Run the IPA build (and APK if requested) with `--build-name=$BUILD_NAME --build-number=$BUILD_NUMBER`.
3. If the build succeeded, persist it:
   ```bash
   python3 <skill-dir>/scripts/bump_build_number.py \
     --set-version $BUILD_NAME --set-build $BUILD_NUMBER --write
   ```
4. Tell the user the version that was built and that `pubspec.yaml` was bumped to it.

### Case B — user specified a version and/or build

Use exactly what they gave (keep the current version name if they only gave a build, and vice versa). Compute and write in one step, then build:

```bash
python3 <skill-dir>/scripts/bump_build_number.py \
  [--set-version <X.Y.Z>] [--set-build <N>] --write
```

Then build with the resulting `--build-name` / `--build-number`.

> If only an APK is requested, skip the increment entirely — build the APK as-is (optionally passing the current version). The increment is an IPA behavior.

## Where artifacts land (report these paths)

- APK: `build/app/outputs/flutter-apk/app-<flavor>-release.apk`
- IPA: `build/ios/ipa/*.ipa`

After building, tell the user the artifact path(s) and the exact version/build used. If a build fails, surface the error and note that the build number was **not** persisted (so re-running will retry the same number).

## Example runs

**"genera el ipa de qa"** → both version/build unspecified, IPA only:
1. `bump_build_number.py --bump` → say `1.4.2+38`.
2. `flutter build ipa -t lib/main_united_qa.dart --flavor unitedQa --build-name=1.4.2 --build-number=38`
3. On success: `bump_build_number.py --set-version 1.4.2 --set-build 38 --write`.

**"saca apk e ipa de prod, versión 2.0.0 build 5"** → both artifacts, explicit version:
1. `bump_build_number.py --set-version 2.0.0 --set-build 5 --write`
2. `flutter build apk -t lib/main_united_prod.dart --flavor unitedProd --build-name=2.0.0 --build-number=5`
3. `flutter build ipa -t lib/main_united_prod.dart --flavor unitedProd --build-name=2.0.0 --build-number=5`

**"solo el apk de dev"** → APK only, no increment:
1. `flutter build apk -t lib/main_united_dev.dart --flavor unitedDev`
