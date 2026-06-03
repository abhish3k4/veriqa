# Roadmap — adding functionality step by step

The whole point of the architecture is that **each new feature has exactly one
obvious place to go**, and adding it doesn't force you to touch anything else.
Here's the map. Ship one row at a time.

## How the pieces fit (so you know where things plug in)

```
veriqa/
├── core/         result.py (AssertionResult), config.py     <- shared contracts
├── stats/        distances.py, tests.py                      <- pure math, no quantum
├── backends/     base.py (Backend ABC) + qiskit_aer.py       <- execution targets
├── assertions/   one file per check, registered in __init__  <- the user-facing checks
└── examples/     demos
```

Two golden rules:
1. **Every assertion returns an `AssertionResult`.** Never return a bare bool.
   That's why a future dashboard/monitor only has to understand one shape.
2. **Anything that executes a circuit goes through a `Backend`.** Never call a
   simulator directly inside an assertion.

## Phase 1 — v0.1 (DONE)
Five assertions on Qiskit + Aer, statistical distribution check, regression
(equivalence) check, pytest-native failures, mutation demo. **This is what you launch.**

## Phase 2 — make it delightful to adopt (week 2–4)
- **A real pytest plugin** → new file `pytest_plugin.py` + a `[project.entry-points.pytest11]`
  line in `pyproject.toml`. Gives nicer reporting and fixtures. Nothing else changes.
- **More statistical tests** (G-test, exact multinomial for low shots) → add a
  function to `stats/tests.py` with the same `GofResult` contract; expose via the
  `method=` kwarg on `assert_distribution_close`.
- **Noise-aware tolerance** → a config knob in `core/config.py`.

## Phase 3 — multi-framework (the moat; month 2)
Every competitor is Qiskit-only. Break out by adding backends:
- `backends/pennylane.py` → subclass `Backend`, implement `run_counts` /
  `statevector` / `unitary`, then one line in `backends/__init__._REGISTRY`.
- `backends/cirq.py` → same recipe.
- Accept those frameworks' circuit objects in `assertions/_convert.py`.
Result: `vq.assert_distribution_close(my_pennylane_qnode, ...)` just works.

## Phase 4 — real hardware (month 2–3)
- `backends/ibm.py`, `backends/braket.py` → implement `run_counts`; override
  `supports_statevector()`/`supports_unitary()` to return `False` so state/unitary
  assertions raise a clean error instead of lying.
- Add cost/shot guards in `core/config.py` so a test run can't accidentally burn
  paid QPU credits.

## Phase 5 — the testing methods that need a home of their own (month 3–4)
These become new top-level subpackages (they're engines, not single asserts):
- `veriqa/mutation/` → gate add/remove/replace operators + a runner that scores a
  user's test suite (the "mutation score" you demo to customers). Reuses the
  `delete_gate` idea from `examples/mutation_demo.py`.
- `veriqa/property/` → input generators + invariants (reversibility, commutation,
  algebraic relations) for property-based testing.
- `veriqa/tomography/` → state/process tomography assertions for richer checks.

## Phase 6 — the observability half (the recurring-revenue product; month 4+)
This is a **separate service**, not part of the pip library — keep it decoupled.
- A small `veriqa-server` (FastAPI + Postgres + a time-series store) that ingests
  `AssertionResult.metrics` over time.
- Because every result already carries `metrics`, the library side needs almost no
  change — just an optional reporter that POSTs results to the server.
- Dashboard (React) trending fidelity/TVD per circuit per backend, with drift alerts.
- This is what hardware vendors and enterprise teams pay for.

## Phase 7 — CI integration (parallel, anytime)
- `.github/workflows/` example + a GitHub Action so quantum tests run on every commit
  and post regressions back to the dashboard.

---

**Sequencing advice:** Phases 1–2 get you launched and adopted. Phase 3 is your
differentiation. Don't start Phase 6 (the SaaS) until you have design partners
asking for it — that's the moment it becomes a company, and the moment a grant
(QC LEAP Slab A) is worth chasing to fund the build.
