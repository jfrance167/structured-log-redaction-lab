"""Frozen utility/leakage oracles and semantic-boundary regressions."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from log_minimizer.admission import LabError
from log_minimizer.core import minimize, project, render
from log_minimizer.evaluation import baseline, evaluate, leaks, load_fixtures
from scripts.make_demo import create


class ProjectionTests(unittest.TestCase):
    def test_demo_inputs_use_frozen_cases_and_preserve_existing_folder(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root = Path(folder) / "fresh"
            create(root)
            self.assertEqual(len(list(root.glob("*.json"))), 5)
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            with self.assertRaises(FileExistsError):
                create(root)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, before)

    def setUp(self):
        self.fixture = load_fixtures()
        self.base = copy.deepcopy(self.fixture["cases"][0]["expected_events"][0])

    def wire(self, events, **extra):
        return json.dumps({"schema_version": 1, "events": events, **extra}).encode()

    def test_all_frozen_cases_against_independent_expectations(self):
        for case in self.fixture["cases"]:
            with self.subTest(case=case["case_id"]):
                try:
                    result = minimize(case["wire"].encode())
                    code = None
                except LabError as error:
                    result, code = {"events": [], "code": error.code}, error.code
                self.assertEqual(result["events"], case["expected_events"])
                self.assertEqual(code, case["expected_code"])
                self.assertFalse(leaks(result, self.fixture["forms"]))
                raw = json.loads(case["wire"])
                masked = baseline(raw, self.fixture["canary"])
                self.assertEqual(leaks(masked, self.fixture["forms"]), case["baseline_leak"])
                self.assertEqual(not case["canary"] and masked != raw, case["baseline_benign_mask"])

    def test_aggregate_denominators_and_no_raw_baseline(self):
        result = evaluate()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["totals"], self.fixture["expected_totals"])
        self.assertEqual(result["minimized_leak_cases"], 0)
        self.assertEqual(result["semantic_rejections"], 4)
        self.assertEqual((result["canary_cases"], result["benign_cases"]), (16, 16))
        self.assertNotIn("events", result)
        self.assertFalse(leaks(result, self.fixture["forms"]))

    def test_fixture_integrity_before_load(self):
        with patch("log_minimizer.evaluation.FIXTURE_SHA256", "changed"):
            with self.assertRaises(LabError) as error:
                load_fixtures()
        self.assertEqual(error.exception.code, "internal.error")

    def test_input_immutable_and_output_has_fresh_context(self):
        value = {"schema_version": 1, "events": [copy.deepcopy(self.base)], "unknown": "invented"}
        value["events"][0]["context"]["unknown"] = ["invented"]
        before = copy.deepcopy(value)
        result = project(value)
        self.assertEqual(value, before)
        result["events"][0]["context"]["elapsed_ms"] = 99
        self.assertEqual(value, before)
        self.assertEqual(result["dropped_fields"], 2)

    def test_unknown_shapes_confusables_and_case_drop(self):
        event = copy.deepcopy(self.base)
        event.update({"Message": "invented", "mеssage": {"nested": ["invented"]}, "unknown": None})
        self.assertEqual(minimize(self.wire([event]))["events"], [self.base])
        event["context"]["Unknown"] = "invented"
        self.assertEqual(minimize(self.wire([event]))["events"], [self.base])

    def test_required_fields_and_closed_value_grammar(self):
        for field in ("event_id", "event_type", "outcome", "severity", "service"):
            for value in (None, True, 1, [], {}, "unknown"):
                event = copy.deepcopy(self.base)
                event[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(LabError):
                    minimize(self.wire([event]))
            event = copy.deepcopy(self.base)
            del event[field]
            with self.assertRaises(LabError):
                minimize(self.wire([event]))
        event = copy.deepcopy(self.base)
        event["event_id"] = "lab-event-１２３４"
        with self.assertRaises(LabError):
            minimize(self.wire([event]))

    def test_version_unique_ids_and_batch_shape(self):
        for raw in (b'{"schema_version":true,"events":[]}', b'{"schema_version":1,"events":null}', b'[]'):
            with self.assertRaises(LabError):
                minimize(raw)
        with self.assertRaises(LabError):
            minimize(self.wire([self.base, self.base]))
        self.assertEqual(minimize(self.wire([]))["events"], [])

    def test_optional_missing_null_and_timing_bounds(self):
        event = copy.deepcopy(self.base)
        del event["context"]
        self.assertNotIn("context", minimize(self.wire([event]))["events"][0])
        for value in (None, True, -1, 60001, "25", [], {}):
            event = copy.deepcopy(self.base)
            event["context"]["elapsed_ms"] = value
            with self.subTest(value=value), self.assertRaises(LabError):
                minimize(self.wire([event]))
        for value in (0, 60000):
            event["context"]["elapsed_ms"] = value
            self.assertEqual(minimize(self.wire([event]))["events"][0]["context"]["elapsed_ms"], value)
        event["context"] = {"unknown": 1}
        self.assertNotIn("context", minimize(self.wire([event]))["events"][0])
        event["context"] = None
        with self.assertRaises(LabError):
            minimize(self.wire([event]))

    def test_render_ascii_and_output_ceiling(self):
        result = minimize(self.wire([self.base]))
        self.assertEqual(json.loads(render(result)), result)
        render(result).encode("ascii")
        with self.assertRaises(LabError) as error:
            render({"too_large": "x" * 65536})
        self.assertEqual(error.exception.code, "output.error")


if __name__ == "__main__":
    unittest.main()
