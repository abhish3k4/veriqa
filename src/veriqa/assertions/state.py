"""assert_state_equal - exact (noise-free) statevector check, up to global phase.

Global phase is physically unobservable, so we compare via fidelity |<a|b>|^2
rather than elementwise equality. Requires a simulator backend that can produce
a statevector (real hardware cannot).
"""

from __future__ import annotations

from typing import Optional, Union

from qiskit import QuantumCircuit

from ..backends import Backend, get_backend
from ..core.config import config
from ..core.result import AssertionResult
from ..exceptions import BackendError
from ..stats.distances import state_fidelity
from ._convert import ExpectedState, to_statevector


def assert_state_equal(
    circuit: QuantumCircuit,
    expected: ExpectedState,
    *,
    atol: Optional[float] = None,
    backend: Optional[Union[str, Backend]] = None,
    raises: bool = True,
) -> AssertionResult:
    """Assert the circuit prepares ``expected`` (up to global phase)."""
    bk = get_backend(backend)
    if not bk.supports_statevector():
        raise BackendError(
            f"Backend {bk.name!r} cannot produce a statevector; "
            "use a simulator backend for assert_state_equal."
        )
    atol = config.atol if atol is None else atol

    actual = bk.statevector(circuit)
    target = to_statevector(expected)
    fidelity = state_fidelity(actual, target)
    passed = fidelity >= 1.0 - atol

    msg = (
        "statevector matches expected (up to global phase)"
        if passed
        else "statevector differs from expected"
    )
    result = AssertionResult(
        passed=passed,
        check="state_equal",
        message=msg,
        metrics={"fidelity": round(fidelity, 8), "atol": atol},
    )
    return result.raise_if_failed() if raises else result
