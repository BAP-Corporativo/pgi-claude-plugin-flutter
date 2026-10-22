#!/usr/bin/env python3
"""
Upload a built APK/IPA to its Google Drive folder using rclone.

Folder layout on Drive:
    <base>/<DRIVE_PROJECT>/<Env>/<system-folder>
where
    Env             = Dev | QA | Prod   (from flavor dev/qa/prod)
    system-folder   = for dev & qa:  "Android" | "iOS"
                      for prod:      "<DRIVE_PROJECT> Android" | "<DRIVE_PROJECT> iOS"

Example (qa iOS):    gdrive:Apps/UNITED/QA/iOS/
Example (prod iOS):  gdrive:Apps/UNITED/Prod/UNITED iOS/

Usage:
    python3 upload_to_drive.py --file <path> --env qa --system ios \
        [--drive-project UNITED] [--remote gdrive] [--base Apps] [--dry-run]

Defaults:
    --remote        gdrive
    --base          Apps
    --drive-project (required unless --project given; then it is <project>.upper())

Exit codes: 0 ok, 1 usage/preflight error, 2 rclone upload failed.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ENV_FOLDER = {"dev": "Dev", "qa": "QA", "prod": "Prod"}
SYSTEM_NAME = {"android": "Android", "ios": "iOS"}


def parse_args():
    p = argparse.ArgumentParser(description="Upload an APK/IPA to Drive via rclone")
    p.add_argument("--file", required=True, help="Path to the .apk/.ipa to upload")
    p.add_argument("--env", required=True, choices=["dev", "qa", "prod"], help="Environment (flavor)")
    p.add_argument("--system", required=True, help="android or ios")
    p.add_argument("--drive-project", dest="drive_project", default=None,
                   help="Drive project folder name (e.g. UNITED)")
    p.add_argument("--project", default=None,
                   help="Code project prefix; drive-project defaults to its uppercase")
    p.add_argument("--remote", default="gdrive", help="rclone remote name (default: gdrive)")
    p.add_argument("--base", default="Apps", help="Base folder on Drive (default: Apps)")
    p.add_argument("--dry-run", action="store_true", help="Print the destination and command, do not upload")
    return p.parse_args()


def resolve_dest(remote, base, drive_project, env, system):
    sys_name = SYSTEM_NAME[system]
    if env == "prod":
        system_folder = f"{drive_project} {sys_name}"
    else:
        system_folder = sys_name
    # rclone path: remote:base/PROJECT/Env/systemfolder
    return f"{remote}:{base}/{drive_project}/{ENV_FOLDER[env]}/{system_folder}"


def main():
    args = parse_args()

    system = args.system.strip().lower()
    if system in ("ios", "iphoneos"):
        system = "ios"
    if system not in SYSTEM_NAME:
        print(f"ERROR=Unknown system '{args.system}', expected android or ios", file=sys.stderr)
        return 1

    drive_project = args.drive_project
    if not drive_project:
        if args.project:
            drive_project = args.project.upper()
        else:
            print("ERROR=Provide --drive-project (or --project to derive it)", file=sys.stderr)
            return 1

    dest = resolve_dest(args.remote, args.base, drive_project, args.env, system)

    file_path = Path(args.file)
    cmd = ["rclone", "copy", str(file_path), dest, "--progress"]

    print(f"DEST={dest}/")
    print(f"CMD={' '.join(cmd)}")

    if args.dry_run:
        print("DRY_RUN=true")
        return 0

    if not file_path.exists():
        print(f"ERROR=File not found: {file_path}", file=sys.stderr)
        return 1

    # Preflight: rclone present and remote configured
    if shutil.which("rclone") is None:
        print("ERROR=rclone is not installed or not on PATH. Install it and run `rclone config`.",
              file=sys.stderr)
        return 1
    try:
        remotes = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR=Could not list rclone remotes: {e.stderr.strip()}", file=sys.stderr)
        return 1
    if f"{args.remote}:" not in remotes.stdout.split():
        print(f"ERROR=rclone remote '{args.remote}:' not found. Configure it with `rclone config` "
              f"(available: {remotes.stdout.strip() or 'none'}).", file=sys.stderr)
        return 1

    # rclone copy creates missing folders in the destination path.
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"ERROR=rclone upload failed (exit {result.returncode})", file=sys.stderr)
        return 2

    print("UPLOADED=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
