"""Run every component's test suite from the repo root.

Each component keeps its own imports relative to its own folder, so the
tests run with that folder as the working directory.
"""
import subprocess
import sys
from pathlib import Path

COMPONENTS = ["market-dashboard", "delinquency-drivers", "mbs-cashflow", "rate-shock"]


def main() -> int:
    root = Path(__file__).resolve().parent
    failed = []
    for name in COMPONENTS:
        print(f"== {name}", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-q"], cwd=root / name
        )
        if result.returncode != 0:
            failed.append(name)
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1
    print(f"All {len(COMPONENTS)} components passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
