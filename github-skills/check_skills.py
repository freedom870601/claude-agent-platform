#!/usr/bin/env python3
"""CLI: validate all skill files in skills/. Exits non-zero on any errors."""

import sys
from pathlib import Path
from validator import validate_skill

SKILLS_DIR = Path(__file__).parent / "skills"


def main() -> int:
    skill_files = sorted(SKILLS_DIR.glob("*.md"))
    if not skill_files:
        print("No skill files found in skills/", file=sys.stderr)
        return 1

    failed = False
    for path in skill_files:
        errors = validate_skill(path)
        if errors:
            print(f"FAIL {path.name}:")
            for err in errors:
                print(f"  - {err}")
            failed = True
        else:
            print(f"OK   {path.name}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
