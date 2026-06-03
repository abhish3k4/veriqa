"""Unitary-level checks: the regression-testing workhorses.

``assert_unitary_equal``      - circuit implements an intended operation.
``assert_circuits_equivalent``- two circuits do the same thing (up to global
                                phase). This is how you catch a refactor,
                                optimisation, or transpilation that silently
                                changed behaviour.

Both compare full unitaries, so they are exact and noise-free but limited to
modest qubit counts (a unitary is 2^n x 2^n).
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from ..core.config import config
from ..core.result import AssertionResult
from ._convert import ExpectedUnitary, to_unitary


def _equiv_up_to_phase(u: np.ndarray, v: np.ndarray, atol: float) -> float:
    """Return normalised |Tr(U^dag V)| / dim in [0, 1]; 1.0 means equal up to phase."""
    if u.shape != v.shape:
        raise ValueError(f"Unitary dim mismatch: {u.shape} vs {v.shape}")
    dim = u.shape[0]
    overlap = np.abs(np.trace(u.conj().T @ v)) / dim
    return float(overlap)


def assert_unitary_equal(
    circuit: QuantumCircuit,
    expected: ExpectedUnitary,
    *,
    atol: Optional[float] = None,
    raises: bool = True,
) -> AssertionResult:
    """Assert the circuit's unitary equals ``expected`` (up to global phase)."""
    atol = config.atol if atol is None else atol
    actual = to_unitary(circuit)
    target = to_unitary(expected)
    overlap = _equiv_up_to_phase(actual, target, atol)
    passed = overlap >= 1.0 - atol
    msg = (
        "unitary matches expected (up to global phase)"
        if passed
        else "unitary differs from expected"
    )
    result = AssertionResult(
        passed=passed,
        check="unitary_equal",
        message=msg,
        metrics={"process_overlap": round(overlap, 8), "atol": atol},
    )
    return result.raise_if_failed() if raises else result


def assert_circuits_equivalent(
    circuit_a: QuantumCircuit,
    circuit_b: QuantumCircuit,
    *,
    atol: Optional[float] = None,
    raises: bool = True,
) -> AssertionResult:
    """Assert two circuits implement the same unitary (up to global phase)."""
    atol = config.atol if atol is None else atol
    # Operator.equiv handles global phase and dimension checks cleanly.
    a = Operator(circuit_a.remove_final_measurements(inplace=False))
    b = Operator(circuit_b.remove_final_measurements(inplace=False))
    passed = bool(a.equiv(b, atol=atol))
    overlap = _equiv_up_to_phase(np.asarray(a.data), np.asarray(b.data), atol)
    msg = (
        "circuits are equivalent (up to global phase)"
        if passed
        else "circuits are NOT equivalent"
    )
    result = AssertionResult(
        passed=passed,
        check="circuits_equivalent",
        message=msg,
        metrics={"process_overlap": round(overlap, 8), "atol": atol},
    )
    return result.raise_if_failed() if raises else result
