---
name: flutter-build-release
description: Build release artifacts (Android APK and/or iOS IPA) for a flavor-based Flutter project, picking the right entrypoint and flavor for the requested environment, auto-incrementing the iOS build number on each new IPA unless a specific version or build is given, and optionally uploading each artifact to its Google Drive folder via rclone. Use this whenever the user asks to generate, build, compile, release, or upload an apk or ipa, mentions "generar una versión", "build release", "compilar", "saca una qa/prod", "súbelo a Drive", or names a flavor/environment (dev, qa, prod) to build. Trigger even if the user only says "genera el apk" or "necesito un ipa de qa" without more detail.
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
4. **Upload to Drive:** by default, after a successful build, upload each artifact to its Drive folder (see "Upload to Drive"). Skip only if the user says not to (e.g. "solo compila", "sin subir").

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

## Upload to Drive

After a successful build, upload each artifact to Google Drive with `scripts/upload_to_drive.py`, which uses `rclone` under the hood and builds the correct destination path.

### Drive folder layout

```
<base>/<PROJECT>/<Env>/<system-folder>
```
- `<base>`: `Apps` (default; override with `--base`)
- `<PROJECT>`: the Drive project folder name, e.g. `UNITED`. Defaults to the code prefix uppercased (`united` → `UNITED`); override with `--drive-project` if the Drive folder is named differently.
- `<Env>`: `Dev` / `QA` / `Prod` (mapped from flavor `dev`/`qa`/`prod`).
- `<system-folder>`:
  - **Dev and QA:** `Android` / `iOS`
  - **Prod:** `<PROJECT> Android` / `<PROJECT> iOS` (prefixed with the project name)

Examples: `gdrive:Apps/UNITED/QA/iOS/`, `gdrive:Apps/UNITED/Prod/UNITED Android/`.

### One-time setup (tell the user if rclone/remote is missing)

The upload needs `rclone` installed and a remote configured against their Drive account:
```bash
# install (macOS): brew install rclone   |   (linux): sudo apt install rclone
rclone config          # create a remote of type "drive"; name it e.g. "gdrive"
rclone listremotes     # should show "gdrive:"
```
The default remote name is `gdrive`; pass `--remote <name>` if theirs differs. The script preflights this and prints a clear error (with setup hints) if rclone or the remote is missing — surface that to the user rather than failing silently.

### Running the upload

Find the freshly built artifact (glob, newest wins) and upload it:
```bash
# APK (path may vary with flavor casing — glob it)
APK=$(ls -t build/app/outputs/flutter-apk/*-release.apk | head -1)
python3 <skill-dir>/scripts/upload_to_drive.py \
  --file "$APK" --env <flavor> --system android --project <project>

# IPA
IPA=$(ls -t build/ios/ipa/*.ipa | head -1)
python3 <skill-dir>/scripts/upload_to_drive.py \
  --file "$IPA" --env <flavor> --system ios --project <project>
```

Use `--drive-project <NAME>` if the Drive folder name differs from the uppercased code prefix. Preview the destination without uploading with `--dry-run`. After uploading, report the Drive destination path to the user. If a build failed, do not upload.

## Example runs

**"genera el ipa de qa"** → version/build unspecified, IPA only, upload by default:
1. `bump_build_number.py --bump` → say `1.4.2+38`.
2. `flutter build ipa -t lib/main_united_qa.dart --flavor unitedQa --build-name=1.4.2 --build-number=38`
3. On success: `bump_build_number.py --set-version 1.4.2 --set-build 38 --write`.
4. Upload: `upload_to_drive.py --file "$IPA" --env qa --system ios --project united` → `gdrive:Apps/UNITED/QA/iOS/`.

**"saca apk e ipa de prod, versión 2.0.0 build 5"** → both artifacts, explicit version, upload both:
1. `bump_build_number.py --set-version 2.0.0 --set-build 5 --write`
2. `flutter build apk -t lib/main_united_prod.dart --flavor unitedProd --build-name=2.0.0 --build-number=5`
3. `flutter build ipa -t lib/main_united_prod.dart --flavor unitedProd --build-name=2.0.0 --build-number=5`
4. Upload APK → `gdrive:Apps/UNITED/Prod/UNITED Android/`; upload IPA → `gdrive:Apps/UNITED/Prod/UNITED iOS/`.

**"solo el apk de dev, sin subir"** → APK only, no increment, no upload:
1. `flutter build apk -t lib/main_united_dev.dart --flavor unitedDev`
