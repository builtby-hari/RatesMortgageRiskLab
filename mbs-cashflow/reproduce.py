"""Reproduce the README worked example and regenerate docs/figures/ in one run.

    pip install -r requirements-extra.txt
    python3 reproduce.py
"""

import sys

import cli
import plots_mpl

# Same inputs as the README worked example (illustrative numbers).
WORKED_EXAMPLE = ["--market-rate", "7.40", "--yield", "5.5", "--oas"]


def main():
    cli.main(WORKED_EXAMPLE)
    print()
    return plots_mpl.main()


if __name__ == "__main__":
    sys.exit(main())
