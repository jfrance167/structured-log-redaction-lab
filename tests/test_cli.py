"""Assert no canary in stdout/stderr across semantic, internal and I/O errors."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from log_minimizer.__main__ import emit, error_channel, main
from log_minimizer.admission import LabError
from log_minimizer.evaluation import leaks, load_fixtures


class CliTests(unittest.TestCase):
    def setUp(self):
        self.fixture = load_fixtures()
        self.canary = self.fixture["canary"]

    def invoke(self, args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(args)
        self.assertFalse(leaks({"stdout": out.getvalue(), "stderr": err.getvalue()}, self.fixture["forms"]))
        return code, out.getvalue(), err.getvalue()

    def test_argv_errors_never_echo_argument(self):
        for args in ([], ["--" + self.canary], ["--evaluate", self.canary]):
            code, out, err = self.invoke(args)
            self.assertEqual((code, out), (2, ""))
            self.assertEqual(json.loads(err)["code"], "arguments.invalid")

    def test_os_and_internal_errors_never_echo_paths_or_exception(self):
        for error, expected in ((OSError(self.canary), "input.io"), (RuntimeError(self.canary), "internal.error")):
            with patch("log_minimizer.__main__.read_input", side_effect=error):
                code, out, err = self.invoke([self.canary])
            self.assertEqual((code, out), (2, ""))
            self.assertEqual(json.loads(err)["code"], expected)

    def test_full_frozen_suite_through_cli_channels(self):
        for case in self.fixture["cases"]:
            with self.subTest(case=case["case_id"]), patch("log_minimizer.__main__.read_input",
                                                         return_value=case["wire"].encode()):
                code, out, err = self.invoke(["synthetic.json"])
                if case["expected_code"]:
                    self.assertEqual((code, out), (2, ""))
                    self.assertEqual(json.loads(err)["code"], case["expected_code"])
                else:
                    self.assertEqual((code, err), (0, ""))
                    self.assertEqual(json.loads(out)["events"], case["expected_events"])

    def test_semantic_batch_failure_emits_no_first_valid_event(self):
        first = json.loads(self.fixture["cases"][0]["wire"])["events"][0]
        raw = json.dumps({"schema_version": 1, "events": [first, {"message": self.canary}]}).encode()
        with patch("log_minimizer.__main__.read_input", return_value=raw):
            code, out, err = self.invoke(["synthetic.json"])
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(json.loads(err)["code"], "schema.invalid")

    def test_invalid_parse_and_surrogate_error_channels(self):
        for raw in (self.canary.encode(), b'{"unknown":"\\ud800"}', b'{"x":0,"x":1}'):
            with patch("log_minimizer.__main__.read_input", return_value=raw):
                code, out, err = self.invoke(["synthetic.json"])
            self.assertEqual((code, out), (2, ""))
            self.assertEqual(json.loads(err)["status"], "error")

    def test_short_and_failed_writes_fail_without_raw_fallback(self):
        for returned in (None, True, 0, 2):
            stream = Mock()
            stream.write.return_value = returned
            with self.assertRaises(LabError) as caught:
                emit("minimized-only", stream)
            self.assertEqual(caught.exception.code, "output.error")
        for operation in ("write", "flush"):
            stream = Mock()
            stream.write.return_value = 14
            getattr(stream, operation).side_effect = BrokenPipeError(self.canary)
            with self.assertRaises(LabError) as caught:
                emit("minimized-only", stream)
            self.assertEqual(caught.exception.code, "output.error")

    def test_main_output_failure_and_failing_error_sink(self):
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err), \
             patch("sys.stdout.write", side_effect=BrokenPipeError(self.canary)):
            self.assertEqual(main(["--evaluate"]), 2)
        self.assertEqual(json.loads(err.getvalue())["code"], "output.error")
        self.assertFalse(leaks(err.getvalue(), self.fixture["forms"]))
        with redirect_stderr(io.StringIO()), patch("sys.stderr.write", side_effect=OSError(self.canary)):
            self.assertEqual(main(["--" + self.canary]), 2)

    def test_error_sink_short_write_does_not_report_delivery(self):
        for returned in (None, True, 0, 2):
            with redirect_stderr(io.StringIO()), patch("sys.stderr.write", return_value=returned):
                self.assertFalse(error_channel("input.io"))

    def test_both_closed_pipes_preserve_failure_exit(self):
        root = Path(__file__).resolve().parents[1]
        with subprocess.Popen([sys.executable, "-m", "log_minimizer", "--evaluate"], cwd=root,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as child:
            child.stdout.close()
            child.stdout = None
            child.stderr.close()
            child.stderr = None
            try:
                child.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.communicate()
                self.fail("CLI timeout")
        self.assertEqual(child.returncode, 2)

    def test_actual_file_and_size_directory_failure(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / "synthetic.json"
            path.write_text(self.fixture["cases"][0]["wire"])
            self.assertEqual(self.invoke([str(path)])[0], 0)
            path.write_bytes(b" " * 65537)
            self.assertEqual(self.invoke([str(path)])[0], 2)
            self.assertEqual(self.invoke([folder])[0], 2)

    def test_optimized_child_and_closed_pipe(self):
        root = Path(__file__).resolve().parents[1]
        child = subprocess.run([sys.executable, "-O", "-m", "log_minimizer", "--evaluate"], cwd=root,
                               capture_output=True, timeout=10, check=False)
        self.assertEqual(child.returncode, 0)
        self.assertEqual(json.loads(child.stdout)["status"], "pass")
        with subprocess.Popen([sys.executable, "-m", "log_minimizer", "--evaluate"], cwd=root,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as child:
            child.stdout.close()
            child.stdout = None
            try:
                _, errors = child.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.communicate()
                self.fail("CLI timeout")
        self.assertEqual(child.returncode, 2)
        self.assertEqual(json.loads(errors)["code"], "output.error")
        self.assertNotIn(b"Traceback", errors)
        self.assertNotIn(b"Exception ignored", errors)


if __name__ == "__main__":
    unittest.main()
