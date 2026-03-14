#!/usr/bin/env python3
from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    feature_dir = script_dir / "features"

    feature_files = sorted(feature_dir.glob("story*.feature"))
    if not feature_files:
        print(f"No story feature files found in {feature_dir}", file=sys.stderr)
        return 1

    random.shuffle(feature_files)

    extra_args = sys.argv[1:]

    for feature_file in feature_files:
        command = [
            "behave",
            *extra_args,
            str(feature_file),
            "-D",
            "shuffle=true",
        ]
        print(f"Running: {feature_file}")
        subprocess.run(command, check=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
