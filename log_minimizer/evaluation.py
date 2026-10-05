"""Exact frozen synthetic comparison; never emit baseline events or canaries."""

import hashlib
import json
from pathlib import Path

from .admission import LabError, MAX_BYTES
from .core import minimize


FIXTURE_SHA256 = "c2c9fc5d84f53e5e491ab69e420c866088766c2bea1eddda5f41488faba70d0e"
MASK_KEYS = frozenset({"password", "token", "api_key"})
MASK = "[MASKED]"


def load_fixtures():
    """Read only the compiled-in fixture path, verifying bytes before parsing."""
    path = Path(__file__).resolve().parents[1] / "fixtures" / "cases.json"
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise LabError("internal.error")
    return json.loads(raw)


def baseline(value, canary):
    """Frozen JSON-only baseline, not a production filter or privacy boundary."""
    if type(value) is dict:
        return {key: MASK if key in MASK_KEYS else baseline(item, canary) for key, item in value.items()}
    if type(value) is list:
        return [baseline(item, canary) for item in value]
    if type(value) is str:
        return value.replace(canary, MASK)
    return value


def leaks(value, forms):
    """Finite fixture oracle; checks decoded strings/keys and serialized output."""
    if any(form in json.dumps(value, ensure_ascii=True) for form in forms):
        return True
    pending = [value]
    while pending:
        node = pending.pop()
        if type(node) is dict:
            pending.extend(node.keys())
            pending.extend(node.values())
        elif type(node) is list:
            pending.extend(node)
        elif type(node) is str and any(form in node for form in forms):
            return True
    return False


def evaluate() -> dict:
    """Return aggregate observations; compare independent preregistered oracles."""
    fixture = load_fixtures()
    totals = {"cases": 0, "projected_events": 0, "failures": 0, "elapsed_ms": 0,
              "baseline_canary_leaks": 0, "baseline_benign_masks": 0}
    mismatches = minimized_leaks = rejections = 0
    for case in fixture["cases"]:
        totals["cases"] += 1
        try:
            result = minimize(case["wire"].encode("utf-8"))
            events, code = result["events"], None
        except LabError as error:
            result, events, code = {"status": "error", "code": error.code}, [], error.code
            rejections += 1
        mismatches += int(events != case["expected_events"] or code != case["expected_code"])
        minimized_leaks += int(leaks(result, fixture["forms"]))
        totals["projected_events"] += len(events)
        totals["failures"] += sum(event["outcome"] == "failure" for event in events)
        totals["elapsed_ms"] += sum(event.get("context", {}).get("elapsed_ms", 0) for event in events)
        original = json.loads(case["wire"])
        masked = baseline(original, fixture["canary"])
        leaked = leaks(masked, fixture["forms"])
        benign_masked = not case["canary"] and masked != original
        totals["baseline_canary_leaks"] += int(case["canary"] and leaked)
        totals["baseline_benign_masks"] += int(benign_masked)
        mismatches += int(leaked != case["baseline_leak"] or benign_masked != case["baseline_benign_mask"])
    matches = totals == fixture["expected_totals"] and mismatches == 0 and minimized_leaks == 0
    return {"status": "pass" if matches else "fail", "evaluation": "frozen-synthetic-v1",
            "totals": totals, "semantic_rejections": rejections, "minimized_leak_cases": minimized_leaks,
            "oracle_mismatches": mismatches, "canary_cases": 16, "benign_cases": 16,
            "notice": "Finite synthetic observations, not universal privacy or production detector accuracy."}
