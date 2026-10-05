"""Create frozen invented demo inputs in a fresh directory, never overwrite.

Usage: python scripts/make_demo.py FRESH_DIRECTORY
This writes input fixtures, not minimized output; never use real data.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from log_minimizer.evaluation import load_fixtures


def create(folder: Path):
    """Exclusive directory/files; a later write failure can leave partial fixtures."""
    fixture = load_fixtures()
    wanted = {"password-canary", "base64-canary", "key-canary", "service-canary", "password-benign"}
    folder.mkdir(parents=True, exist_ok=False)
    for case in fixture["cases"]:
        if case["case_id"] in wanted:
            with (folder / (case["case_id"] + ".json")).open("xb") as stream:
                stream.write(case["wire"].encode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("demo.arguments.invalid")
    try:
        create(Path(sys.argv[1]))
    except Exception:
        raise SystemExit("demo.error") from None
