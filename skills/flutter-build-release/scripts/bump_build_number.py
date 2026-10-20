#!/usr/bin/env python3
"""
Read, compute, and (optionally) write the Flutter app version stored in
pubspec.yaml (`version: X.Y.Z+B`, where B is the build number).

Typical release flow (so a failed build never burns a build number):

  1) Compute the target WITHOUT writing:
        python bump_build_number.py --bump
     -> prints CURRENT / TARGET / BUILD_NAME / BUILD_NUMBER

  2) Build the IPA/APK using BUILD_NAME and BUILD_NUMBER as flags.

  3) Only on a successful build, persist it:
        python bump_build_number.py --set-version 1.0.0 --set-build 6 --write

Options:
  --pubspec PATH     Path to pubspec.yaml (default: ./pubspec.yaml)
  --bump             Target build number = current + 1
  --set-version X.Y.Z  Target version name (defaults to current)
  --set-build N      Target build number (overrides --bump)
  --write            Persist the computed target back to pubspec.yaml
  (no flags)         Just read and print the current version

Output is line-based KEY=VALUE so it is easy to parse:
  CURRENT=1.0.0+5
  TARGET=1.0.0+6
  BUILD_NAME=1.0.0
  BUILD_NUMBER=6
  WROTE=false
"""

import argparse
import re
import sys
from pathlib import Path

# Matches the pubspec version line. Build number (+B) is optional.
VERSION_RE = re.compile(
    r'^(?P<prefix>version:\s*)'
    r'(?P<name>\d+\.\d+\.\d+)'
    r'(?:\+(?P<build>\d+))?'
    r'(?P<trailing>[^\S\n]*)$',
    re.MULTILINE,
)


def parse_args():
    p = argparse.ArgumentParser(description="Read/bump the Flutter build number in pubspec.yaml")
    p.add_argument("--pubspec", default="pubspec.yaml", help="Path to pubspec.yaml")
    p.add_argument("--bump", action="store_true", help="Target build = current + 1")
    p.add_argument("--set-version", dest="set_version", default=None, help="Target version name X.Y.Z")
    p.add_argument("--set-build", dest="set_build", type=int, default=None, help="Target build number")
    p.add_argument("--write", action="store_true", help="Persist the target back to pubspec.yaml")
    return p.parse_args()


def main():
    args = parse_args()
    path = Path(args.pubspec)

    if not path.exists():
        print(f"ERROR=pubspec.yaml not found at {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    if not m:
        print("ERROR=Could not find a 'version: X.Y.Z(+B)' line in pubspec.yaml", file=sys.stderr)
        return 1

    cur_name = m.group("name")
    cur_build = int(m.group("build")) if m.group("build") else 0

    # Resolve target
    tgt_name = args.set_version or cur_name
    if args.set_build is not None:
        tgt_build = args.set_build
    elif args.bump:
        tgt_build = cur_build + 1
    else:
        tgt_build = cur_build

    if not re.fullmatch(r'\d+\.\d+\.\d+', tgt_name):
        print(f"ERROR=Invalid version name '{tgt_name}', expected X.Y.Z", file=sys.stderr)
        return 1
    if tgt_build < 0:
        print(f"ERROR=Build number must be >= 0, got {tgt_build}", file=sys.stderr)
        return 1

    wrote = False
    if args.write:
        def _repl(match):
            return f"{match.group('prefix')}{tgt_name}+{tgt_build}{match.group('trailing')}"
        new_text = VERSION_RE.sub(_repl, text, count=1)
        path.write_text(new_text, encoding="utf-8")
        wrote = True

    print(f"CURRENT={cur_name}+{cur_build}")
    print(f"TARGET={tgt_name}+{tgt_build}")
    print(f"BUILD_NAME={tgt_name}")
    print(f"BUILD_NUMBER={tgt_build}")
    print(f"WROTE={'true' if wrote else 'false'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
