"""assert_deterministic - a simple property check.

Many circuits (oracles, reversible/classical-logic circuits, fully-resolved
computations) should produce a single outcome with probability ~1. This catches
the case where such a circuit leaks probability mass into other states.

This module is also the template for future property-based checks
(unitarity, idempotence, commutation relations, custom invariants): each is a
function that builds an AssertionResult.
"""

from __future__ import annotations

from typing import Optional, Union

from qiskit import QuantumCircuit

from ..backends import Backend, get_backend
from ..core.config import config
from ..core.result import AssertionResult


def assert_deterministic(
    circuit: QuantumCircuit,
    expected_outcome: Optional[str] = None,
    *,
    shots: Optional[int] = None,
    min_probability: float = 0.99,
    backend: Optional[Union[str, Backend]] = None,
    raises: bool = True,
) -> AssertionResult:
    """Assert the circuit concentrates on one outcome.

    If ``expected_outcome`` is given, that specific bitstring must dominate;
    otherwise any single outcome dominating with probability >= ``min_probability``
    passes.
    """
    bk = get_backend(backend)
    shots = shots or config.shots
    counts = bk.run_counts(circuit, shots)
    total = sum(counts.values())

    top_outcome, top_count = max(counts.items(), key=lambda kv: kv[1])
    top_outcome = top_outcome.replace(" ", "")
    top_prob = top_count / total

    if expected_outcome is not None:
        target = expected_outcome.replace(" ", "")
        target_prob = counts.get(expected_outcome, counts.get(target, 0)) / total
        passed = target_prob >= min_probability
        msg = (
            f"outcome {target!r} dominates (p={target_prob:.3f})"
            if passed
            else f"outcome {target!r} only p={target_prob:.3f} (< {min_probability})"
        )
        metrics = {"target_prob": round(target_prob, 4), "shots": shots}
    else:
        passed = top_prob >= min_probability
        msg = (
            f"deterministic on {top_outcome!r} (p={top_prob:.3f})"
            if passed
            else f"not deterministic; top outcome {top_outcome!r} p={top_prob:.3f}"
        )
        metrics = {"top_outcome": top_outcome, "top_prob": round(top_prob, 4), "shots": shots}

    result = AssertionResult(passed=passed, check="deterministic", message=msg, metrics=metrics)
    return result.raise_if_failed() if raises else result
