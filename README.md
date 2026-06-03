# Veriqa

**Catch silently-wrong quantum circuits.**

Quantum programs output *probability distributions*, not values — so you can't
write `assert result == expected`. A circuit can run, return perfectly normal
counts, and still be wrong: a misplaced gate, a transpiler that rewrote your
circuit, hardware that drifted overnight. Veriqa gives you assertions,
statistical checks, and regression tests that catch those silent failures —
and they drop straight into the `pytest` you already use.

```bash
pip install veriqa
```

> Status: **v0.1 (alpha).** Qiskit + Aer simulator. Multi-framework backends
> (PennyLane, Cirq) and real-hardware monitoring are on the [roadmap](ROADMAP.md).

## Quick start

```python
from qiskit import QuantumCircuit
import veriqa as vq

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)                       # a Bell state

# 1. Does it produce the right distribution? (shot-noise aware)
vq.assert_distribution_close(qc, {"00": 0.5, "11": 0.5})

# 2. Did an "optimised" rewrite change behaviour? (regression test)
vq.assert_circuits_equivalent(qc, my_optimised_qc)
```

Failures raise `QuantumAssertionError` (a subclass of `AssertionError`), so they
show up in pytest exactly like any other failed assertion.

## The five checks in v0.1

| Function | What it verifies | How |
|---|---|---|
| `assert_distribution_close` | output distribution matches expected | chi-squared goodness-of-fit (shot-noise aware) or TVD threshold |
| `assert_state_equal` | circuit prepares a target statevector | fidelity, up to global phase |
| `assert_unitary_equal` | circuit implements an intended operation | full-unitary overlap, up to global phase |
| `assert_circuits_equivalent` | two circuits do the same thing | unitary equivalence — the regression workhorse |
| `assert_deterministic` | circuit collapses to one outcome | for oracles / reversible logic |

Every check returns an `AssertionResult` carrying numeric `metrics`
(p-values, distances, fidelities), so reporters and dashboards can trend them.

## Why it works: a circuit that *looks* fine but isn't

`examples/mutation_demo.py` builds a correct 3-qubit GHZ state, then deletes a
single `CX` (a classic mutation-testing bug). A naive eyeball check passes the
broken circuit. Veriqa catches it:

```
MUTANT circuit (one CX silently deleted)
  naive_check(mutant): P('000') = 0.505 -> PASS (looks fine)
  veriqa.assert_distribution_close(mutant): [FAIL] output distribution differs (p_value=0.0, tvd=0.5)
  veriqa.assert_circuits_equivalent(correct, mutant): [FAIL] circuits are NOT equivalent
```

The bug lives in the *correlations*, not the marginal you happened to look at.
That gap is exactly what Veriqa exists to close.

## Configuration

```python
import veriqa as vq
vq.configure(shots=8192, seed=42, alpha=0.05)   # set once per session
```

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

## License

MIT © 2026 Shubham Tripathi
