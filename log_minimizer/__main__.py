"""Local synthetic CLI with closed error channels, including argument errors."""

import argparse
import json
import os
from pathlib import Path
import stat
import sys

from .admission import CODES, LabError, MAX_BYTES
from .core import minimize, render
from .evaluation import evaluate


class Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise LabError("arguments.invalid")


def read_input(path):
    """Bound stable regular files; cannot isolate open-time races/blocking I/O."""
    if not stat.S_ISREG(path.stat().st_mode):
        raise LabError("input.io")
    with path.open("rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise LabError("input.io")
        if info.st_size > MAX_BYTES:
            raise LabError("input.limit")
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise LabError("input.limit")
    return raw


def emit(output, stream):
    """A later short/failed write is nontransactional; never claim success."""
    failed = False
    try:
        written = stream.write(output)
        if type(written) is not int or written != len(output):
            raise LabError("output.error")
        stream.flush()
    except (OSError, ValueError):
        failed = True
    if failed:
        raise LabError("output.error")


def error_channel(code):
    """Never reflect exception text or fall back to raw data if stderr fails."""
    if type(code) is not str or code not in CODES:
        code = "internal.error"
    try:
        message = json.dumps({"status": "error", "code": code}) + "\n"
        written = sys.stderr.write(message)
        if type(written) is not int or written != len(message):
            return False
        sys.stderr.flush()
    except Exception:
        # Already returning failure; a failed error sink has no raw fallback.
        return False
    return True


def main(argv=None) -> int:
    """Exit 0 minimized/evaluation pass; 1 evaluation mismatch; 2 fixed error."""
    try:
        cli = Parser(prog="log-minimizer", description="Minimize synthetic structured events before a local sink")
        cli.add_argument("file", nargs="?", type=Path)
        cli.add_argument("--evaluate", action="store_true", help="Run the frozen invented-canary comparison")
        args = cli.parse_args(argv)
        if args.evaluate == (args.file is not None):
            raise LabError("arguments.invalid")
        result = evaluate() if args.evaluate else minimize(read_input(args.file))
        emit(render(result), sys.stdout)
        return 1 if args.evaluate and result["status"] != "pass" else 0
    except LabError as error:
        error_channel(error.code)
    except OSError:
        error_channel("input.io")
    except Exception:
        # Even programming errors must not leak a raw exception via this CLI.
        # Fixed internal.error makes failure visible without a traceback.
        error_channel("internal.error")
    return 2


if __name__ == "__main__":
    status = main()
    if status == 2:
        for name in ("stdout", "stderr"):
            try:
                getattr(sys, name).flush()
            except Exception:
                # A dirty failed buffer changes exit 2 to 120 at shutdown.
                # Both channels can fail; never retry or print raw errors.
                setattr(sys, name, None)
    raise SystemExit(status)
