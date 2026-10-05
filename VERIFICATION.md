# Verification — October 5, 2026

Windows CPython 3.13.7; exact synthetic-only scope. Latest affected check records:
docs/verification/final-results.json plus full normal-final/optimized-final and
bandit-final logs/JSON. Earlier records retained, not overwritten. Commands use
<PYTHON> for the selected interpreter and <PROJECT> for normalized local paths.

| Phase | Outcome | Evidence |
|---|---|---|
| Stage 1 admission | PASS, nine tests before projection | docs/ADMISSION.md; admission test module |
| Final normal tests | PASS, 31 | python -m unittest discover -v; normal-final.log |
| Final optimized tests | PASS, 31 | python -O -m unittest discover -v; optimized-final.log |
| Frozen evaluation | PASS, 32 independent outcomes | python -m log_minimizer --evaluate; frozen-evaluation.log |
| Bandit 1.9.4 | PASS, zero findings/errors/exclusions | bandit-final.json; initial B110 finding preserved |
| Syntax | PASS, six app/demo files | static-policy.json |
| Local workflow policy | PASS | YAML parsed; exact verified Action pins and checkout credentials false |
| Mutation witness | Detected, original core bytes restored | docs/mutation.json/log |
| Both closed pipes | Exit 120 reproduced, fixed to exit 2 | before-fix JSON + actual subprocess regression |
| Git whitespace/fixture identity | PASS before code commit, final stage rechecked | Receipt/indexed bytes; final STATE |
| Types/lint | NOT RUN | No configured checker established |
| Linux/other runtimes/hosted CI/CodeQL | NOT RUN | No target/runtime/hosted repository execution |

Evaluation: baseline leaks 4/16 canary cases and masks benign data in 1/16 controls.
Minimization leaks zero listed forms in 32 outcomes, retains expected 28 events/
28 failures/700 ms, and rejects four invalid recognized values. No production
accuracy, general privacy or universal encoding metric. Fixed baseline/oracles
and fixture digest were established before application code. Tests include CLI
output/error checks for every case. Mutation logs intentionally contain invented
fixture data; application no-leak claims do not cover developer fixture evidence.

App/helper commands are in README. Reusable minimize(bytes) and frozen demo
helper have usage/assumptions documented; existing shared worker tools reused.
Final normal/optimized tests were rerun after the dual-sink correction; no
unaffected suite repetition after documentation-only work.

Prepared security baseline: immutable-pin Python tests/Bandit, CodeQL main
push/PR + weekly/manual, Dependabot, SECURITY.md. Pins reuse exact previously
verified release commits from this session. Hosted feature eligibility,
protections, secret scanning/push protection and code-scanning alerts cannot be
assessed without a separately authorized hosted repository. Dev Bandit directly
pinned; no transitive artifact-hash lock. No dependency installation or billing.
